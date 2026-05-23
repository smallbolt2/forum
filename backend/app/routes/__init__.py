"""
路由模块
"""
from flask import Blueprint, jsonify
from app.routes.posts import post_bp
from app.routes.topics import topic_bp
from app.routes.categories import category_bp
from app.routes.tags import tag_bp
from app.routes.comments import comment_bp
from app.routes.users import user_bp
from app.routes.auth import auth_bp
from app.routes.home import home_bp
from app.routes.topic_replies import topic_reply_bp
from app.routes.kun_topic import kun_topic_bp
from app.routes.kun_toolset import kun_toolset_bp
from app.routes.kun_galgame import kun_galgame_bp
from app.routes.kun_admin import kun_admin_bp
from app.routes.kun_user import kun_user_bp
from app.routes.kun_topic_best_answer import kun_topic_best_answer_bp
from app.routes.kun_topic_reply_detail import kun_topic_reply_detail_bp
from app.routes.kun_doc_article_stub import kun_doc_article_bp
from app.routes.kun_resource import kun_resource_bp
from app.routes.kun_category import kun_category_bp
from app.routes.kun_search import kun_search_bp
from app.routes.kun_image import kun_image_bp
from app.routes.kun_section import kun_section_bp
from app.routes.kun_activity import kun_activity_bp
from app.routes.kun_message import kun_message_bp

# 创建API蓝图
api_bp = Blueprint('api', __name__)

# API根路径
@api_bp.route('/', methods=['GET'])
def api_root():
    """API根路径"""
    return jsonify({
        'code': 200,
        'message': '博客API服务运行正常',
        'version': '1.0.0',
        'endpoints': {
            'auth': '/api/auth',
            'posts': '/api/posts',
            'categories': '/api/categories',
            'tags': '/api/tags',
            'comments': '/api/comments',
            'users': '/api/users',
            'home': '/api/home',
            'topics': '/api/topics',
            'topic_replies': '/api/topic_replies'
        }
    })

api_bp.register_blueprint(auth_bp, url_prefix='/auth')
## 已注册 home_bp，移除重复注册
api_bp.register_blueprint(post_bp, url_prefix='/posts')
api_bp.register_blueprint(category_bp, url_prefix='/categories')
api_bp.register_blueprint(tag_bp, url_prefix='/tags')
api_bp.register_blueprint(comment_bp, url_prefix='/comments')
api_bp.register_blueprint(user_bp, url_prefix='/users')
api_bp.register_blueprint(home_bp, url_prefix='/home')
api_bp.register_blueprint(topic_bp, url_prefix='/topics')
api_bp.register_blueprint(topic_reply_bp, url_prefix='/topic_replies')
api_bp.register_blueprint(kun_topic_bp, url_prefix='/topic')
api_bp.register_blueprint(kun_toolset_bp, url_prefix='/toolset')
api_bp.register_blueprint(kun_galgame_bp, url_prefix='/galgame')
api_bp.register_blueprint(kun_admin_bp, url_prefix='/admin')
api_bp.register_blueprint(kun_user_bp, url_prefix='/user')
api_bp.register_blueprint(kun_topic_best_answer_bp, url_prefix='/topic')
api_bp.register_blueprint(kun_topic_reply_detail_bp, url_prefix='/topic')
api_bp.register_blueprint(kun_doc_article_bp, url_prefix='/doc')
api_bp.register_blueprint(kun_resource_bp, url_prefix='/resource')
api_bp.register_blueprint(kun_category_bp, url_prefix='/category')
api_bp.register_blueprint(kun_search_bp, url_prefix='/search')
api_bp.register_blueprint(kun_image_bp, url_prefix='/image')
api_bp.register_blueprint(kun_section_bp, url_prefix='/section')
api_bp.register_blueprint(kun_activity_bp, url_prefix='/activity')
api_bp.register_blueprint(kun_message_bp, url_prefix='/message')

