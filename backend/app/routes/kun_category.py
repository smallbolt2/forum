"""
Nuxt/Nitro 兼容：分类页数据

GET /api/category?category=galgame|technique|others

返回：CategorySectionStats[]（供 CategoryContainer 渲染）
"""

import json
from datetime import datetime
from collections import defaultdict

from flask import Blueprint, request, jsonify

from app.models.topic import Topic
from app.models.user import User
from app.models.prisma_topic_extras import (
  TopicSection,
  TopicSectionRelation
)
from app.utils.response import error


kun_category_bp = Blueprint('kun_category', __name__)


def _get_is_sfw():
  # Nuxt 里 getNSFWCookie(event) 默认返回 'sfw'
  settings_cookie = request.cookies.get('KUNGalgameSettings')
  if not settings_cookie:
    return True
  try:
    settings = json.loads(settings_cookie)
    return settings.get('showKUNGalgameContentLimit') != 'nsfw'
  except Exception:
    return True


@kun_category_bp.route('', methods=['GET'])
def category_sections():
  try:
    category = request.args.get('category', type=str)
    if not category:
      return error('category is required', code=400, http_status=400)

    is_sfw = _get_is_sfw()

    topics_q = Topic.query.filter(Topic.status != 1, Topic.category == category).order_by(Topic.created.desc())
    if is_sfw:
      topics_q = topics_q.filter(Topic.is_nsfw == False)  # noqa: E712

    topics = topics_q.all()
    if not topics:
      return jsonify([])

    topic_ids = [t.id for t in topics]
    rels = TopicSectionRelation.query.filter(TopicSectionRelation.topic_id.in_(topic_ids)).all()
    section_ids = list({r.topic_section_id for r in rels})

    section_map = {}
    if section_ids:
      for s in TopicSection.query.filter(TopicSection.id.in_(section_ids)).all():
        section_map[s.id] = s.name

    topic_map = {t.id: t for t in topics}

    # 由于 topics 已按 created desc 排序，按遍历顺序设置 latestTopic 为第一个即可
    latest_seen = set()
    stats_map = {}

    # Build set of section -> first (latest) topic info
    for t in topics:
      t_rels = [r for r in rels if r.topic_id == t.id]
      for r in t_rels:
        sid = r.topic_section_id
        if sid not in stats_map:
          stats_map[sid] = {
            'id': sid,
            'name': section_map.get(sid, ''),
            'topicCount': 0,
            'viewCount': 0,
            'latestTopic': None
          }
        st = stats_map[sid]
        st['topicCount'] += 1
        st['viewCount'] += int(getattr(t, 'view', 0) or 0)
        if st['latestTopic'] is None:
          st['latestTopic'] = {
            'id': t.id,
            'title': t.title,
            'created': t.created.isoformat() if t.created else None
          }

    return jsonify(list(stats_map.values()))
  except Exception as e:
    return error(str(e), code=500, http_status=500)

