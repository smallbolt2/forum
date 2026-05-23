"""
Nuxt/Nitro 兼容的 Admin API

映射自 server/api/admin/*
"""

from datetime import datetime, timedelta

from flask import Blueprint, request
from sqlalchemy import text

from app import db
from app.models.user import User
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.prisma_topic_extras import TopicComment
from app.models.prisma_galgame_min import Galgame, GalgameResource
from app.utils.auth import token_required
from app.utils.response import success, error

kun_admin_bp = Blueprint('kun_admin', __name__)

# 与前端 app/constants/admin.ts 保持一致
OVERVIEW_STATS_ITEMS = [
  'user',
  'topic',
  'topic_reply',
  'topic_comment',
  'galgame',
  'galgame_resource',
  'galgame_comment',
  'galgame_website',
  'galgame_website_comment',
  'chat_message',
]

OVERVIEW_STATS_MAP = {
  'user': {'label': '用户', 'color': '#006FEE'},
  'topic': {'label': '话题', 'color': '#7828C8'},
  'topic_reply': {'label': '话题回复', 'color': '#17C964'},
  'topic_comment': {'label': '话题评论', 'color': '#F31260'},
  'galgame': {'label': 'game', 'color': '#FF4ECD'},
  'galgame_resource': {'label': 'game 资源', 'color': '#F5A524'},
  'galgame_comment': {'label': 'game 评论', 'color': '#7EE7FC'},
  'galgame_website': {'label': 'game 网站', 'color': '#7ccf00'},
  'galgame_website_comment': {'label': 'game 网站评论', 'color': '#ff637e'},
  'chat_message': {'label': '聊天消息', 'color': '#ff8904'},
}

# SQLAlchemy 模型映射（无模型的表用 raw SQL）
OVERVIEW_COUNT_MODELS = {
  'user': User,
  'topic': Topic,
  'topic_reply': TopicReply,
  'topic_comment': TopicComment,
  'galgame': Galgame,
  'galgame_resource': GalgameResource,
}


def _require_admin(current_user):
  if not current_user:
    return error('用户登录失效', code=401, http_status=401)
  if int(current_user.role) <= 1:
    return error('您没有权限查看此页面', code=403, http_status=403)
  return None


def _count_table(table_name: str) -> int:
  if table_name in OVERVIEW_COUNT_MODELS:
    return db.session.query(OVERVIEW_COUNT_MODELS[table_name]).count()
  sql = text(f'SELECT COUNT(*) AS cnt FROM [{table_name}]')
  row = db.session.execute(sql).first()
  return int(row[0]) if row else 0


def _daily_counts(table_name: str, start: datetime, end: datetime) -> dict[str, int]:
  """按日期聚合 created 字段，返回 {yyyy-MM-dd: count}"""
  sql = text(f'''
    SELECT CAST([created] AS date) AS [day], COUNT([id]) AS [cnt]
    FROM [{table_name}]
    WHERE [created] >= :start AND [created] <= :end
    GROUP BY CAST([created] AS date)
    ORDER BY [day] ASC
  ''')
  rows = db.session.execute(sql, {'start': start, 'end': end}).fetchall()
  result = {}
  for row in rows:
    day = row[0]
    if hasattr(day, 'strftime'):
      key = day.strftime('%Y-%m-%d')
    else:
      key = str(day)[:10]
    result[key] = int(row[1])
  return result


def _date_range(days: int):
  end = datetime.utcnow().replace(hour=23, minute=59, second=59, microsecond=999999)
  start = (end - timedelta(days=days - 1)).replace(hour=0, minute=0, second=0, microsecond=0)
  return start, end


def _each_day_keys(start: datetime, end: datetime) -> list[str]:
  keys = []
  cur = start.date()
  end_date = end.date()
  while cur <= end_date:
    keys.append(cur.strftime('%Y-%m-%d'))
    cur += timedelta(days=1)
  return keys


@kun_admin_bp.route('/overview/all', methods=['GET'])
@token_required
def overview_all(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  result = []
  for name in OVERVIEW_STATS_ITEMS:
    info = OVERVIEW_STATS_MAP[name]
    try:
      count = _count_table(name)
    except Exception:
      count = 0
    result.append({
      'name': name,
      'label': info['label'],
      'color': info['color'],
      'count': count,
    })

  return success(data=result, message='获取成功')


@kun_admin_bp.route('/overview/stats', methods=['GET'])
@token_required
def overview_stats(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  days = request.args.get('days', 30, type=int)
  days = max(1, min(days, 365))

  start, end = _date_range(days)
  day_keys = _each_day_keys(start, end)

  daily_map = {d: {m: 0 for m in OVERVIEW_STATS_ITEMS} for d in day_keys}

  for model_name in OVERVIEW_STATS_ITEMS:
    try:
      counts_by_day = _daily_counts(model_name, start, end)
    except Exception:
      counts_by_day = {}
    for day, cnt in counts_by_day.items():
      if day in daily_map:
        daily_map[day][model_name] = cnt

  final_data = [{'date': d, **daily_map[d]} for d in day_keys]
  return success(data=final_data, message='获取成功')


@kun_admin_bp.route('/user', methods=['GET'])
@token_required
def admin_user_list(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  page = request.args.get('page', 1, type=int)
  limit = request.args.get('limit', 20, type=int)
  offset = (page - 1) * limit

  q = User.query.order_by(User.created.desc())
  total = q.count()
  data = q.offset(offset).limit(limit).all()

  users = [{
    'id': u.id,
    'name': u.name,
    'avatar': u.avatar,
    'created': u.created.isoformat() if u.created else None,
    'status': u.status
  } for u in data]

  return success(data={'users': users, 'totalCount': total}, message='获取成功')


@kun_admin_bp.route('/user/search', methods=['GET'])
@token_required
def admin_user_search(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  q = request.args.get('q', '', type=str)
  data = User.query.filter(User.name.like(f'%{q}%')).limit(50).all()
  users = [{
    'id': u.id,
    'name': u.name,
    'avatar': u.avatar,
    'created': u.created.isoformat() if u.created else None,
    'status': u.status
  } for u in data]
  return success(data=users, message='获取成功')
