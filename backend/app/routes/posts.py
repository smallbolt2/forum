"""
文章路由
"""
from flask import Blueprint, request, jsonify
from app import db
from app.models.post import Post
from app.models.topic import Topic
from app.models.tag import Tag
from app.models.category import Category
from app.models.post_like import PostLike
from app.models.post_view import PostView
from app.utils.auth import token_required
from datetime import datetime, timedelta

post_bp = Blueprint('posts', __name__)


@post_bp.route('', methods=['GET'])
def get_posts():
    """获取文章列表"""
    try:
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 10, type=int)
        category_id = request.args.get('category_id', type=int)
        tag_id = request.args.get('tag_id', type=int)
        keyword = request.args.get('keyword', '')
        author_id = request.args.get('author_id', type=int)
        status = request.args.get('status', 1, type=int)  # 默认只获取已发布的文章
        
        # 根据status参数决定过滤条件
        if status == 0:
            # status=0表示获取所有状态（包括草稿和已发布的，但不包括已删除的）
            query = Post.query.filter(Post.status != 2)
        else:
            query = Post.query.filter_by(status=status)
        
        # 作者筛选
        if author_id:
            query = query.filter_by(author_id=author_id)
        
        # 分类筛选
        if category_id:
            query = query.filter_by(category_id=category_id)
        
        # 标签筛选
        if tag_id:
            query = query.join(Post.tags).filter(Tag.id == tag_id)
        
        # 关键词搜索
        if keyword:
            query = query.filter(
                db.or_(
                    Post.title.like(f'%{keyword}%'),
                    Post.content.like(f'%{keyword}%')
                )
            )
        
        # 排序：置顶优先，然后按发布时间倒序
        query = query.order_by(Post.is_top.desc(), Post.published_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        posts = pagination.items
        
        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': {
                'posts': [post.to_dict() for post in posts],
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


@post_bp.route('/<int:post_id>', methods=['GET'])
def get_post(post_id):
    """获取文章详情"""
    try:
        # 先尝试从 posts 表读取
        post = Post.query.get(post_id)
        is_topic = False

        # 如果 posts 表中不存在，则尝试从 topic 表读取（兼容旧表）
        if not post:
            post = Topic.query.get(post_id)
            is_topic = True

        if not post or (is_topic and post.status == 2):
            return jsonify({'code': 404, 'message': '文章不存在'}), 404

        # 如果是 topic 表数据，直接增加浏览量（不记录访问日志）
        if is_topic:
            post.view = (post.view or 0) + 1
            db.session.commit()

            return jsonify({
                'code': 200,
                'message': '获取成功',
                'data': {
                    'id': post.id,
                    'title': post.title,
                    'content': post.content,
                    'summary': None,
                    'cover_image': None,
                    'view': post.view,
                    'likes': 0,
                    'author': {
                        'id': post.user.id,
                        'nickname': post.user.nickname,
                        'avatar': post.user.avatar
                    } if getattr(post, 'user', None) else None,
                    'created_at': post.created.strftime('%Y-%m-%d %H:%M:%S') if post.created else None,
                    'updated_at': post.updated.strftime('%Y-%m-%d %H:%M:%S') if post.updated else None,
                    'published_at': post.created.strftime('%Y-%m-%d %H:%M:%S') if post.created else None,
                    'tags': [],
                    'comments': []
                }
            })

        # 以下为 posts 表逻辑（包含浏览记录）
        client_ip = request.remote_addr
        user_agent = request.headers.get('User-Agent', '')

        # 检查该IP在24小时内是否已经浏览过这篇文章
        twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
        existing_view = PostView.query.filter_by(
            post_id=post_id,
            ip_address=client_ip
        ).filter(PostView.viewed_at >= twenty_four_hours_ago).first()

        # 如果没有浏览记录，则增加浏览量并记录
        if not existing_view:
            post.views += 1

            # 创建浏览记录
            view_record = PostView(
                post_id=post_id,
                ip_address=client_ip,
                user_agent=user_agent[:255]  # 限制长度
            )
            db.session.add(view_record)

        db.session.commit()

        return jsonify({
            'code': 200,
            'message': '获取成功',
            'data': post.to_full_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@post_bp.route('', methods=['POST'])
@token_required
def create_post(current_user=None):
    """创建文章"""
    try:
        data = request.get_json()
        
        # 验证必填字段
        if not data.get('title'):
            return jsonify({'code': 400, 'message': '标题不能为空'}), 400
        if not data.get('content'):
            return jsonify({'code': 400, 'message': '内容不能为空'}), 400
        
        post = Post(
            title=data.get('title'),
            content=data.get('content'),
            summary=data.get('summary'),
            cover_image=data.get('cover_image'),
            author_id=current_user.id,  # 使用当前登录用户
            category_id=data.get('category_id'),
            status=data.get('status', 1),
            is_top=data.get('is_top', False)
        )
        
        # 处理标签
        if data.get('tags'):
            tag_ids = data.get('tags', [])
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            post.tags = tags
        
        db.session.add(post)
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '创建成功',
            'data': post.to_dict()
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@post_bp.route('/<int:post_id>', methods=['PUT'])
@token_required
def update_post(post_id, current_user=None):
    """更新文章"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # 检查权限：只能编辑自己的文章或管理员
        if post.author_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权编辑此文章'}), 403
        
        data = request.get_json()
        
        post.title = data.get('title', post.title)
        post.content = data.get('content', post.content)
        post.summary = data.get('summary', post.summary)
        post.cover_image = data.get('cover_image', post.cover_image)
        post.category_id = data.get('category_id', post.category_id)
        post.status = data.get('status', post.status)
        post.is_top = data.get('is_top', post.is_top)
        
        # 处理标签
        if 'tags' in data:
            tag_ids = data.get('tags', [])
            tags = Tag.query.filter(Tag.id.in_(tag_ids)).all()
            post.tags = tags
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '更新成功',
            'data': post.to_dict()
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@post_bp.route('/<int:post_id>', methods=['DELETE'])
@token_required
def delete_post(post_id, current_user=None):
    """删除文章"""
    try:
        post = Post.query.get_or_404(post_id)
        
        # 检查权限：只能删除自己的文章或管理员
        if post.author_id != current_user.id and current_user.role != 'admin':
            return jsonify({'code': 403, 'message': '无权删除此文章'}), 403
        
        post.status = 2  # 软删除
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '删除成功'
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500


@post_bp.route('/<int:post_id>/like', methods=['POST'])
def like_post(post_id):
    """点赞文章"""
    try:
        # 获取客户端IP
        client_ip = request.remote_addr
        
        # 检查该IP是否已经点赞过该文章
        existing_like = PostLike.query.filter_by(post_id=post_id, ip_address=client_ip).first()
        if existing_like:
            return jsonify({
                'code': 400,
                'message': '您已经点赞过了'
            }), 400
        
        post = Post.query.get_or_404(post_id)
        post.likes += 1
        
        # 记录点赞记录
        new_like = PostLike(post_id=post_id, ip_address=client_ip)
        db.session.add(new_like)
        
        db.session.commit()
        
        return jsonify({
            'code': 200,
            'message': '点赞成功',
            'data': {'likes': post.likes}
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({'code': 500, 'message': str(e)}), 500

