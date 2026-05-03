"""
Nuxt/Nitro 兼容的 Admin API（简化实现）

映射自 server/api/admin/*
"""

from flask import Blueprint, request
from app.models.user import User
from app.utils.auth import token_required
from app.utils.response import success, error


kun_admin_bp = Blueprint('kun_admin', __name__)


def _require_admin(current_user):
  # Nuxt: role > 1 才允许访问这些页面
  if not current_user:
    return error('用户登录失效', code=401, http_status=401)
  if int(current_user.role) <= 1:
    return error('您没有权限查看此页面', code=403, http_status=403)
  return None


@kun_admin_bp.route('/overview/all', methods=['GET'])
@token_required
def overview_all(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard
  # 占位：返回空统计项列表
  return success(data=[], message='获取成功')


@kun_admin_bp.route('/overview/stats', methods=['GET'])
@token_required
def overview_stats(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard
  days = request.args.get('days', 7, type=int)
  # 占位：返回空时间序列
  return success(data=[], message='获取成功')


@kun_admin_bp.route('/user', methods=['GET'])
@token_required
def admin_user_list(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  page = request.args.get('page', 1, type=int)
  limit = request.args.get('limit', 20, type=int)
  offset = (page - 1) * limit

  q = User.query.order_by(User.created.desc())
  total = q.count()
  data = q.offset(offset).limit(limit).all()

  users = [{
    'id': u.id,
    'name': u.name,
    'avatar': u.avatar,
    'created': u.created.isoformat() if u.created else None,
    'status': u.status
  } for u in data]

  return success(data={'users': users, 'totalCount': total}, message='获取成功')


@kun_admin_bp.route('/user/search', methods=['GET'])
@token_required
def admin_user_search(current_user=None):
  guard = _require_admin(current_user)
  if guard:
    return guard

  q = request.args.get('q', '', type=str)
  data = User.query.filter(User.name.like(f'%{q}%')).limit(50).all()
  users = [{
    'id': u.id,
    'name': u.name,
    'avatar': u.avatar,
    'created': u.created.isoformat() if u.created else None,
    'status': u.status
  } for u in data]
  return success(data=users, message='获取成功')

