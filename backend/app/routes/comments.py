"""
评论路由
"""
from datetime import datetime

from flask import Blueprint, request, jsonify
from app import db
from app.models.comment import Comment
from app.models.post import Post
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.utils.auth import token_required

comment_bp = Blueprint('comments', __name__)


def build_comment_tree(comments):
    """根据 parent_id 构建评论树（只返回根节点）"""
    comments_by_id = {c.id: c for c in comments}
    roots = []

    for comment in comments:
        if comment.parent_id and comment.parent_id in comments_by_id:
            parent = comments_by_id[comment.parent_id]
            if not hasattr(parent, 'children_cache'):
                parent.children_cache = []
            parent.children_cache.append(comment)
        else:
            roots.append(comment)

    def to_dict_with_children(c, floor=None):
        data = c.to_dict()
        data.pop('replies', None)
        if floor is not None:
            data['floor'] = floor
        children = getattr(c, 'children_cache', [])
        if children:
            data['replies'] = [to_dict_with_children(child) for child in children]
        return data

    return [to_dict_with_children(c, floor=idx + 1) for idx, c in enumerate(roots)]


@comment_bp.route('', methods=['GET'])
def get_comments():
    """获取评论列表"""
    try:
        post_id = request.args.get('post_id', type=int)
        status = request.args.get('status', 1, type=int)

        query = Comment.query.filter_by(status=status)
        if post_id:
            query = query.filter_by(post_id=post_id)

        comments = query.order_by(Comment.created_at.asc()).all()

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': build_comment_tree(comments)
        })
    except Exception as e:
        return jsonify({'code': 500, 'message': str(e)}), 500


@comment_bp.route('', methods=['POST'])
@token_required
def create_comment(current_user=None):
    """创建评论"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('content'):
            return jsonify({'code': 400, 'message': '评论内容不能为空'}), 400
        if not data.get('post_id'):
            return jsonify({'code': 400, 'message': '文章ID不能为空'}), 400

        # 验证文章是否存在，防止外键约束失败
        post_id = data.get('post_id')
        post = Post.query.get(post_id)

        # 如果是旧的 topic 表结构，则支持直接在 /api/comments 创建回复（兼容旧接口）
        if not post:
            topic = Topic.query.get(post_id)
            if topic:
                if topic.status == 2:
                    return jsonify({'code': 404, 'message': '话题不存在，无法回复'}), 404

                parent_id = data.get('parent_id')
                if parent_id:
                    if not TopicReply.query.get(parent_id):
                        return jsonify({'code': 404, 'message': '父回复不存在'}), 404

                reply = TopicReply(
                    topic_id=post_id,
                    user_id=current_user.id,
                    content=data.get('content'),
                    parent_id=parent_id,
                    status=data.get('status', 1)
                )
                db.session.add(reply)
                db.session.commit()
                return jsonify({
                    'code': 200,
                    'message': '创建成功',
                    'data': reply.to_dict()
                }), 201

            return jsonify({'code': 404, 'message': '文章不存在，无法发表评论'}), 404

        parent_id = data.get('parent_id')
        if parent_id:
            from app.models.comment import Comment as CommentModel
            if not CommentModel.query.get(parent_id):
                return jsonify({'code': 404, 'message': '父评论不存在'}), 404

        comment = Comment(
            content=data.get('content'),
            post_id=post_id,
            user_id=current_user.id,  # 使用当前登录用户
            parent_id=parent_id,
            status=data.get('status', 1)
        )
        db.session.add(comment)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': comment.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@comment_bp.route('', methods=['PUT'])
@token_required
def update_comment(current_user=None):
    """更新评论"""
    try:
        data = request.get_json() or {}
        comment_id = data.get('comment_id')
        content = (data.get('content') or '').strip()

        if not comment_id:
            return jsonify({'code': 400, 'message': '缺少 comment_id'}), 400
        if not content:
            return jsonify({'code': 400, 'message': '评论内容不能为空'}), 400

        comment = Comment.query.get(comment_id)
        if not comment or comment.status == 2:
            return jsonify({'code': 404, 'message': '评论不存在'}), 404

        if comment.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限编辑评论'}), 403

        comment.content = content
        comment.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({'code': 200, 'message': '更新成功', 'data': comment.to_dict()}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@comment_bp.route('', methods=['DELETE'])
@token_required
def delete_comment(current_user=None):
    """删除评论（软删除）"""
    try:
        comment_id = request.args.get('comment_id', type=int)
        if not comment_id:
            return jsonify({'code': 400, 'message': '缺少 comment_id 参数'}), 400

        comment = Comment.query.get(comment_id)
        if not comment or comment.status == 2:
            return jsonify({'code': 404, 'message': '评论不存在'}), 404

        if comment.user_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '没有权限删除评论'}), 403

        comment.status = 2
        db.session.commit()

        return jsonify({'code': 200, 'message': '删除成功'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500
