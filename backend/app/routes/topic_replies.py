"""话题回复路由"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.topic_reply import TopicReply
from app.models.topic import Topic
from app.utils.auth import token_required
from datetime import datetime

topic_reply_bp = Blueprint('topic_replies', __name__)


def build_reply_tree(replies):
    """根据 parent_id 构建回复树"""
    replies_by_id = {r.id: r for r in replies}
    root = []

    for reply in replies:
        if reply.parent_id and reply.parent_id in replies_by_id:
            parent = replies_by_id[reply.parent_id]
            # 确保父节点已经包含 replies 列表
            if not hasattr(parent, 'children_cache'):
                parent.children_cache = []
            parent.children_cache.append(reply)
        else:
            root.append(reply)

    # 将缓存字段转化为 to_dict 结构
    def to_dict_with_children(r, floor=None):
        data = r.to_dict()
        # Ensure tree building logic is authoritative (avoid duplicate nested replies)
        data.pop('replies', None)
        if floor is not None:
            data['floor'] = floor
        children = getattr(r, 'children_cache', [])
        if children:
            data['replies'] = [to_dict_with_children(c) for c in children]
        return data

    return [to_dict_with_children(r, floor=idx + 1) for idx, r in enumerate(root)]


@topic_reply_bp.route('', methods=['GET'])
def get_topic_replies():
    """获取话题回复列表"""
    try:
        topic_id = request.args.get('topic_id', type=int)
        if not topic_id:
            return jsonify({'code': 400, 'message': '缺少 topic_id 参数'}), 400

        topic = Topic.query.get_or_404(topic_id)
        if topic.status == 2:
            return jsonify({'code': 404, 'message': '话题不存在'}), 404

        replies = TopicReply.query.filter_by(topic_id=topic_id, status=1).order_by(TopicReply.created_at.asc()).all()
        return jsonify({'code': 200, 'message': '获取成功', 'data': build_reply_tree(replies)})
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_reply_bp.route('', methods=['POST'])
@token_required
def create_topic_reply(current_user=None):
    """创建话题回复"""
    try:
        data = request.get_json() or {}
        topic_id = data.get('topic_id')
        content = data.get('content', '').strip()
        parent_id = data.get('parent_id')

        if not topic_id:
            return jsonify({'code': 400, 'message': '缺少 topic_id'}), 400
        if not content:
            return jsonify({'code': 400, 'message': '回复内容不能为空'}), 400

        topic = Topic.query.get_or_404(topic_id)
        if topic.status == 2:
            return jsonify({'code': 404, 'message': '话题不存在'}), 404

        reply = TopicReply(
            topic_id=topic_id,
            user_id=current_user.id,
            content=content,
            parent_id=parent_id if parent_id else None,
            status=1,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )

        db.session.add(reply)
        db.session.commit()

        return jsonify({'code': 200, 'message': '回复成功', 'data': reply.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_reply_bp.route('', methods=['PUT'])
@token_required
def update_topic_reply(current_user=None):
    """更新话题回复"""
    try:
        data = request.get_json() or {}
        reply_id = data.get('reply_id')
        content = data.get('content', '').strip()

        if not reply_id:
            return jsonify({'code': 400, 'message': '缺少 reply_id'}), 400
        if not content:
            return jsonify({'code': 400, 'message': '回复内容不能为空'}), 400

        reply = TopicReply.query.get(reply_id)
        if not reply or reply.status == 2:
            return jsonify({'code': 404, 'message': '回复不存在'}), 404

        if reply.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限编辑回复'}), 403

        reply.content = content
        reply.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'code': 200, 'message': '更新成功', 'data': reply.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_reply_bp.route('', methods=['DELETE'])
@token_required
def delete_topic_reply(current_user=None):
    """删除话题回复（软删除）"""
    try:
        reply_id = request.args.get('reply_id', type=int)
        if not reply_id:
            return jsonify({'code': 400, 'message': '缺少 reply_id 参数'}), 400

        reply = TopicReply.query.get(reply_id)
        if not reply or reply.status == 2:
            return jsonify({'code': 404, 'message': '回复不存在'}), 404

        if reply.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限删除回复'}), 403

        reply.status = 2
        db.session.commit()

        return jsonify({'code': 200, 'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
