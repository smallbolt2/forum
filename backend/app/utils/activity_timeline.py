"""
全站动态时间线（对齐 server/utils/activityTimeline.ts）
"""

import json
import re
from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.user import User
from app.models.prisma_topic_extras import TopicComment, TopicReplyTarget
from app.models.prisma_toolset_min import GalgameToolset

_MD_STRIP = re.compile(r'[#*`\[\]()>_~\-]')


def _strip_markdown(text: str) -> str:
  if not text:
    return ''
  return _MD_STRIP.sub('', text).strip()


def _iso(dt) -> str | None:
  if not dt:
    return None
  if isinstance(dt, datetime):
    return dt.isoformat()
  return str(dt)


def _actor(user_id: int, cache: dict) -> dict:
  if user_id not in cache:
    u = User.query.get(user_id)
    cache[user_id] = {
      'id': user_id,
      'name': u.name if u else '',
      'avatar': u.avatar if u else '',
    }
  return cache[user_id]


def _topic_sfw_filter(is_sfw: bool):
  q = Topic.status != 1
  if is_sfw:
    q = db.and_(q, Topic.is_nsfw == False)  # noqa: E712
  return q


def _fetch_topic_creation(take: int, is_sfw: bool, user_cache: dict) -> tuple[list, int]:
  q = Topic.query.filter(_topic_sfw_filter(is_sfw))
  total = q.count()
  rows = q.order_by(Topic.created.desc()).limit(take).all()
  items = [{
    'uniqueId': f'topic-{t.id}',
    'type': 'TOPIC_CREATION',
    'timestamp': _iso(t.created),
    'actor': _actor(t.user_id, user_cache),
    'link': f'/topic/{t.id}',
    'content': t.title or '',
  } for t in rows]
  return items, total


def _fetch_topic_reply_creation(take: int, is_sfw: bool, user_cache: dict) -> tuple[list, int]:
  q = TopicReply.query
  if is_sfw:
    q = q.join(Topic, Topic.id == TopicReply.topic_id).filter(
      Topic.is_nsfw == False  # noqa: E712
    )
  total = q.count()
  rows = q.order_by(TopicReply.created.desc()).limit(take).all()

  items = []
  for r in rows:
    content = _strip_markdown(r.content or '')[:100]
    try:
      targets = TopicReplyTarget.query.filter_by(reply_id=r.id).all()
      for t in targets:
        content += _strip_markdown(t.content or '')
      content = content[:100]
    except SQLAlchemyError:
      db.session.rollback()

    items.append({
      'uniqueId': f'topic-reply-{r.id}',
      'type': 'TOPIC_REPLY_CREATION',
      'timestamp': _iso(r.created),
      'actor': _actor(r.user_id, user_cache),
      'link': f'/topic/{r.topic_id}',
      'content': content,
    })
  return items, total


def _fetch_topic_comment_creation(take: int, is_sfw: bool, user_cache: dict) -> tuple[list, int]:
  q = TopicComment.query
  if is_sfw:
    q = q.join(Topic, Topic.id == TopicComment.topic_id).filter(
      Topic.is_nsfw == False  # noqa: E712
    )
  total = q.count()
  rows = q.order_by(TopicComment.created.desc()).limit(take).all()
  items = [{
    'uniqueId': f'topic-comment-{c.id}',
    'type': 'TOPIC_COMMENT_CREATION',
    'timestamp': _iso(c.created),
    'actor': _actor(c.user_id, user_cache),
    'link': f'/topic/{c.topic_id}',
    'content': (c.content or '')[:100],
  } for c in rows]
  return items, total


def _fetch_toolset_creation(take: int, user_cache: dict) -> tuple[list, int]:
  try:
    q = GalgameToolset.query.filter(GalgameToolset.status != 1)
    total = q.count()
    rows = q.order_by(GalgameToolset.created.desc()).limit(take).all()
    items = [{
      'uniqueId': f'toolset-{t.id}',
      'type': 'TOOLSET_CREATION',
      'timestamp': _iso(t.created),
      'actor': _actor(t.user_id, user_cache),
      'link': f'/toolset/{t.id}',
      'content': (t.name or '')[:100],
    } for t in rows]
    return items, total
  except SQLAlchemyError:
    db.session.rollback()
    return [], 0


def _safe_table_fetch(
  table: str,
  type_name: str,
  link_tpl: str,
  content_col: str,
  take: int,
  user_cache: dict,
  *,
  extra_where: str = '',
  content_fn=None,
) -> tuple[list, int]:
  """通用 raw SQL 拉取（表不存在则返回空）"""
  from sqlalchemy import text

  where = f'WHERE 1=1 {extra_where}' if extra_where else ''
  try:
    total_row = db.session.execute(
      text(f'SELECT COUNT(*) FROM [{table}] {where}')
    ).first()
    total = int(total_row[0]) if total_row else 0

    rows = db.session.execute(
      text(f'''
        SELECT TOP (:take) id, [{content_col}] AS content, created, user_id
        FROM [{table}]
        {where}
        ORDER BY [created] DESC
      '''),
      {'take': take},
    ).fetchall()

    items = []
    for row in rows:
      rid, content, created, uid = row[0], row[1], row[2], row[3]
      body = content_fn(content) if content_fn else (content or '')
      if isinstance(body, str):
        body = body[:100]
      items.append({
        'uniqueId': f'{table}-{rid}',
        'type': type_name,
        'timestamp': _iso(created),
        'actor': _actor(int(uid), user_cache),
        'link': link_tpl.format(id=rid),
        'content': body,
      })
    return items, total
  except SQLAlchemyError:
    db.session.rollback()
    return [], 0


def _fetch_update_log(take: int, user_cache: dict) -> tuple[list, int]:
  return _safe_table_fetch(
    'update_log',
    'UPDATE_LOG_CREATION',
    '/update/history',
    'content_zh_cn',
    take,
    user_cache,
    content_fn=lambda c: (c or '')[:100],
  )


def _fetch_todo(take: int, user_cache: dict) -> tuple[list, int]:
  def _todo_content(raw):
    if not raw:
      return ''
    try:
      data = json.loads(raw) if isinstance(raw, str) else raw
      if isinstance(data, dict):
        return (data.get('zh-cn') or data.get('zh_cn') or next(iter(data.values()), ''))[:100]
    except (json.JSONDecodeError, TypeError):
      pass
    return str(raw)[:100]

  return _safe_table_fetch(
    'todo',
    'TODO_CREATION',
    '/update/todo',
    'content_zh_cn',
    take,
    user_cache,
    content_fn=_todo_content,
  )


def _fetch_message(msg_type: str, activity_type: str, take: int, user_cache: dict) -> tuple[list, int]:
  from sqlalchemy import text

  try:
    total_row = db.session.execute(
      text('SELECT COUNT(*) FROM [message] WHERE [type] = :t'),
      {'t': msg_type},
    ).first()
    total = int(total_row[0]) if total_row else 0

    rows = db.session.execute(
      text('''
        SELECT TOP (:take) id, content, link, created, sender_id
        FROM [message]
        WHERE [type] = :t
        ORDER BY [created] DESC
      '''),
      {'take': take, 't': msg_type},
    ).fetchall()

    items = []
    for row in rows:
      mid, content, link, created, sender_id = row
      body = _strip_markdown(content or '')[:100]
      items.append({
        'uniqueId': f'message-{mid}',
        'type': activity_type,
        'timestamp': _iso(created),
        'actor': _actor(int(sender_id), user_cache),
        'link': link or '/',
        'content': body,
      })
    return items, total
  except SQLAlchemyError:
    db.session.rollback()
    return [], 0


def get_activity_timeline_data(page: int, limit: int, is_sfw: bool = False) -> dict:
  page = max(1, min(page, 9999999))
  limit = max(1, min(limit, 50))
  skip = (page - 1) * limit
  take_window = skip + limit
  user_cache: dict = {}

  fetchers = [
    lambda: _fetch_topic_creation(take_window, is_sfw, user_cache),
    lambda: _fetch_topic_reply_creation(take_window, is_sfw, user_cache),
    lambda: _fetch_topic_comment_creation(take_window, is_sfw, user_cache),
    lambda: _fetch_toolset_creation(take_window, user_cache),
    lambda: _fetch_update_log(take_window, user_cache),
    lambda: _fetch_todo(take_window, user_cache),
    lambda: _fetch_message('upvoted', 'MESSAGE_UPVOTE', take_window, user_cache),
    lambda: _fetch_message('solution', 'MESSAGE_SOLUTION', take_window, user_cache),
  ]

  all_items = []
  total_count = 0

  for fn in fetchers:
    try:
      items, total = fn()
      all_items.extend(items)
      total_count += total
    except Exception:
      db.session.rollback()

  def _sort_key(item):
    ts = item.get('timestamp') or ''
    try:
      return datetime.fromisoformat(ts.replace('Z', '+00:00'))
    except ValueError:
      return datetime.min

  all_items.sort(key=_sort_key, reverse=True)
  paged = all_items[skip:skip + limit]

  return {'items': paged, 'totalCount': total_count}
