"""
论坛通知消息（message 表），对齐 server/utils/message.ts
"""

from __future__ import annotations

from app import db
from app.models.prisma_message import Message


def _build_link(
  topic_id: int | None = None,
  galgame_id: int | None = None,
  toolset_id: int | None = None,
  website_domain: str | None = None,
) -> str:
  if topic_id:
    return f'/topic/{topic_id}'
  if galgame_id:
    return f'/galgame/{galgame_id}'
  if toolset_id:
    return f'/toolset/{toolset_id}'
  if website_domain:
    return f'/website/{website_domain}'
  return ''


def generate_room_id(uid1: int, uid2: int) -> str:
  a, b = sorted([int(uid1), int(uid2)])
  return f'{a}-{b}'


def create_message(
  sender_id: int,
  receiver_id: int,
  msg_type: str,
  content: str,
  topic_id: int | None = None,
  galgame_id: int | None = None,
  toolset_id: int | None = None,
  website_domain: str | None = None,
) -> Message:
  link = _build_link(topic_id, galgame_id, toolset_id, website_domain)
  row = Message(
    sender_id=sender_id,
    receiver_id=receiver_id,
    type=msg_type,
    content=(content or '')[:233],
    link=link[:100],
    status='unread',
  )
  db.session.add(row)
  return row


def create_dedup_message(
  sender_id: int,
  receiver_id: int,
  msg_type: str,
  content: str,
  topic_id: int | None = None,
  galgame_id: int | None = None,
  toolset_id: int | None = None,
) -> Message | None:
  link = _build_link(topic_id, galgame_id, toolset_id)
  snippet = (content or '')[:233]
  existing = Message.query.filter_by(
    sender_id=sender_id,
    receiver_id=receiver_id,
    type=msg_type,
    content=snippet,
    link=link[:100],
  ).first()
  if existing:
    return None
  return create_message(
    sender_id,
    receiver_id,
    msg_type,
    snippet,
    topic_id=topic_id,
    galgame_id=galgame_id,
    toolset_id=toolset_id,
  )
