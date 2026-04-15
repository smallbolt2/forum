"""话题（Topic）路由"""

from flask import Blueprint, request, jsonify
from app import db
from app.models.topic import Topic
from app.utils.auth import token_required
from datetime import datetime

topic_bp = Blueprint('topics', __name__)


@topic_bp.route('', methods=['GET'])
def get_topics():
    """获取话题列表（支持分页/筛选/搜索）"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        author_id = request.args.get('author_id', type=int)
        keyword = request.args.get('keyword', type=str)
        status = request.args.get('status', None, type=int)

        query = Topic.query

        # 默认只展示非删除状态
        if status is None:
            query = query.filter(Topic.status != 2)
        else:
            query = query.filter_by(status=status)

        if author_id:
            query = query.filter_by(user_id=author_id)

        if keyword:
            query = query.filter(
                db.or_(
                    Topic.title.like(f'%{keyword}%'),
                    Topic.content.like(f'%{keyword}%')
                )
            )

        query = query.order_by(Topic.created.desc())

        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        topics = pagination.items

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'topics': [topic.to_dict() for topic in topics],
                'pagination': {
                    'page': page,
                    'per_page': per_page,
                    'total': pagination.total,
                    'pages': pagination.pages
                }
            }
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_bp.route('/<int:topic_id>', methods=['GET'])
def get_topic(topic_id):
    """获取话题详情（增加浏览量）"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        if topic.status == 2:
            return jsonify({'code': 404, 'message': '话题不存在'}), 404

        # 增加浏览量
        topic.view = (topic.view or 0) + 1
        db.session.commit()

        return jsonify({'code': 200, 'message': '获取成功', 'data': topic.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_bp.route('', methods=['POST'])
@token_required
def create_topic(current_user=None):
    """创建话题"""
    try:
        data = request.get_json() or {}
        title = data.get('title')
        content = data.get('content')
        category = data.get('category')
        # 兼容前端传递的多种字段
        if not category:
            category = data.get('category_id') or data.get('category_name')
        is_nsfw = bool(data.get('is_nsfw', False))
        status = data.get('status', 1)

        if not title:
            return jsonify({'code': 400, 'message': '标题不能为空'}), 400
        if not content:
            return jsonify({'code': 400, 'message': '内容不能为空'}), 400
        if not category:
            return jsonify({'code': 400, 'message': '请填写分类/标签'}), 400

        topic = Topic(
            title=title,
            content=content,
            category=category if isinstance(category, str) else str(category),
            is_nsfw=is_nsfw,
            status=status,
            user_id=current_user.id
        )

        db.session.add(topic)
        db.session.commit()

        return jsonify({'code': 200, 'message': '创建成功', 'data': topic.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_bp.route('/<int:topic_id>', methods=['PUT'])
@token_required
def update_topic(topic_id, current_user=None):
    """更新话题"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        if topic.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权编辑此话题'}), 403

        data = request.get_json() or {}
        topic.title = data.get('title', topic.title)
        topic.content = data.get('content', topic.content)
        if data.get('category') is not None:
            topic.category = data.get('category')
        topic.is_nsfw = bool(data.get('is_nsfw', topic.is_nsfw))
        topic.status = data.get('status', topic.status)
        topic.updated = datetime.utcnow()

        db.session.commit()

        return jsonify({'code': 200, 'message': '更新成功', 'data': topic.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@topic_bp.route('/<int:topic_id>', methods=['DELETE'])
@token_required
def delete_topic(topic_id, current_user=None):
    """删除话题（软删除）"""
    try:
        topic = Topic.query.get_or_404(topic_id)
        if topic.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权删除此话题'}), 403

        topic.status = 2
        db.session.commit()

        return jsonify({'code': 200, 'message': '删除成功'})
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
