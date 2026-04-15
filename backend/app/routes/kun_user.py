"""
Nuxt/Nitro 兼容的 User API（核心：登录/注册）

映射自 server/api/user/*
"""

from datetime import datetime, timedelta

from flask import Blueprint, request, jsonify, current_app, make_response
import jwt

from app import db
from app.models.user import User
from app.utils.response import error


kun_user_bp = Blueprint('kun_user', __name__)


def _generate_token(uid: int, name: str, role: int, expire_seconds: int):
  secret = current_app.config['SECRET_KEY']
  iss = current_app.config.get('JWT_ISS')
  aud = current_app.config.get('JWT_AUD')
  payload = {
    'iss': iss,
    'aud': aud,
    'uid': uid,
    'name': name,
    'role': role,
    'exp': datetime.utcnow() + timedelta(seconds=expire_seconds),
    'iat': datetime.utcnow()
  }
  return jwt.encode(payload, secret, algorithm='HS256')


def _login_response(user: User):
  # 对齐前端期望的 AuthLoginResponseData
  return {
    'id': user.id,
    'name': user.name,
    'avatar': user.avatar,
    'avatarMin': user.avatar,
    'moemoepoint': user.moemoepoint,
    'role': user.role,
    'isCheckIn': bool(user.daily_check_in),
    'dailyToolsetUploadCount': user.daily_toolset_upload_count
  }


@kun_user_bp.route('/login', methods=['POST'])
def login():
  """
  POST /api/user/login
  body: { name, password }
  return: AuthLoginResponseData (object)
  """
  try:
    data = request.get_json() or {}
    name_or_email = (data.get('name') or '').strip()
    password = data.get('password') or ''

    if not name_or_email or not password:
      return error('用户名或邮箱与密码不能为空', code=400, http_status=400)

    user = User.query.filter((User.name == name_or_email) | (User.email == name_or_email)).first()
    if not user:
      return error('未找到用户', code=404, http_status=404)
    if user.status != 0:
      return error('该用户已被封禁', code=403, http_status=403)
    if not user.check_password(password):
      return error('用户密码错误', code=401, http_status=401)

    refresh_token = _generate_token(user.id, user.name, user.role, 30 * 24 * 60 * 60)
    resp = make_response(jsonify(_login_response(user)))
    # Nuxt: cookie 名 kungalgame-moemoe-refresh-token
    resp.set_cookie(
      'kungalgame-moemoe-refresh-token',
      refresh_token,
      httponly=True,
      samesite='Strict',
      secure=False,
      path='/',
      max_age=30 * 24 * 60 * 60
    )
    return resp
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_user_bp.route('/register', methods=['POST'])
def register():
  """
  POST /api/user/register
  body: { codeSalt, name, email, password, code }
  return: AuthLoginResponseData (object)

  注意：验证码校验暂未 1:1 复刻（后续接入 topic storage / db）
  """
  try:
    data = request.get_json() or {}
    name = (data.get('name') or '').strip().lower()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''

    if not name or not email or not password:
      return error('用户名、邮箱和密码不能为空', code=400, http_status=400)

    if User.query.filter_by(name=name).first():
      return error('您的用户名已经被使用, 请更换', code=400, http_status=400)
    if User.query.filter_by(email=email).first():
      return error('您的邮箱已经被使用, 请更换', code=400, http_status=400)

    user = User(
      name=name,
      email=email,
      password='',
      ip=request.remote_addr or '',
      avatar='',
      role=1,
      status=0,
      moemoepoint=7,
      bio='',
      daily_check_in=0,
      daily_image_count=0,
      daily_toolset_upload_count=0
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    refresh_token = _generate_token(user.id, user.name, user.role, 30 * 24 * 60 * 60)
    resp = make_response(jsonify(_login_response(user)))
    resp.set_cookie(
      'kungalgame-moemoe-refresh-token',
      refresh_token,
      httponly=True,
      samesite='Strict',
      secure=False,
      path='/',
      max_age=30 * 24 * 60 * 60
    )
    return resp
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)

