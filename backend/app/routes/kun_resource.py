"""
Nuxt/Nitro 兼容：资源/求助话题列表

GET /api/resource?page&limit&sortField&sortOrder&category
返回 TopicCard[]
"""

from collections import defaultdict

from flask import Blueprint, request, jsonify
from sqlalchemy import func

from app import db
from app.models.topic import Topic
from app.models.user import User
from app.models.topic_reply import TopicReply
from app.models.prisma_topic_extras import (
  TopicTag,
  TopicSection,
  TopicSectionRelation,
  TopicLike
)
from app.utils.response import error


kun_resource_bp = Blueprint('kun_resource', __name__)

RESOURCE_SECTIONS = {'g-seeking', 'g-other', 't-help'}


@kun_resource_bp.route('', methods=['GET'])
def list_resource_topics():
  try:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 24, type=int)
    sort_field = request.args.get('sortField', 'status_update_time', type=str)
    sort_order = request.args.get('sortOrder', 'desc', type=str)
    category = request.args.get('category', 'all', type=str)

    # find section ids for resource sections
    section_rows = TopicSection.query.filter(TopicSection.name.in_(list(RESOURCE_SECTIONS))).all()
    section_ids = [s.id for s in section_rows]
    if not section_ids:
      return jsonify([])

    topic_ids_subq = db.session.query(TopicSectionRelation.topic_id).filter(
      TopicSectionRelation.topic_section_id.in_(section_ids)
    ).subquery()

    q = Topic.query.filter(
      Topic.status != 1,
      Topic.id.in_(topic_ids_subq)
    )
    if category and category != 'all':
      q = q.filter(Topic.category == category)

    order_col = getattr(Topic, sort_field, Topic.status_update_time)
    q = q.order_by(order_col.asc() if sort_order == 'asc' else order_col.desc())

    rows = q.offset((page - 1) * limit).limit(limit).all()
    ids = [t.id for t in rows]

    # batch tags
    tags_by_topic = defaultdict(list)
    if ids:
      for tt in TopicTag.query.filter(TopicTag.topic_id.in_(ids)).all():
        tags_by_topic[tt.topic_id].append(tt.tag)

    # batch sections
    sections_by_topic = defaultdict(list)
    if ids:
      rels = TopicSectionRelation.query.filter(TopicSectionRelation.topic_id.in_(ids)).all()
      sids = list({r.topic_section_id for r in rels})
      smap = {}
      if sids:
        for s in TopicSection.query.filter(TopicSection.id.in_(sids)).all():
          smap[s.id] = s.name
      for r in rels:
        name = smap.get(r.topic_section_id)
        if name:
          sections_by_topic[r.topic_id].append(name)

    # counts
    like_counts = {tid: c for tid, c in db.session.query(
      TopicLike.topic_id, func.count(TopicLike.id)
    ).filter(TopicLike.topic_id.in_(ids)).group_by(TopicLike.topic_id).all()} if ids else {}

    reply_counts = {tid: c for tid, c in db.session.query(
      TopicReply.topic_id, func.count(TopicReply.id)
    ).filter(TopicReply.topic_id.in_(ids)).group_by(TopicReply.topic_id).all()} if ids else {}

    # users
    user_ids = list({t.user_id for t in rows})
    users_map = {}
    if user_ids:
      for u in User.query.filter(User.id.in_(user_ids)).all():
        users_map[u.id] = u

    items = []
    for t in rows:
      u = users_map.get(t.user_id)
      items.append({
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
        'commentCount': 0,
        'section': sections_by_topic.get(t.id, []),
        'statusUpdateTime': t.status_update_time.isoformat() if t.status_update_time else None,
        'upvoteTime': t.upvote_time.isoformat() if t.upvote_time else None
      })

    return jsonify(items)
  except Exception as e:
    return error(str(e), code=500, http_status=500)

