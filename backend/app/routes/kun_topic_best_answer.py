"""
Nuxt/Nitro 兼容：设置最佳答案

PUT /api/topic/<tid>/best-answer
"""

from flask import Blueprint, request, jsonify
from datetime import datetime

from app import db
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.user import User
from app.utils.auth import token_required
from app.utils.response import error


kun_topic_best_answer_bp = Blueprint('kun_topic_best_answer', __name__)


@kun_topic_best_answer_bp.route('/<int:topic_id>/best-answer', methods=['PUT'])
@token_required
def set_best_answer(topic_id, current_user=None):
  try:
    data = request.get_json() or {}
    reply_id = data.get('replyId') or data.get('reply_id')
    if not reply_id:
      return error('缺少 replyId', code=400, http_status=400)

    topic = Topic.query.get(topic_id)
    if not topic or topic.status == 1:
      return error('未找到该话题', code=404, http_status=404)

    # only topic author or admin
    if topic.user_id != current_user.id and current_user.role != 'admin':
      return error('您无权将该回复设置为最佳答案', code=403, http_status=403)

    reply = TopicReply.query.get(int(reply_id))
    if not reply or reply.topic_id != topic_id:
      return error('未找到该回复', code=404, http_status=404)

    # toggle
    is_unset = topic.best_answer_id == reply.id
    topic.best_answer_id = None if is_unset else reply.id
    topic.status_update_time = datetime.utcnow()

    # moemoepoint +/- 7
    target_user = User.query.get(reply.user_id)
    if target_user:
      target_user.moemoepoint = (target_user.moemoepoint or 0) + (-7 if is_unset else 7)

    db.session.commit()
    return jsonify('MOEMOE set best answer successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)

