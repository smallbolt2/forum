"""
Nuxt/Nitro 兼容的 Topic API

映射自 server/api/topic/*
"""

from datetime import datetime
from collections import defaultdict

from sqlalchemy import func

from flask import Blueprint, request, jsonify

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.user import User
from app.models.prisma_topic_extras import (
  TopicTag,
  TopicSection,
  TopicSectionRelation,
  TopicLike,
  TopicDislike,
  TopicFavorite,
  TopicUpvote,
  TopicReplyLike,
  TopicReplyDislike,
  TopicReplyTarget
)
from app.utils.auth import token_required
from app.utils.response import error
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie
from app.utils.markdown_render import markdown_to_html


kun_topic_bp = Blueprint('kun_topic', __name__)


def _get_nsfw_mode():
  # Nuxt 里用 getNSFWCookie(event) 返回 'sfw' 等，这里简单兼容
  return request.cookies.get('nsfw') or request.cookies.get('kun-nsfw') or ''


def _topic_card(topic: Topic):
  raise NotImplementedError()


def _topic_detail(topic: Topic, uid=None):
  nsfw = _get_nsfw_mode()
  if (nsfw == 'sfw' and topic.is_nsfw) or topic.status == 1:
    return 'banned'

  # will be filled in get_topic_detail()
  raise NotImplementedError()

  return {
    'id': topic.id,
    'title': topic.title,
    'view': topic.view or 0,
    'status': topic.status,
    'isNSFW': bool(topic.is_nsfw),
    'category': category_info.get('name') or '',
    'section': sections,
    'tag': tags,
    'user': user,

    'likeCount': 0,
    'isLiked': False,
    'dislikeCount': 0,
    'isDisliked': False,
    'favoriteCount': 0,
    'isFavorited': False,
    'upvoteCount': 0,
    'isUpvoted': False,

    'replyCount': reply_count,
    'bestAnswer': None,

    # Nuxt 会返回 html + markdown，这里先返回 markdown 原文，html 留空（后续可接 markdown 渲染）
    'contentHtml': '',
    'contentMarkdown': topic.content,
    'statusUpdateTime': topic.status_update_time.isoformat() if topic.status_update_time else None,
    'upvoteTime': topic.upvote_time.isoformat() if topic.upvote_time else None,
    'edited': topic.edited.isoformat() if topic.edited else None,
    'created': topic.created.isoformat() if topic.created else None
  }


@kun_topic_bp.route('', methods=['GET'])
def list_topics():
  """
  GET /api/topic
  """
  try:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort_field = request.args.get('sortField', 'created', type=str)
    sort_order = request.args.get('sortOrder', 'desc', type=str)
    category = request.args.get('category', 'all', type=str)

    query = Topic.query

    # Nuxt 原版：category 精确匹配
    if category and category != 'all':
      query = query.filter(Topic.category == category)

    # Nuxt: status { not: 1 } 且过滤某些 section，这里只过滤已删除
    query = query.filter(Topic.status != 2)

    # NSFW
    if _get_nsfw_mode() == 'sfw':
      query = query.filter(Topic.is_nsfw == False)  # noqa: E712

    # order by
    order_attr = getattr(Topic, sort_field, Topic.created)
    if sort_order == 'asc':
      query = query.order_by(order_attr.asc())
    else:
      query = query.order_by(order_attr.desc())

    pagination = query.paginate(page=page, per_page=limit, error_out=False)
    rows = pagination.items

    topic_ids = [t.id for t in rows]

    # batch tags
    tags_by_topic = defaultdict(list)
    if topic_ids:
      for tt in TopicTag.query.filter(TopicTag.topic_id.in_(topic_ids)).all():
        tags_by_topic[tt.topic_id].append(tt.tag)

    # batch sections
    sections_by_topic = defaultdict(list)
    if topic_ids:
      rels = TopicSectionRelation.query.filter(
        TopicSectionRelation.topic_id.in_(topic_ids)
      ).all()
      section_ids = list({r.topic_section_id for r in rels})
      section_map = {}
      if section_ids:
        for s in TopicSection.query.filter(TopicSection.id.in_(section_ids)).all():
          section_map[s.id] = s.name
      for r in rels:
        name = section_map.get(r.topic_section_id)
        if name:
          sections_by_topic[r.topic_id].append(name)

    # batch counts
    like_counts = {tid: c for tid, c in db.session.query(
      TopicLike.topic_id, func.count(TopicLike.id)
    ).filter(TopicLike.topic_id.in_(topic_ids)).group_by(TopicLike.topic_id).all()} if topic_ids else {}

    reply_counts = {tid: c for tid, c in db.session.query(
      TopicReply.topic_id, func.count(TopicReply.id)
    ).filter(TopicReply.topic_id.in_(topic_ids)).group_by(TopicReply.topic_id).all()} if topic_ids else {}

    comment_counts = {}  # expensive; omit for now

    # batch users
    user_ids = list({t.user_id for t in rows})
    users_map = {}
    if user_ids:
      for u in User.query.filter(User.id.in_(user_ids)).all():
        users_map[u.id] = u

    topics = []
    for t in rows:
      u = users_map.get(t.user_id)
      topics.append({
        'id': t.id,
        'title': t.title,
        'view': t.view or 0,
        'tag': tags_by_topic.get(t.id, []),
        'user': {
          'id': t.user_id,
          'name': u.name if u else '',
          'avatar': u.avatar if u else ''
        },
        'status': t.status,
        'hasBestAnswer': bool(t.best_answer_id),
        'isNSFWTopic': bool(t.is_nsfw),
        'likeCount': like_counts.get(t.id, 0),
        'replyCount': reply_counts.get(t.id, 0),
        'commentCount': comment_counts.get(t.id, 0),
        'section': sections_by_topic.get(t.id, []),
        'statusUpdateTime': t.status_update_time.isoformat() if t.status_update_time else None,
        'upvoteTime': t.upvote_time.isoformat() if t.upvote_time else None
      })

    # Nuxt 返回数组（不包裹 code/message）
    return jsonify(topics)
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('', methods=['POST'])
@token_required
def create_topic(current_user=None):
  """
  POST /api/topic
  """
  try:
    data = request.get_json() or {}

    title = data.get('title')
    content = data.get('content')
    is_nsfw = bool(data.get('is_nsfw', False))
    category = data.get('category') or ''
    section = data.get('section') or []
    tag = data.get('tag') or []

    if not title or not content:
      return error('标题或内容不能为空', code=400, http_status=400)

    topic = Topic(
      title=title,
      content=content,
      is_nsfw=is_nsfw,
      status=0,
      category=category,
      user_id=current_user.id,
      created=datetime.utcnow(),
      updated=datetime.utcnow(),
      status_update_time=datetime.utcnow()
    )

    db.session.add(topic)
    db.session.commit()

    # Nuxt 返回新 topic id（number）
    return jsonify(topic.id)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>', methods=['GET'])
def get_topic_detail(topic_id):
  """
  GET /api/topic/:tid
  """
  try:
    topic = Topic.query.get(topic_id)
    if not topic or topic.status == 2:
      return error('未找到该话题', code=404, http_status=404)

    # view +1
    topic.view = (topic.view or 0) + 1
    db.session.commit()

    uid = get_uid_from_refresh_cookie()

    nsfw = _get_nsfw_mode()
    if (nsfw == 'sfw' and topic.is_nsfw) or topic.status == 1:
      # Nuxt 直接返回字符串
      return jsonify('banned')

    tags = [t.tag for t in TopicTag.query.filter_by(topic_id=topic.id).all()]

    # sections
    rels = TopicSectionRelation.query.filter_by(topic_id=topic.id).all()
    section_ids = list({r.topic_section_id for r in rels})
    section_map = {}
    if section_ids:
      for s in TopicSection.query.filter(TopicSection.id.in_(section_ids)).all():
        section_map[s.id] = s.name
    sections = [section_map.get(r.topic_section_id) for r in rels if section_map.get(r.topic_section_id)]

    # counts
    like_count = TopicLike.query.filter_by(topic_id=topic.id).count()
    dislike_count = TopicDislike.query.filter_by(topic_id=topic.id).count()
    favorite_count = TopicFavorite.query.filter_by(topic_id=topic.id).count()
    upvote_count = TopicUpvote.query.filter_by(topic_id=topic.id).count()
    reply_count = TopicReply.query.filter_by(topic_id=topic.id).count()

    is_liked = bool(uid and TopicLike.query.filter_by(topic_id=topic.id, user_id=uid).first())
    is_disliked = bool(uid and TopicDislike.query.filter_by(topic_id=topic.id, user_id=uid).first())
    is_favorited = bool(uid and TopicFavorite.query.filter_by(topic_id=topic.id, user_id=uid).first())
    is_upvoted = bool(uid and TopicUpvote.query.filter_by(topic_id=topic.id, user_id=uid).first())

    u = User.query.get(topic.user_id)

    detail = {
      'id': topic.id,
      'title': topic.title,
      'view': topic.view or 0,
      'status': topic.status,
      'isNSFW': bool(topic.is_nsfw),
      'category': topic.category,
      'section': sections,
      'tag': tags,
      'user': {
        'id': topic.user_id,
        'name': u.name if u else '',
        'avatar': u.avatar if u else '',
        'moemoepoint': u.moemoepoint if u else 0
      },
      'likeCount': like_count,
      'isLiked': is_liked,
      'dislikeCount': dislike_count,
      'isDisliked': is_disliked,
      'favoriteCount': favorite_count,
      'isFavorited': is_favorited,
      'upvoteCount': upvote_count,
      'isUpvoted': is_upvoted,
      'replyCount': reply_count,
      'bestAnswer': None,
      'contentHtml': markdown_to_html(topic.content),
      'contentMarkdown': topic.content,
      'statusUpdateTime': topic.status_update_time.isoformat() if topic.status_update_time else None,
      'upvoteTime': topic.upvote_time.isoformat() if topic.upvote_time else None,
      'edited': topic.edited.isoformat() if topic.edited else None,
      'created': topic.created.isoformat() if topic.created else None
    }

    # best answer (basic)
    if topic.best_answer_id:
      ba = TopicReply.query.get(topic.best_answer_id)
      if ba:
        ba_user = User.query.get(ba.user_id)
        detail['bestAnswer'] = {
          'id': ba.id,
          'topicId': ba.topic_id,
          'floor': ba.floor,
          'user': {
            'id': ba.user_id,
            'name': ba_user.name if ba_user else '',
            'avatar': ba_user.avatar if ba_user else '',
            'moemoepoint': ba_user.moemoepoint if ba_user else 0
          },
          'edited': ba.edited.isoformat() if ba.edited else None,
          'created': ba.created.isoformat() if ba.created else None,
          'contentMarkdown': ba.content,
          'contentHtml': markdown_to_html(ba.content)
        }

    return jsonify(detail)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>', methods=['PUT'])
@token_required
def update_topic(topic_id, current_user=None):
  """
  PUT /api/topic/:tid
  """
  try:
    data = request.get_json() or {}

    topic = Topic.query.get(topic_id)
    if not topic:
      return error('未找到此话题', code=404, http_status=404)

    # Nuxt: 作者或管理员(role>=2)；Flask 里暂以 admin 角色放行
    if current_user.id != topic.user_id and current_user.role != 'admin':
      return error('您没有权限更改此话题', code=403, http_status=403)

    topic.title = data.get('title', topic.title)
    topic.content = data.get('content', topic.content)
    topic.is_nsfw = bool(data.get('is_nsfw', topic.is_nsfw))
    topic.edited = datetime.utcnow()
    topic.status_update_time = datetime.utcnow()

    # 更新分类/section/tag
    if 'category' in data or 'section' in data or 'tag' in data:
      category_info = topic._parse_category()
      payload = {
        'category': data.get('category', category_info.get('name')),
        'sections': data.get('section', category_info.get('sections', [])),
        'tags': data.get('tag', category_info.get('tags', []))
      }
      topic.category = json.dumps(payload, ensure_ascii=False)

    db.session.commit()
    return jsonify('MOEMOE update topic successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>', methods=['DELETE'])
@token_required
def delete_topic_permanently(topic_id, current_user=None):
  """
  DELETE /api/topic/:tid
  """
  try:
    topic = Topic.query.get(topic_id)
    if not topic:
      return error('未找到该话题', code=404, http_status=404)

    if topic.user_id != current_user.id and current_user.role != 'admin':
      return error('您没有权限删除该话题', code=403, http_status=403)

    # 简化：删除 replies，再删除 topic
    TopicReply.query.filter_by(topic_id=topic_id).delete()
    db.session.delete(topic)
    db.session.commit()
    return jsonify('MOEMOE delete topic permanently!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


# ----- reactions (like/dislike/favorite/upvote) -----
@kun_topic_bp.route('/<int:topic_id>/like', methods=['PUT'])
@token_required
def like_topic(topic_id, current_user=None):
  return jsonify(True)


@kun_topic_bp.route('/<int:topic_id>/dislike', methods=['PUT'])
@token_required
def dislike_topic(topic_id, current_user=None):
  return jsonify(True)


@kun_topic_bp.route('/<int:topic_id>/favorite', methods=['PUT'])
@token_required
def favorite_topic(topic_id, current_user=None):
  return jsonify(True)


@kun_topic_bp.route('/<int:topic_id>/upvote', methods=['PUT'])
@token_required
def upvote_topic(topic_id, current_user=None):
  return jsonify(True)


# ----- replies -----
@kun_topic_bp.route('/<int:topic_id>/reply', methods=['GET'])
def list_replies(topic_id):
  try:
    topic = Topic.query.get(topic_id)
    if not topic or topic.status == 2:
      return error('话题不存在', code=404, http_status=404)

    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort_order = request.args.get('sortOrder', 'asc', type=str)

    uid = get_uid_from_refresh_cookie()

    special_ids = []
    if topic.pinned_reply_id:
      special_ids.append(topic.pinned_reply_id)
    if topic.best_answer_id and topic.best_answer_id not in special_ids:
      special_ids.append(topic.best_answer_id)

    # only include special on first page
    special_replies = []
    if page == 1 and special_ids:
      special_replies = TopicReply.query.filter(TopicReply.id.in_(special_ids)).all()

    q = TopicReply.query.filter_by(topic_id=topic_id)
    if special_ids:
      q = q.filter(~TopicReply.id.in_(special_ids))
    if sort_order == 'desc':
      q = q.order_by(TopicReply.floor.desc())
    else:
      q = q.order_by(TopicReply.floor.asc())

    regular = q.offset((page - 1) * limit).limit(limit).all()

    all_rows = special_replies + regular
    reply_ids = [r.id for r in all_rows]
    user_ids = list({r.user_id for r in all_rows})

    users_map = {}
    if user_ids:
      for u in User.query.filter(User.id.in_(user_ids)).all():
        users_map[u.id] = u

    like_counts = {rid: c for rid, c in db.session.query(
      TopicReplyLike.topic_reply_id, func.count(TopicReplyLike.id)
    ).filter(TopicReplyLike.topic_reply_id.in_(reply_ids)).group_by(TopicReplyLike.topic_reply_id).all()} if reply_ids else {}

    dislike_counts = {rid: c for rid, c in db.session.query(
      TopicReplyDislike.topic_reply_id, func.count(TopicReplyDislike.id)
    ).filter(TopicReplyDislike.topic_reply_id.in_(reply_ids)).group_by(TopicReplyDislike.topic_reply_id).all()} if reply_ids else {}

    # targets count = how many target_by (reverse) not implemented; fallback 0

    liked_set = set()
    disliked_set = set()
    if uid and reply_ids:
      liked_set = set(rid for (rid,) in db.session.query(TopicReplyLike.topic_reply_id).filter(
        TopicReplyLike.user_id == uid,
        TopicReplyLike.topic_reply_id.in_(reply_ids)
      ).all())
      disliked_set = set(rid for (rid,) in db.session.query(TopicReplyDislike.topic_reply_id).filter(
        TopicReplyDislike.user_id == uid,
        TopicReplyDislike.topic_reply_id.in_(reply_ids)
      ).all())

    data = []
    for r in all_rows:
      u = users_map.get(r.user_id)
      data.append({
        'id': r.id,
        'topicId': r.topic_id,
        'floor': r.floor,
        'user': {
          'id': r.user_id,
          'name': u.name if u else '',
          'avatar': u.avatar if u else '',
          'moemoepoint': u.moemoepoint if u else 0
        },
        'edited': r.edited.isoformat() if r.edited else None,
        'contentMarkdown': r.content,
        'contentHtml': markdown_to_html(r.content),
        'likeCount': like_counts.get(r.id, 0),
        'isLiked': r.id in liked_set,
        'dislikeCount': dislike_counts.get(r.id, 0),
        'isDisliked': r.id in disliked_set,
        'targetByCount': 0,
        'comment': [],
        'created': r.created.isoformat() if r.created else None,
        'targets': [],
        'isPinned': r.id == topic.pinned_reply_id,
        'isBestAnswer': r.id == topic.best_answer_id
      })

    # ensure pinned before best answer (match Nuxt behavior roughly)
    data.sort(key=lambda x: (not x.get('isPinned', False), not x.get('isBestAnswer', False)))

    return jsonify(data)
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>/reply', methods=['POST'])
@token_required
def create_reply(topic_id, current_user=None):
  try:
    data = request.get_json() or {}
    content = (data.get('content') or '').strip()
    if not content:
      return error('回复内容不能为空', code=400, http_status=400)

    topic = Topic.query.get(topic_id)
    if not topic or topic.status == 2:
      return error('话题不存在', code=404, http_status=404)

    # floor = max(floor)+1
    last_floor = db.session.query(func.max(TopicReply.floor)).filter(TopicReply.topic_id == topic_id).scalar()
    new_floor = (last_floor or 0) + 1

    reply = TopicReply(
      topic_id=topic_id,
      user_id=current_user.id,
      content=content,
      floor=new_floor,
      edited=None,
      created=datetime.utcnow(),
      updated=datetime.utcnow()
    )
    db.session.add(reply)
    topic.status_update_time = datetime.utcnow()
    # optional targets (topic_reply_target)
    targets = data.get('targets') or []
    valid_targets = [t for t in targets if (t.get('content') or '').strip() and t.get('targetReplyId')]
    db.session.commit()

    if valid_targets:
      for t in valid_targets:
        db.session.add(TopicReplyTarget(
          reply_id=reply.id,
          target_reply_id=int(t.get('targetReplyId')),
          content=t.get('content')
        ))
      db.session.commit()

    u = User.query.get(reply.user_id)
    formatted = {
      'id': reply.id,
      'topicId': reply.topic_id,
      'floor': reply.floor,
      'user': {
        'id': reply.user_id,
        'name': u.name if u else '',
        'avatar': u.avatar if u else '',
        'moemoepoint': u.moemoepoint if u else 0
      },
      'edited': reply.edited.isoformat() if reply.edited else None,
      'contentMarkdown': reply.content,
      'contentHtml': markdown_to_html(reply.content),
      'likeCount': 0,
      'isLiked': False,
      'dislikeCount': 0,
      'isDisliked': False,
      'targetByCount': 0,
      'comment': [],
      'created': reply.created.isoformat() if reply.created else None,
      'targets': [],
      'isBestAnswer': False,
      'isPinned': False
    }
    return jsonify(formatted)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>/reply', methods=['PUT'])
@token_required
def update_reply(topic_id, current_user=None):
  try:
    data = request.get_json() or {}
    reply_id = data.get('replyId') or data.get('reply_id')
    content = (data.get('content') or '').strip()
    if not reply_id:
      return error('缺少 replyId', code=400, http_status=400)
    if not content:
      return error('回复内容不能为空', code=400, http_status=400)

    reply = TopicReply.query.get(reply_id)
    if not reply or reply.topic_id != topic_id:
      return error('回复不存在', code=404, http_status=404)

    if reply.user_id != current_user.id and current_user.role != 'admin':
      return error('没有权限编辑回复', code=403, http_status=403)

    reply.content = content
    reply.edited = datetime.utcnow()
    reply.updated = datetime.utcnow()

    # targets overwrite if provided
    if 'targets' in data:
      TopicReplyTarget.query.filter_by(reply_id=reply.id).delete()
      targets = data.get('targets') or []
      valid_targets = [t for t in targets if (t.get('content') or '').strip() and t.get('targetReplyId')]
      for t in valid_targets:
        db.session.add(TopicReplyTarget(
          reply_id=reply.id,
          target_reply_id=int(t.get('targetReplyId')),
          content=t.get('content')
        ))
    db.session.commit()

    uid = get_uid_from_refresh_cookie()
    u = User.query.get(reply.user_id)
    like_count = TopicReplyLike.query.filter_by(topic_reply_id=reply.id).count()
    dislike_count = TopicReplyDislike.query.filter_by(topic_reply_id=reply.id).count()
    is_liked = bool(uid and TopicReplyLike.query.filter_by(topic_reply_id=reply.id, user_id=uid).first())
    is_disliked = bool(uid and TopicReplyDislike.query.filter_by(topic_reply_id=reply.id, user_id=uid).first())

    formatted = {
      'id': reply.id,
      'topicId': reply.topic_id,
      'floor': reply.floor,
      'user': {
        'id': reply.user_id,
        'name': u.name if u else '',
        'avatar': u.avatar if u else '',
        'moemoepoint': u.moemoepoint if u else 0
      },
      'edited': reply.edited.isoformat() if reply.edited else None,
      'contentMarkdown': reply.content,
      'contentHtml': markdown_to_html(reply.content),
      'likeCount': like_count,
      'isLiked': is_liked,
      'dislikeCount': dislike_count,
      'isDisliked': is_disliked,
      'targetByCount': 0,
      'comment': [],
      'created': reply.created.isoformat() if reply.created else None,
      'targets': [],
      'isPinned': False,
      'isBestAnswer': False
    }
    return jsonify(formatted)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_topic_bp.route('/<int:topic_id>/reply', methods=['DELETE'])
@token_required
def delete_reply(topic_id, current_user=None):
  try:
    reply_id = request.args.get('replyId', type=int) or request.args.get('reply_id', type=int)
    if not reply_id:
      return error('缺少 replyId 参数', code=400, http_status=400)

    reply = TopicReply.query.get(reply_id)
    if not reply or reply.status == 2 or reply.topic_id != topic_id:
      return error('回复不存在', code=404, http_status=404)

    if reply.user_id != current_user.id and current_user.role != 'admin':
      return error('没有权限删除回复', code=403, http_status=403)

    reply.status = 2
    db.session.commit()
    return jsonify('MOEMOE delete reply successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)

