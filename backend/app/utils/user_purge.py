"""
永久删除用户前清理关联数据（按当前库中实际存在的表执行，避免查询不存在的表）。
"""

from __future__ import annotations

from sqlalchemy import inspect, text

from app import db
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
  TopicReplyTarget,
  TopicTag,
  TopicSectionRelation,
)

_db_tables: set[str] | None = None


def _existing_tables() -> set[str]:
  global _db_tables
  if _db_tables is None:
    _db_tables = set(inspect(db.engine).get_table_names())
  return _db_tables


def _sql_delete(table: str, where_sql: str, params: dict) -> None:
  if table not in _existing_tables():
    return
  db.session.execute(text(f'DELETE FROM [{table}] WHERE {where_sql}'), params)


def _delete_single_reply_graph(reply_id: int) -> None:
  TopicReplyTarget.query.filter(
    (TopicReplyTarget.reply_id == reply_id)
    | (TopicReplyTarget.target_reply_id == reply_id)
  ).delete(synchronize_session=False)
  TopicReplyLike.query.filter_by(topic_reply_id=reply_id).delete()
  TopicReplyDislike.query.filter_by(topic_reply_id=reply_id).delete()
  rep = TopicReply.query.get(reply_id)
  if rep:
    db.session.delete(rep)


def _delete_topic_fully(topic_id: int) -> None:
  rids = [r.id for r in TopicReply.query.filter_by(topic_id=topic_id).all()]
  if rids:
    Topic.query.filter(Topic.best_answer_id.in_(rids)).update(
      {Topic.best_answer_id: None}, synchronize_session=False
    )
    Topic.query.filter(Topic.pinned_reply_id.in_(rids)).update(
      {Topic.pinned_reply_id: None}, synchronize_session=False
    )
  for rid in rids:
    _delete_single_reply_graph(rid)
  cids = [c.id for c in TopicComment.query.filter_by(topic_id=topic_id).all()]
  for cid in cids:
    TopicCommentLike.query.filter_by(topic_comment_id=cid).delete()
  TopicComment.query.filter_by(topic_id=topic_id).delete()
  if 'topic_tag' in _existing_tables():
    TopicTag.query.filter_by(topic_id=topic_id).delete()
  if 'topic_section_relation' in _existing_tables():
    TopicSectionRelation.query.filter_by(topic_id=topic_id).delete()
  TopicLike.query.filter_by(topic_id=topic_id).delete()
  TopicDislike.query.filter_by(topic_id=topic_id).delete()
  TopicFavorite.query.filter_by(topic_id=topic_id).delete()
  TopicUpvote.query.filter_by(topic_id=topic_id).delete()
  top = Topic.query.get(topic_id)
  if top:
    db.session.delete(top)


def _purge_user_topics(user_id: int) -> None:
  for topic in list(Topic.query.filter_by(user_id=user_id).all()):
    _delete_topic_fully(topic.id)
  for reply in list(TopicReply.query.filter_by(user_id=user_id).all()):
    _delete_single_reply_graph(reply.id)
  for c in list(TopicComment.query.filter_by(user_id=user_id).all()):
    TopicCommentLike.query.filter_by(topic_comment_id=c.id).delete()
    db.session.delete(c)
  TopicComment.query.filter_by(target_user_id=user_id).delete()
  TopicLike.query.filter_by(user_id=user_id).delete()
  TopicDislike.query.filter_by(user_id=user_id).delete()
  TopicFavorite.query.filter_by(user_id=user_id).delete()
  TopicUpvote.query.filter_by(user_id=user_id).delete()
  TopicReplyLike.query.filter_by(user_id=user_id).delete()
  TopicReplyDislike.query.filter_by(user_id=user_id).delete()
  TopicCommentLike.query.filter_by(user_id=user_id).delete()
  _sql_delete('topic_poll_vote', 'user_id = :uid', {'uid': user_id})
  _sql_delete('topic_poll', 'user_id = :uid', {'uid': user_id})


def _purge_user_toolsets(user_id: int) -> None:
  if 'galgame_toolset' not in _existing_tables():
    return

  from app.models.prisma_toolset_min import (
    GalgameToolset,
    GalgameToolsetAlias,
    GalgameToolsetResource,
    GalgameToolsetComment,
    GalgameToolsetPracticality,
  )

  GalgameToolsetPracticality.query.filter_by(user_id=user_id).delete()
  GalgameToolsetResource.query.filter_by(user_id=user_id).delete()
  GalgameToolsetComment.query.filter_by(user_id=user_id).delete()
  _sql_delete('galgame_toolset_contributor', 'user_id = :uid', {'uid': user_id})

  for ts in list(GalgameToolset.query.filter_by(user_id=user_id).all()):
    tid = ts.id
    if 'galgame_toolset_alias' in _existing_tables():
      GalgameToolsetAlias.query.filter_by(toolset_id=tid).delete()
    _sql_delete('galgame_toolset_category_relation', 'toolset_id = :tid', {'tid': tid})
    GalgameToolsetResource.query.filter_by(toolset_id=tid).delete()
    while True:
      n = GalgameToolsetComment.query.filter(
        GalgameToolsetComment.toolset_id == tid,
        GalgameToolsetComment.parent_id.isnot(None),
      ).delete(synchronize_session=False)
      if not n:
        break
    GalgameToolsetComment.query.filter_by(toolset_id=tid).delete()
    GalgameToolsetPracticality.query.filter_by(toolset_id=tid).delete()
    _sql_delete('galgame_toolset_contributor', 'toolset_id = :tid', {'tid': tid})
    db.session.delete(ts)


def _purge_user_galgame(user_id: int) -> None:
  if 'galgame' not in _existing_tables():
    return

  from app.models.prisma_galgame_min import (
    Galgame,
    GalgameLike,
    GalgameFavorite,
    GalgameResource,
  )

  GalgameLike.query.filter_by(user_id=user_id).delete()
  GalgameFavorite.query.filter_by(user_id=user_id).delete()
  GalgameResource.query.filter_by(user_id=user_id).delete()
  _sql_delete('galgame_comment_like', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_comment', 'user_id = :uid OR target_user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_contributor', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_history', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_link', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_rating_like', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_rating_comment', 'user_id = :uid OR target_user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_rating', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_resource_like', 'user_id = :uid', {'uid': user_id})
  _sql_delete('galgame_pr', 'user_id = :uid', {'uid': user_id})

  for g in list(Galgame.query.filter_by(user_id=user_id).all()):
    gid = g.id
    _sql_delete('galgame_resource', 'galgame_id = :gid', {'gid': gid})
    _sql_delete('galgame_like', 'galgame_id = :gid', {'gid': gid})
    _sql_delete('galgame_favorite', 'galgame_id = :gid', {'gid': gid})
    db.session.delete(g)


def _purge_user_chat_and_misc(user_id: int) -> None:
  """与 Nitro permanent.delete 一致：聊天表为 NoAction，需先删。"""
  _sql_delete('chat_message_read_by', 'user_id = :uid', {'uid': user_id})
  _sql_delete('chat_message_reaction', 'user_id = :uid', {'uid': user_id})
  _sql_delete(
    'chat_message',
    'sender_id = :uid OR receiver_id = :uid',
    {'uid': user_id},
  )
  _sql_delete('chat_room_admin', 'user_id = :uid', {'uid': user_id})
  _sql_delete('chat_room_participant', 'user_id = :uid', {'uid': user_id})
  _sql_delete(
    'message',
    'sender_id = :uid OR receiver_id = :uid',
    {'uid': user_id},
  )
  _sql_delete('system_message', 'user_id = :uid', {'uid': user_id})
  _sql_delete(
    'user_friend',
    'user_id = :uid OR friend_id = :uid',
    {'uid': user_id},
  )
  _sql_delete(
    'user_follow',
    'follower_id = :uid OR followed_id = :uid',
    {'uid': user_id},
  )
  _sql_delete('unmoe', 'user_id = :uid', {'uid': user_id})
  _sql_delete('update_log', 'user_id = :uid', {'uid': user_id})
  _sql_delete('todo', 'user_id = :uid', {'uid': user_id})

  if 'doc_article' in _existing_tables():
    if 'doc_article_tag_relation' in _existing_tables():
      _sql_delete(
        'doc_article_tag_relation',
        'doc_article_id IN (SELECT id FROM doc_article WHERE author_id = :uid)',
        {'uid': user_id},
      )
    _sql_delete('doc_article', 'author_id = :uid', {'uid': user_id})


def purge_user_for_permanent_delete(user_id: int) -> None:
  """删除 user 行之前调用；不 commit。"""
  global _db_tables
  _db_tables = None
  _purge_user_topics(user_id)
  _purge_user_toolsets(user_id)
  _purge_user_galgame(user_id)
  _purge_user_chat_and_misc(user_id)
