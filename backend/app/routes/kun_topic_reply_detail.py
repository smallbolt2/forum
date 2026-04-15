"""
Nuxt/Nitro 兼容：获取单条回复详情（用于引用跳转）

GET /api/topic/<tid>/reply/detail?replyId=123
"""

from flask import Blueprint, request, jsonify

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.user import User
from app.models.prisma_topic_extras import TopicReplyLike, TopicReplyDislike
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie
from app.utils.markdown_render import markdown_to_html
from app.utils.response import error


kun_topic_reply_detail_bp = Blueprint('kun_topic_reply_detail', __name__)


@kun_topic_reply_detail_bp.route('/<int:topic_id>/reply/detail', methods=['GET'])
def reply_detail(topic_id: int):
  try:
    reply_id = request.args.get('replyId', type=int)
    if not reply_id:
      return error('缺少 replyId', code=400, http_status=400)

    topic = Topic.query.get(topic_id)
    if not topic or topic.status == 1:
      return error('未找到该话题', code=404, http_status=404)

    reply = TopicReply.query.get(reply_id)
    if not reply or reply.topic_id != topic_id:
      return error('未找到该回复', code=404, http_status=404)

    uid = get_uid_from_refresh_cookie()

    u = User.query.get(reply.user_id)
    like_count = TopicReplyLike.query.filter_by(topic_reply_id=reply.id).count()
    dislike_count = TopicReplyDislike.query.filter_by(topic_reply_id=reply.id).count()
    is_liked = bool(uid and TopicReplyLike.query.filter_by(topic_reply_id=reply.id, user_id=uid).first())
    is_disliked = bool(uid and TopicReplyDislike.query.filter_by(topic_reply_id=reply.id, user_id=uid).first())

    result = {
      'id': reply.id,
      'topicId': reply.topic_id,
      'floor': reply.floor,
      'user': {
        'id': reply.user_id,
        'name': u.name if u else '',
        'avatar': u.avatar if u else '',
        'moemoepoint': u.moemoepoint if u else 0
      },
      'edited': reply.edited.isoformat() if reply.edited else None,
      'contentMarkdown': reply.content,
      'contentHtml': markdown_to_html(reply.content),
      'likeCount': like_count,
      'isLiked': is_liked,
      'dislikeCount': dislike_count,
      'isDisliked': is_disliked,
      'targetByCount': 0,
      'created': reply.created.isoformat() if reply.created else None,
      'targets': [],
      'isPinned': reply.id == topic.pinned_reply_id,
      'isBestAnswer': reply.id == topic.best_answer_id
    }

    return jsonify(result)
  except Exception as e:
    return error(str(e), code=500, http_status=500)

