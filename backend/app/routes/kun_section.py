"""
GET /api/section — 与 server/api/section/index.get.ts 对齐
"""

from collections import defaultdict

from sqlalchemy import and_, func

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
)


kun_section_bp = Blueprint('kun_section', __name__)


def _get_nsfw_mode():
  return request.cookies.get('nsfw') or request.cookies.get('kun-nsfw') or ''


def _validate_section_query():
  section = (request.args.get('section') or '').strip()
  if not section or len(section) > 50:
    return None, 'section 无效'
  page = request.args.get('page', 1, type=int)
  limit = request.args.get('limit', 30, type=int)
  sort_order = (request.args.get('sortOrder') or 'desc').lower()
  if page < 1 or page > 9999999:
    return None, 'page 无效'
  if limit < 1 or limit > 30:
    return None, 'limit 无效'
  if sort_order not in ('asc', 'desc'):
    return None, 'sortOrder 无效'
  return {
    'section': section,
    'page': page,
    'limit': limit,
    'sort_order': sort_order,
  }, None


@kun_section_bp.route('', methods=['GET'])
def get_section_topics():
  params, err = _validate_section_query()
  if err:
    return jsonify({'code': 400, 'message': err, 'data': None}), 400

  section_name = params['section']
  page = params['page']
  limit = params['limit']
  sort_order = params['sort_order']

  sec = TopicSection.query.filter(TopicSection.name == section_name).first()
  if not sec:
    return jsonify({'topics': [], 'totalCount': 0})

  base = Topic.query.join(
    TopicSectionRelation,
    and_(
      TopicSectionRelation.topic_id == Topic.id,
      TopicSectionRelation.topic_section_id == sec.id,
    ),
  ).filter(Topic.status != 1)

  if _get_nsfw_mode() == 'sfw':
    base = base.filter(Topic.is_nsfw == False)  # noqa: E712

  total_count = base.count()

  order_col = Topic.created
  if sort_order == 'asc':
    base = base.order_by(order_col.asc())
  else:
    base = base.order_by(order_col.desc())

  offset = (page - 1) * limit
  rows = base.offset(offset).limit(limit).all()
  topic_ids = [t.id for t in rows]
  if not topic_ids:
    return jsonify({'topics': [], 'totalCount': total_count})

  tags_by_topic = defaultdict(list)
  for tt in TopicTag.query.filter(TopicTag.topic_id.in_(topic_ids)).all():
    tags_by_topic[tt.topic_id].append(tt.tag)

  sections_by_topic = defaultdict(list)
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

  like_counts = {
    tid: c for tid, c in db.session.query(
      TopicLike.topic_id, func.count(TopicLike.id)
    ).filter(TopicLike.topic_id.in_(topic_ids)).group_by(TopicLike.topic_id).all()
  }

  reply_counts = {
    tid: c for tid, c in db.session.query(
      TopicReply.topic_id, func.count(TopicReply.id)
    ).filter(TopicReply.topic_id.in_(topic_ids)).group_by(TopicReply.topic_id).all()
  }

  user_ids = list({t.user_id for t in rows})
  users_map = {}
  if user_ids:
    for u in User.query.filter(User.id.in_(user_ids)).all():
      users_map[u.id] = u

  topics = []
  for t in rows:
    u = users_map.get(t.user_id)
    raw = t.content or ''
    topics.append({
      'id': t.id,
      'title': t.title,
      'content': raw[:233],
      'section': sections_by_topic.get(t.id, []),
      'tag': tags_by_topic.get(t.id, []),
      'view': t.view or 0,
      'like': like_counts.get(t.id, 0),
      'reply': reply_counts.get(t.id, 0),
      'user': {
        'id': t.user_id,
        'name': u.name if u else '',
        'avatar': u.avatar if u else '',
      },
      'hasBestAnswer': bool(t.best_answer_id),
      'isNSFWTopic': bool(t.is_nsfw),
      'created': t.created.isoformat() if t.created else None,
    })

  return jsonify({'topics': topics, 'totalCount': total_count})
