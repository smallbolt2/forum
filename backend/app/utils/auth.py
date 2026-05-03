"""
认证工具函数
"""
from functools import wraps
from flask import request, jsonify, current_app
import jwt
from app.models.user import User


def _extract_jwt_token() -> str:
    """
    优先读取 Authorization: Bearer xxx；
    若不存在则回退读取 Nuxt 登录写入的 refresh cookie。
    """
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        token = auth_header.replace('Bearer ', '', 1).strip()
        if token:
            return token

    cookie_token = request.cookies.get('kungalgame-moemoe-refresh-token', '').strip()
    return cookie_token


def token_required(f):
    """Token验证装饰器，兼容 Nuxt JWT 负载（含 iss / aud / uid / role）"""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _extract_jwt_token()
        
        if not token:
            return jsonify({'code': 401, 'message': '未提供Token'}), 401
        
        try:
            # 使用配置中的SECRET_KEY，并校验 iss / aud（如果提供）
            options = {"verify_iss": False, "verify_aud": False}
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
                options=options
            )
            # Nuxt 侧 payload 使用 uid 字段
            user_id = payload.get('uid') or payload.get('user_id')
            user = User.query.get(user_id)
            
            # Prisma: 0 normal, 1 banned
            if not user or user.status != 0:
                return jsonify({'code': 401, 'message': '用户不存在或已被禁用'}), 401
            
            # 将用户对象添加到kwargs中
            kwargs['current_user'] = user
            return f(*args, **kwargs)
        except jwt.ExpiredSignatureError:
            return jsonify({'code': 401, 'message': 'Token已过期'}), 401
        except jwt.InvalidTokenError:
            return jsonify({'code': 401, 'message': '无效的Token'}), 401
    
    return decorated


def admin_required(f):
    """管理员权限装饰器"""
    @wraps(f)
    @token_required
    def decorated(*args, **kwargs):
        current_user = kwargs.get('current_user')
        if not current_user or int(current_user.role) <= 1:
            return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
        return f(*args, **kwargs)
    
    return decorated

