"""
用户认证路由
"""
import re
import secrets
import unicodedata

from flask import Blueprint, request, current_app, jsonify
from app import db
from app.models.user import User
from datetime import datetime, timedelta
import jwt
from app.utils.response import success, error
from app.utils import verification_email as vmail

auth_bp = Blueprint('auth', __name__)

_EMAIL_BODY_PATTERN = re.compile(
  r'^[^\s@]{1,64}@[^\s@]{1,255}\.[^\s@]{1,24}$',
)

# 与 app/config/email-whitelist.ts 中当前启用的域名一致
_KUN_ALLOW_REGISTER_EMAIL = frozenset({
  'qq.com',
  'gmail.com',
  'outlook.com',
})


def _is_valid_name(name: str) -> bool:
  """对齐 shared/utils/validate.ts isValidName（简化不可见字符表）。"""
  if len(name) < 1 or len(name) > 17:
    return False
  invisible = (
    '\u0009\u0020\u00a0\u00ad\u034f\u061c\u115f\u1160\u17b4\u17b5\u180e'
    '\u2000\u2001\u2002\u2003\u2004\u2005\u2006\u2007\u2008\u2009\u200a'
    '\u200b\u200c\u200d\u200e\u200f\u202f\u205f\u2060\u2061\u2062\u2063'
    '\u2064\u2065\u206a\u206b\u206c\u206d\u206e\u206f\u3000\u2800\u3164'
    '\ufeff\uffa0\ufe00'
  )
  if any(c in name for c in invisible):
    return False
  for ch in name:
    cat = unicodedata.category(ch)[0]
    if cat in ('L', 'N'):
      continue
    if ch in '!~_@#$%^&*()+=-':
      continue
    return False
  return True


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


@auth_bp.route('/email/code/register', methods=['POST'])
def email_code_register():
    """
    POST /api/auth/email/code/register
    body: { name, email } — 与 server/api/auth/email/code/register.post.ts 一致，返回 64 位 hex salt。
    """
    try:
        data = request.get_json() or {}
        name = (data.get('name') or '').strip().lower()
        email = (data.get('email') or '').strip().lower()

        if not name or not email:
            return error('非法的邮箱格式', code=400, http_status=400)

        if not _is_valid_name(name):
            return error('非法的用户名', code=400, http_status=400)

        if not email or not _EMAIL_BODY_PATTERN.match(email):
            return error('非法的邮箱格式', code=400, http_status=400)

        domain = email.split('@', 1)[1] if '@' in email else ''
        if domain not in _KUN_ALLOW_REGISTER_EMAIL:
            return error('您的邮箱地址暂时不受支持, 请换一个邮箱试试', code=400, http_status=400)

        if User.query.filter_by(name=name).first():
            return error('您的用户名已经被使用了, 请换一个试试', code=400, http_status=400)

        if User.query.filter_by(email=email).first():
            return error('您的邮箱已经被使用了, 请换一个试试', code=400, http_status=400)

        ip = request.remote_addr or ''
        if vmail.rate_throttled(email, ip):
            return error('您的发邮件的频率过快, 请 30s 后重试', code=400, http_status=400)

        salt = secrets.token_hex(32)
        code = vmail.generate_random_code(7)
        vmail.set_verification_code(salt, email, code, ttl_sec=600)
        vmail.log_register_verification_code(
            current_app._get_current_object(), email, code, salt
        )

        host = current_app.config.get('MAIL_HOST')
        mail_user = current_app.config.get('MAIL_USERNAME')
        mail_password = current_app.config.get('MAIL_PASSWORD')

        if not host or not mail_user or not mail_password:
            if vmail.should_log_verification_code(current_app._get_current_object()):
                vmail.rate_mark_sent(email, ip)
                return jsonify(salt)
            vmail.remove_verification_code(salt, email)
            return error('邮件服务未配置', code=503, http_status=503)

        try:
            vmail.send_register_email_verification(
                current_app._get_current_object(), email, code
            )
        except Exception:
            current_app.logger.exception('SMTP 发送失败')
            vmail.remove_verification_code(salt, email)
            return error('邮件发送失败，请稍后重试', code=500, http_status=500)

        vmail.rate_mark_sent(email, ip)
        return jsonify(salt)
    except Exception as e:
        return error(str(e), code=500, http_status=500)


@auth_bp.route('/email/code/reset', methods=['POST'])
def email_code_reset():
    """
    POST /api/auth/email/code/reset
    body: { email }
    返回 64 位 hex salt（JSON 字符串），与前端 ``result.length === 64`` 一致。
    """
    try:
        data = request.get_json() or {}
        email = (data.get('email') or '').strip().lower()
        if not email or not _EMAIL_BODY_PATTERN.match(email):
            return error('非法的邮箱格式', code=400, http_status=400)

        if User.query.filter_by(email=email).first():
            # Nitro 文案如此（语义实为「该邮箱已被占用」）
            return error('未找到该邮箱对应的用户', code=400, http_status=400)

        ip = request.remote_addr or ''
        if vmail.rate_throttled(email, ip):
            return error('您的发邮件的频率过快, 请 30s 后重试', code=400, http_status=400)

        salt = secrets.token_hex(32)
        code = vmail.generate_random_code(7)
        vmail.set_verification_code(salt, email, code, ttl_sec=600)

        host = current_app.config.get('MAIL_HOST')
        user = current_app.config.get('MAIL_USERNAME')
        password = current_app.config.get('MAIL_PASSWORD')

        if not host or not user or not password:
            if current_app.debug:
                current_app.logger.warning(
                    '[DEV] 未配置 SMTP，邮箱换绑验证码 email=%s code=%s salt(前8)=%s',
                    email,
                    code,
                    salt[:8],
                )
                vmail.rate_mark_sent(email, ip)
                return jsonify(salt)
            vmail.remove_verification_code(salt, email)
            return error('邮件服务未配置', code=503, http_status=503)

        try:
            vmail.send_reset_email_verification(
                current_app._get_current_object(), email, code
            )
        except Exception:
            current_app.logger.exception('SMTP 发送失败')
            vmail.remove_verification_code(salt, email)
            return error('邮件发送失败，请稍后重试', code=500, http_status=500)

        vmail.rate_mark_sent(email, ip)
        return jsonify(salt)
    except Exception as e:
        return error(str(e), code=500, http_status=500)
