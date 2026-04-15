"""
Flask应用初始化
"""
from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_migrate import Migrate
from app.config import Config

# 初始化扩展
db = SQLAlchemy()
migrate = Migrate()
cors = CORS()


def create_app(config_class=Config):
    """
    应用工厂函数
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app, resources={
        r"/api/*": {
            "origins": ["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173"],
            "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
            "allow_headers": ["Content-Type", "Authorization"]
        }
    })

    # 注册蓝图
    from app.routes import api_bp
    app.register_blueprint(api_bp, url_prefix='/api')
    
    # 添加根路径
    @app.route('/')
    def root():
        from flask import jsonify
        return jsonify({
            'status': 'success',
            'message': '博客后端服务运行正常',
            'api_docs': '访问 /api 查看API信息',
            'api_base': '/api',
            'available_endpoints': [
                'GET /api/posts - 获取文章列表',
                'GET /api/posts/<id> - 获取文章详情',
                'POST /api/posts - 创建文章',
                'GET /api/categories - 获取分类列表',
                'GET /api/tags - 获取标签列表',
                'GET /api/comments - 获取评论列表',
                'POST /api/auth/login - 用户登录',
                'POST /api/auth/register - 用户注册'
            ]
        })

    # 全局错误处理，确保返回统一 JSON 结构
    @app.errorhandler(404)
    def handle_404(error):
        return jsonify({'code': 404, 'message': 'Not Found', 'data': None}), 404

    @app.errorhandler(500)
    def handle_500(error):
        return jsonify({'code': 500, 'message': 'Internal Server Error', 'data': None}), 500

    return app

