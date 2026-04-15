"""
用户认证路由
"""
from flask import Blueprint, request, current_app
from app import db
from app.models.user import User
from datetime import datetime, timedelta
import jwt
from app.utils.response import success, error

auth_bp = Blueprint('auth', __name__)


def generate_token(user_id, secret_key=None):
    """生成与 Nuxt 类似结构的 JWT Token"""
    if secret_key is None:
        secret_key = current_app.config['SECRET_KEY']

    iss = current_app.config.get('JWT_ISS')
    aud = current_app.config.get('JWT_AUD')

    payload = {
        'iss': iss,
        'aud': aud,
        'uid': user_id,
        'exp': datetime.utcnow() + timedelta(days=30),
        'iat': datetime.utcnow()
    }

    token = jwt.encode(payload, secret_key, algorithm='HS256')
    return token


@auth_bp.route('/login', methods=['POST'])
def login():
    """用户登录"""
    try:
        data = request.get_json()
        name_or_email = data.get('name') or data.get('username')
        password = data.get('password')
        
        if not name_or_email or not password:
            return error('用户名或邮箱与密码不能为空', code=400, http_status=400)
        
        # 查找用户
        user = User.query.filter(
            (User.name == name_or_email) | (User.email == name_or_email)
        ).first()
        if not user:
            return error('未找到用户', code=401, http_status=401)
        
        # 验证密码
        if not user.check_password(password):
            return error('用户密码错误', code=401, http_status=401)
        
        # 检查用户状态
        # Prisma: 0 normal, 1 banned
        if user.status != 0:
            return error('该用户已被封禁', code=403, http_status=403)
        
        # 生成Token
        token = generate_token(user.id, current_app.config['SECRET_KEY'])

        user_info = user.to_dict()

        return success(
            data={
                'token': token,
                'user': user_info
            },
            message='登录成功'
        )
    except Exception as e:
        return error(str(e), code=500, http_status=500)


@auth_bp.route('/register', methods=['POST'])
def register():
    """用户注册"""
    try:
        data = request.get_json()
        username = data.get('name') or data.get('username')
        email = data.get('email')
        password = data.get('password')

        if not username or not email or not password:
            return error('用户名、邮箱和密码不能为空', code=400, http_status=400)

        if len(password) < 6:
            return error('密码长度至少6位', code=400, http_status=400)

        if User.query.filter_by(name=username.lower()).first():
            return error('您的用户名已经被使用, 请更换', code=400, http_status=400)

        if User.query.filter_by(email=email.lower()).first():
            return error('您的邮箱已经被使用, 请更换', code=400, http_status=400)

        user = User(
            name=username.lower(),
            email=email.lower(),
            avatar='',
            role=1,
            status=0
        )
        user.set_password(password)

        db.session.add(user)
        db.session.commit()

        token = generate_token(user.id, current_app.config['SECRET_KEY'])

        return success(
            data={
                'token': token,
                'user': user.to_dict()
            },
            message='注册成功',
            http_status=201
        )
    except Exception as e:
        db.session.rollback()
        return error(str(e), code=500, http_status=500)


@auth_bp.route('/me', methods=['GET'])
def get_current_user():
    """获取当前登录用户信息"""
    try:
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        if not token:
            return error('未提供Token', code=401, http_status=401)

        try:
            options = {"verify_iss": False, "verify_aud": False}
            payload = jwt.decode(
                token,
                current_app.config['SECRET_KEY'],
                algorithms=['HS256'],
                options=options
            )
            user_id = payload.get('uid') or payload.get('user_id')
            user = User.query.get(user_id)

            if not user or user.status != 0:
                return error('用户不存在或已被禁用', code=401, http_status=401)

            return success(data=user.to_dict(), message='获取成功')
        except jwt.ExpiredSignatureError:
            return error('Token已过期', code=401, http_status=401)
        except jwt.InvalidTokenError:
            return error('无效的Token', code=401, http_status=401)
    except Exception as e:
        return error(str(e), code=500, http_status=500)

