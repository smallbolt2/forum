"""
话题互动：点赞 / 点踩 / 收藏 / 推（对齐 Nitro server/api/topic/*）
"""

from datetime import datetime

from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.user import User
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.prisma_topic_extras import (
  TopicLike,
  TopicDislike,
  TopicFavorite,
  TopicUpvote,
  TopicReplyLike,
  TopicReplyDislike,
  TopicComment,
  TopicCommentLike,
)
from app.utils.kun_message_util import create_dedup_message


def _snippet(text: str | None, limit: int = 233) -> str:
  return (text or '').replace('\n', ' ')[:limit]


def _topic_for_reaction(topic_id: int) -> Topic | None:
  topic = Topic.query.get(topic_id)
  if not topic or topic.status in (1, 2):
    return None
  return topic


def _adjust_moemoepoint(user_id: int, delta: int) -> None:
  if not delta:
    return
  user = User.query.get(user_id)
  if user:
    user.moemoepoint = (user.moemoepoint or 0) + delta


def toggle_topic_like(uid: int, topic_id: int) -> str:
  topic = _topic_for_reaction(topic_id)
  if not topic:
    raise ValueError('未找到该话题')
  if topic.user_id == uid:
    raise ValueError('您不能给自己点赞')

  existing = TopicLike.query.filter_by(topic_id=topic_id, user_id=uid).first()
  if existing:
    db.session.delete(existing)
    _adjust_moemoepoint(topic.user_id, -1)
  else:
    db.session.add(TopicLike(topic_id=topic_id, user_id=uid))
    _adjust_moemoepoint(topic.user_id, 1)
    create_dedup_message(
      uid, topic.user_id, 'liked', _snippet(topic.content), topic_id=topic_id
    )
  db.session.commit()
  return 'MOEMOE like topic successfully!'


def toggle_topic_dislike(uid: int, topic_id: int) -> str:
  topic = _topic_for_reaction(topic_id)
  if not topic:
    raise ValueError('未找到该话题')
  if topic.user_id == uid:
    raise ValueError('您不能给自己点踩')

  existing = TopicDislike.query.filter_by(topic_id=topic_id, user_id=uid).first()
  if existing:
    db.session.delete(existing)
  else:
    db.session.add(TopicDislike(topic_id=topic_id, user_id=uid))
  db.session.commit()
  return 'MOEMOE dislike topic successfully!'


def toggle_topic_favorite(uid: int, topic_id: int) -> str:
  topic = _topic_for_reaction(topic_id)
  if not topic:
    raise ValueError('未找到该话题')

  existing = TopicFavorite.query.filter_by(topic_id=topic_id, user_id=uid).first()
  if existing:
    db.session.delete(existing)
    if topic.user_id != uid:
      _adjust_moemoepoint(topic.user_id, -1)
  else:
    db.session.add(TopicFavorite(topic_id=topic_id, user_id=uid))
    if topic.user_id != uid:
      _adjust_moemoepoint(topic.user_id, 1)
      create_dedup_message(
        uid,
        topic.user_id,
        'favorite',
        _snippet(topic.content),
        topic_id=topic_id,
      )
  db.session.commit()
  return 'MOEMOE favorite topic successfully!'


def upvote_topic(uid: int, topic_id: int) -> str:
  topic = _topic_for_reaction(topic_id)
  if not topic:
    raise ValueError('未找到该话题')
  if topic.user_id == uid:
    raise ValueError('您不能推自己的话题')

  now = datetime.utcnow()
  db.session.add(TopicUpvote(topic_id=topic_id, user_id=uid))
  topic.status_update_time = now
  topic.upvote_time = now
  _adjust_moemoepoint(topic.user_id, 3)
  _adjust_moemoepoint(uid, -7)
  create_dedup_message(
    uid, topic.user_id, 'upvoted', _snippet(topic.content), topic_id=topic_id
  )
  db.session.commit()
  return 'MOEMOE upvoted topic successfully!'


def toggle_reply_like(uid: int, reply_id: int) -> str:
  reply = TopicReply.query.get(reply_id)
  if not reply:
    raise ValueError('未找到该回复')
  if reply.user_id == uid:
    raise ValueError('您不能给自己点赞')

  existing = TopicReplyLike.query.filter_by(
    topic_reply_id=reply_id, user_id=uid
  ).first()
  if existing:
    db.session.delete(existing)
    _adjust_moemoepoint(reply.user_id, -1)
  else:
    db.session.add(TopicReplyLike(topic_reply_id=reply_id, user_id=uid))
    _adjust_moemoepoint(reply.user_id, 1)
    create_dedup_message(
      uid,
      reply.user_id,
      'liked',
      _snippet(reply.content),
      topic_id=reply.topic_id,
    )
  db.session.commit()
  return 'MOEMOE like reply successfully!'


def toggle_reply_dislike(uid: int, reply_id: int) -> str:
  reply = TopicReply.query.get(reply_id)
  if not reply:
    raise ValueError('未找到该回复')
  if reply.user_id == uid:
    raise ValueError('您不能给自己点踩')

  existing = TopicReplyDislike.query.filter_by(
    topic_reply_id=reply_id, user_id=uid
  ).first()
  if existing:
    db.session.delete(existing)
  else:
    db.session.add(TopicReplyDislike(topic_reply_id=reply_id, user_id=uid))
  db.session.commit()
  return 'MOEMOE dislike reply successfully!'


def toggle_comment_like(uid: int, comment_id: int) -> str:
  comment = TopicComment.query.get(comment_id)
  if not comment:
    raise ValueError('未找到该评论')
  if comment.user_id == uid:
    raise ValueError('您不能给自己的评论点赞')

  existing = TopicCommentLike.query.filter_by(
    topic_comment_id=comment_id, user_id=uid
  ).first()
  if existing:
    db.session.delete(existing)
    _adjust_moemoepoint(comment.user_id, -1)
  else:
    db.session.add(TopicCommentLike(topic_comment_id=comment_id, user_id=uid))
    _adjust_moemoepoint(comment.user_id, 1)
    create_dedup_message(
      uid,
      comment.user_id,
      'liked',
      _snippet(comment.content),
      topic_id=comment.topic_id,
    )
  db.session.commit()
  return 'MOEMOE like comment successfully!'
