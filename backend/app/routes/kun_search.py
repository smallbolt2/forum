from collections import defaultdict

from flask import Blueprint, request, jsonify
from sqlalchemy import func, or_

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.user import User
from app.models.prisma_topic_extras import (
  TopicTag,
  TopicSection,
  TopicSectionRelation,
  TopicLike,
  TopicComment,
  TopicReplyTarget,
)


kun_search_bp = Blueprint('kun_search', __name__)


def _split_keywords(raw: str):
  return [k.strip() for k in (raw or '').strip().split(' ') if k.strip()]


@kun_search_bp.route('', methods=['GET'])
def search():
  keywords = (request.args.get('keywords') or '').strip()
  search_type = (request.args.get('type') or 'topic').strip()
  page = request.args.get('page', 1, type=int) or 1
  limit = request.args.get('limit', 12, type=int) or 12
  offset = (max(page, 1) - 1) * max(limit, 1)

  if not keywords:
    return jsonify([])

  keys = _split_keywords(keywords)

  if search_type == 'topic':
    query = Topic.query.filter(Topic.status != 2)
    for kw in keys:
      pattern = f'%{kw}%'
      query = query.filter(or_(
        Topic.title.like(pattern),
        Topic.content.like(pattern),
        Topic.category.like(pattern),
      ))

    rows = query.order_by(Topic.created.desc()).offset(offset).limit(limit).all()
    topic_ids = [t.id for t in rows]
    user_ids = list({t.user_id for t in rows})

    users_map = {}
    if user_ids:
      for u in User.query.filter(User.id.in_(user_ids)).all():
        users_map[u.id] = u

    tags_by_topic = defaultdict(list)
    if topic_ids:
      for tt in TopicTag.query.filter(TopicTag.topic_id.in_(topic_ids)).all():
        tags_by_topic[tt.topic_id].append(tt.tag)

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

    like_counts = {tid: c for tid, c in db.session.query(
      TopicLike.topic_id, func.count(TopicLike.id)
    ).filter(TopicLike.topic_id.in_(topic_ids)).group_by(TopicLike.topic_id).all()} if topic_ids else {}

    reply_counts = {tid: c for tid, c in db.session.query(
      TopicReply.topic_id, func.count(TopicReply.id)
    ).filter(TopicReply.topic_id.in_(topic_ids)).group_by(TopicReply.topic_id).all()} if topic_ids else {}

    comment_counts = {tid: c for tid, c in db.session.query(
      TopicComment.topic_id, func.count(TopicComment.id)
    ).filter(TopicComment.topic_id.in_(topic_ids)).group_by(TopicComment.topic_id).all()} if topic_ids else {}

    result = []
    for t in rows:
      u = users_map.get(t.user_id)
      result.append({
        'id': t.id,
        'title': t.title,
        'view': t.view or 0,
        'statusUpdateTime': t.status_update_time.isoformat() if t.status_update_time else None,
        'tag': tags_by_topic.get(t.id, []),
        'section': sections_by_topic.get(t.id, []),
        'user': {
          'id': t.user_id,
          'name': u.name if u else '',
          'avatar': u.avatar if u else ''
        },
        'status': t.status,
        'upvoteTime': t.upvote_time.isoformat() if t.upvote_time else None,
        'likeCount': like_counts.get(t.id, 0),
        'replyCount': reply_counts.get(t.id, 0),
        'commentCount': comment_counts.get(t.id, 0),
        'hasBestAnswer': bool(t.best_answer_id),
        'isNSFWTopic': bool(t.is_nsfw)
      })
    return jsonify(result)

  if search_type == 'user':
    pattern = f'%{keywords}%'
    rows = User.query.filter(User.name.like(pattern)).order_by(
      User.created.desc()
    ).offset(offset).limit(limit).all()
    return jsonify([{
      'id': u.id,
      'name': u.name,
      'avatar': u.avatar,
      'bio': u.bio,
      'moemoepoint': u.moemoepoint,
      'created': u.created.isoformat() if u.created else None
    } for u in rows])

  if search_type == 'reply':
    pattern = f'%{keywords}%'
    rows = TopicReply.query.filter(TopicReply.content.like(pattern)).order_by(
      TopicReply.created.desc()
    ).offset(offset).limit(limit).all()
    topic_ids = list({r.topic_id for r in rows})
    user_ids = list({r.user_id for r in rows})
    reply_ids = [r.id for r in rows]

    topic_map = {}
    if topic_ids:
      for t in Topic.query.filter(Topic.id.in_(topic_ids)).all():
        topic_map[t.id] = t

    user_map = {}
    if user_ids:
      for u in User.query.filter(User.id.in_(user_ids)).all():
        user_map[u.id] = u

    target_rows = TopicReplyTarget.query.filter(
      TopicReplyTarget.reply_id.in_(reply_ids)
    ).all() if reply_ids else []
    target_reply_ids = list({t.target_reply_id for t in target_rows})
    target_reply_map = {}
    if target_reply_ids:
      for tr in TopicReply.query.filter(TopicReply.id.in_(target_reply_ids)).all():
        target_reply_map[tr.id] = tr
    target_user_ids = list({tr.user_id for tr in target_reply_map.values()})
    target_user_map = {}
    if target_user_ids:
      for u in User.query.filter(User.id.in_(target_user_ids)).all():
        target_user_map[u.id] = u
    targets_by_reply = defaultdict(list)
    for tr in target_rows:
      target_reply = target_reply_map.get(tr.target_reply_id)
      if not target_reply:
        continue
      target_user = target_user_map.get(target_reply.user_id)
      content = (tr.content or '')[:150]
      preview = (target_reply.content or '')[:150]
      targets_by_reply[tr.reply_id].append({
        'id': target_reply.id,
        'user': {
          'id': target_reply.user_id,
          'name': target_user.name if target_user else '',
          'avatar': target_user.avatar if target_user else ''
        },
        'content': content,
        'contentPreview': preview
      })

    return jsonify([{
      'topicId': r.topic_id,
      'topicTitle': (topic_map.get(r.topic_id).title if topic_map.get(r.topic_id) else ''),
      'floor': r.floor,
      'content': (r.content or '')[:233],
      'user': {
        'id': r.user_id,
        'name': (user_map.get(r.user_id).name if user_map.get(r.user_id) else ''),
        'avatar': (user_map.get(r.user_id).avatar if user_map.get(r.user_id) else '')
      },
      'targets': targets_by_reply.get(r.id, []),
      'created': r.created.isoformat() if r.created else None
    } for r in rows])

  # default comment search
  pattern = f'%{keywords}%'
  rows = TopicComment.query.filter(TopicComment.content.like(pattern)).order_by(
    TopicComment.created.desc()
  ).offset(offset).limit(limit).all()
  topic_ids = list({c.topic_id for c in rows})
  user_ids = list({c.user_id for c in rows} | {c.target_user_id for c in rows})

  topic_map = {}
  if topic_ids:
    for t in Topic.query.filter(Topic.id.in_(topic_ids)).all():
      topic_map[t.id] = t

  user_map = {}
  if user_ids:
    for u in User.query.filter(User.id.in_(user_ids)).all():
      user_map[u.id] = u

  return jsonify([{
    'topicId': c.topic_id,
    'topicTitle': (topic_map.get(c.topic_id).title if topic_map.get(c.topic_id) else ''),
    'content': (c.content or '')[:233],
    'user': {
      'id': c.user_id,
      'name': (user_map.get(c.user_id).name if user_map.get(c.user_id) else ''),
      'avatar': (user_map.get(c.user_id).avatar if user_map.get(c.user_id) else '')
    },
    'targetUser': {
      'id': c.target_user_id,
      'name': (user_map.get(c.target_user_id).name if user_map.get(c.target_user_id) else ''),
      'avatar': (user_map.get(c.target_user_id).avatar if user_map.get(c.target_user_id) else '')
    },
    'created': c.created.isoformat() if c.created else None
  } for c in rows])
