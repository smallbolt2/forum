"""
删除话题回复（含引用链上的子回复），对齐 Nitro deleteTopicRepliesRecursive。
"""

from __future__ import annotations

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.prisma_topic_extras import (
  TopicReplyTarget,
  TopicReplyLike,
  TopicReplyDislike,
  TopicComment,
  TopicCommentLike,
)


def collect_topic_reply_cascade_ids(root_reply_ids: list[int]) -> set[int]:
  unique_roots = {int(i) for i in root_reply_ids if i is not None}
  if not unique_roots:
    return set()

  ids_to_delete = set(unique_roots)
  queue = list(unique_roots)

  while queue:
    child_rows = (
      db.session.query(TopicReply.id)
      .join(TopicReplyTarget, TopicReplyTarget.reply_id == TopicReply.id)
      .filter(TopicReplyTarget.target_reply_id.in_(queue))
      .distinct()
      .all()
    )
    queue = []
    for (rid,) in child_rows:
      if rid not in ids_to_delete:
        ids_to_delete.add(rid)
        queue.append(rid)

  return ids_to_delete


def _delete_reply_row(reply_id: int) -> None:
  cids = [
    c.id
    for c in TopicComment.query.filter_by(topic_reply_id=reply_id).all()
  ]
  for cid in cids:
    TopicCommentLike.query.filter_by(topic_comment_id=cid).delete()
  TopicComment.query.filter_by(topic_reply_id=reply_id).delete()

  TopicReplyTarget.query.filter(
    (TopicReplyTarget.reply_id == reply_id)
    | (TopicReplyTarget.target_reply_id == reply_id)
  ).delete(synchronize_session=False)
  TopicReplyLike.query.filter_by(topic_reply_id=reply_id).delete()
  TopicReplyDislike.query.filter_by(topic_reply_id=reply_id).delete()

  rep = TopicReply.query.get(reply_id)
  if rep:
    db.session.delete(rep)


def delete_topic_replies_recursive(root_reply_ids: list[int]) -> set[int]:
  ids_to_delete = collect_topic_reply_cascade_ids(root_reply_ids)
  if not ids_to_delete:
    return ids_to_delete

  id_list = list(ids_to_delete)
  Topic.query.filter(Topic.best_answer_id.in_(id_list)).update(
    {Topic.best_answer_id: None}, synchronize_session=False
  )
  Topic.query.filter(Topic.pinned_reply_id.in_(id_list)).update(
    {Topic.pinned_reply_id: None}, synchronize_session=False
  )

  for rid in id_list:
    _delete_reply_row(rid)

  return ids_to_delete


def moemoepoint_cost_for_reply_delete(reply_id: int) -> int:
  """与 Nitro index.delete.ts 中 moemoepointToDecreaseIfUserDelete 一致。"""
  comment_count = TopicComment.query.filter_by(topic_reply_id=reply_id).count()
  like_count = TopicReplyLike.query.filter_by(topic_reply_id=reply_id).count()
  target_count = TopicReplyTarget.query.filter_by(reply_id=reply_id).count()
  target_by_count = TopicReplyTarget.query.filter_by(target_reply_id=reply_id).count()
  return 3 * (comment_count + like_count + target_count + target_by_count + 1)
