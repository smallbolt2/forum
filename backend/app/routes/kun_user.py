"""
Nuxt/Nitro 兼容的 User API（核心：登录/注册）

映射自 server/api/user/*
"""

import re
from datetime import datetime, timedelta
from pathlib import Path

import bcrypt
import jwt
from flask import Blueprint, request, jsonify, current_app, make_response
from sqlalchemy import func
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import aliased

from app import db
from app.models.user import User
from app.models.topic import Topic
from app.models.topic_reply import TopicReply
from app.models.prisma_topic_extras import (
  TopicLike,
  TopicDislike,
  TopicFavorite,
  TopicUpvote,
  TopicReplyLike,
  TopicReplyDislike,
  TopicComment,
  TopicCommentLike,
  TopicReplyTarget,
  TopicTag,
  TopicSectionRelation,
)
from app.models.prisma_galgame_min import Galgame, GalgameLike, GalgameFavorite, GalgameResource
from app.models.prisma_toolset_min import GalgameToolset, GalgameToolsetResource
from app.utils.response import error
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie
from app.utils import verification_email as vmail
from app.utils.user_purge import purge_user_for_permanent_delete


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


def _count_with_in(model, column, ids):
  if not ids:
    return 0
  try:
    return model.query.filter(column.in_(ids)).count()
  except SQLAlchemyError:
    # 某些实例未同步完整表结构时，降级为 0，避免接口 500
    return 0


def _safe_count(query):
  try:
    return query.count()
  except SQLAlchemyError:
    # 某些实例未同步完整表结构时，降级为 0，避免接口 500
    return 0


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
    pw_raw = data.get('password')
    password = '' if pw_raw is None else str(pw_raw)

    if not name_or_email or not password:
      return error('用户名或邮箱与密码不能为空', code=400, http_status=400)

    key = name_or_email.strip().lower()
    user = User.query.filter(
      (func.lower(User.name) == key) | (func.lower(User.email) == key)
    ).first()
    # 与 Nitro kunError 默认一致：HTTP 233 + body code，避免真 404 被当成路由错误
    if not user:
      return error('未找到用户', code=233, http_status=233)
    if user.status != 0:
      return error('该用户已被封禁', code=233, http_status=233)
    if not user.check_password(password):
      # HTTP 401 便于从访问日志区分「账号不存在(233)」与「密码错误」
      return error('用户密码错误', code=233, http_status=401)

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

  """
  try:
    data = request.get_json() or {}
    code_salt = (data.get('codeSalt') or '').strip()
    name = (data.get('name') or '').strip().lower()
    email = (data.get('email') or '').strip().lower()
    password = data.get('password') or ''
    code = (data.get('code') or '').strip()

    if not name or not email or not password:
      return error('用户名、邮箱和密码不能为空', code=400, http_status=400)

    if len(code_salt) != 64 or not re.fullmatch(r'[0-9a-fA-F]{64}', code_salt):
      return error('非法的邮箱验证码', code=400, http_status=400)
    if len(code) != 7:
      return error('非法的邮箱验证码', code=400, http_status=400)

    if not vmail.verify_verification_code(code_salt, email, code):
      return error('非法的邮箱验证码', code=400, http_status=400)
    vmail.remove_verification_code(code_salt, email)

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


@kun_user_bp.route('/<int:uid>', methods=['GET'])
def get_user_info(uid: int):
  """
  GET /api/user/<uid>?userId=<uid>
  与 Nuxt 约定一致：返回 UserInfo 对象或字符串 'banned'
  """
  user = User.query.filter_by(id=uid).first()
  if not user:
    return error('未找到该用户', code=404, http_status=404)
  if user.status == 1:
    return jsonify('banned')

  # 基础统计
  topic_query = Topic.query.filter_by(user_id=uid)
  reply_query = TopicReply.query.filter_by(user_id=uid)
  comment_query = TopicComment.query.filter_by(user_id=uid)
  galgame_query = Galgame.query.filter_by(user_id=uid)

  topic_count = _safe_count(topic_query)
  reply_count = _safe_count(reply_query)
  comment_count = _safe_count(comment_query)
  galgame_count = _safe_count(galgame_query)
  galgame_resource_count = _safe_count(GalgameResource.query.filter_by(user_id=uid))
  toolset_count = _safe_count(GalgameToolset.query.filter_by(user_id=uid))
  toolset_resource_count = _safe_count(GalgameToolsetResource.query.filter_by(user_id=uid))

  # 近 1 天新增
  one_day_ago = datetime.utcnow() - timedelta(days=1)
  daily_topic_count = _safe_count(topic_query.filter(Topic.created >= one_day_ago))
  daily_galgame_count = _safe_count(galgame_query.filter(Galgame.created >= one_day_ago))

  # 被收到的互动统计（基于该用户创建的话题/回复/评论/galgame）
  try:
    user_topic_ids = [t.id for t in topic_query.with_entities(Topic.id).all()]
  except SQLAlchemyError:
    user_topic_ids = []
  try:
    user_reply_ids = [r.id for r in reply_query.with_entities(TopicReply.id).all()]
  except SQLAlchemyError:
    user_reply_ids = []
  try:
    user_comment_ids = [c.id for c in comment_query.with_entities(TopicComment.id).all()]
  except SQLAlchemyError:
    user_comment_ids = []
  try:
    user_galgame_ids = [g.id for g in galgame_query.with_entities(Galgame.id).all()]
  except SQLAlchemyError:
    user_galgame_ids = []

  total_likes = (
    _count_with_in(TopicLike, TopicLike.topic_id, user_topic_ids)
    + _count_with_in(TopicReplyLike, TopicReplyLike.topic_reply_id, user_reply_ids)
    + _count_with_in(TopicCommentLike, TopicCommentLike.topic_comment_id, user_comment_ids)
    + _count_with_in(GalgameLike, GalgameLike.galgame_id, user_galgame_ids)
  )
  total_dislikes = (
    _count_with_in(TopicDislike, TopicDislike.topic_id, user_topic_ids)
    + _count_with_in(TopicReplyDislike, TopicReplyDislike.topic_reply_id, user_reply_ids)
  )
  total_upvotes = _count_with_in(TopicUpvote, TopicUpvote.topic_id, user_topic_ids)
  total_favorites = (
    _count_with_in(TopicFavorite, TopicFavorite.topic_id, user_topic_ids)
    + _count_with_in(GalgameFavorite, GalgameFavorite.galgame_id, user_galgame_ids)
  )

  # 这里部分表尚未建模，先对齐字段并回填 0，避免前端报错
  response_data = {
    'id': user.id,
    'name': user.name,
    'avatar': user.avatar,
    'role': user.role,
    'status': user.status,
    'moemoepoint': user.moemoepoint,
    'bio': user.bio,
    'created': user.created.isoformat() if user.created else None,
    'upvote': total_upvotes,
    'like': total_likes,
    'dislike': total_dislikes,
    'favorite': total_favorites,
    'replyCreated': reply_count,
    'commentCreated': comment_count,
    'topic': topic_count,
    'galgame': galgame_count,
    'galgameComment': 0,
    'galgamePr': 0,
    'galgameLink': 0,
    'galgameRating': 0,
    'contributeGalgame': 0,
    'galgameResource': galgame_resource_count,
    'galgameToolset': toolset_count,
    'galgameToolsetResource': toolset_resource_count,
    'dailyTopicCount': daily_topic_count,
    'dailyGalgameCount': daily_galgame_count,
  }
  return jsonify(response_data)


@kun_user_bp.route('/<int:uid>/floating', methods=['GET'])
def get_user_floating(uid: int):
  """
  GET /api/user/<uid>/floating?userId=<uid>
  与 Nuxt 约定一致：返回 UserFloatingCard 对象或字符串 'banned'
  """
  user = User.query.filter_by(id=uid).first()
  if not user:
    return error('未找到该用户', code=404, http_status=404)
  if user.status == 1:
    return jsonify('banned')

  topic_count = _safe_count(Topic.query.filter_by(user_id=uid))
  topic_reply_count = _safe_count(TopicReply.query.filter_by(user_id=uid))
  topic_comment_count = _safe_count(TopicComment.query.filter_by(user_id=uid))
  galgame_count = _safe_count(Galgame.query.filter_by(user_id=uid))
  galgame_resource_count = _safe_count(GalgameResource.query.filter_by(user_id=uid))

  # galgame_contributor 表当前未建模，先返回 0 保持字段完整
  response_data = {
    'id': user.id,
    'name': user.name,
    'avatar': user.avatar,
    'moemoepoint': user.moemoepoint,
    'topicCount': topic_count,
    'topicReplyCount': topic_reply_count,
    'topicCommentCount': topic_comment_count,
    'galgameCount': galgame_count,
    'galgameResourceCount': galgame_resource_count,
    'galgameContributeCount': 0,
  }
  return jsonify(response_data)


def _parse_user_list_query(uid: int):
  """与 getUserTopicSchema / getUserReplySchema 对齐：userId 与路径 uid 一致"""
  q_user = request.args.get('userId', type=int)
  if q_user is not None and q_user != uid:
    return None
  page = request.args.get('page', 1, type=int) or 1
  limit = request.args.get('limit', 50, type=int) or 50
  page = max(1, min(page, 9_999_999))
  limit = max(1, min(limit, 50))
  return page, limit, (page - 1) * limit


def _nsfw_cookie_mode():
  return request.cookies.get('nsfw') or request.cookies.get('kun-nsfw') or ''


def _format_replies_created_batch(replies):
  """对齐 Nitro replies.get：有楼中楼则按 target 拆条，否则用主楼 content"""
  if not replies:
    return []
  ids = [r.id for r in replies]
  targets_by_reply = {}
  for tt in TopicReplyTarget.query.filter(TopicReplyTarget.reply_id.in_(ids)).all():
    targets_by_reply.setdefault(tt.reply_id, []).append(tt)
  out = []
  for reply in replies:
    tgts = targets_by_reply.get(reply.id) or []
    if tgts:
      for t in tgts:
        out.append({
          'topicId': reply.topic_id,
          'content': t.content,
          'created': reply.created.isoformat() if reply.created else None,
        })
    elif reply.content:
      out.append({
        'topicId': reply.topic_id,
        'content': reply.content,
        'created': reply.created.isoformat() if reply.created else None,
      })
  return out


@kun_user_bp.route('/<int:uid>/replies', methods=['GET'])
def list_user_replies(uid: int):
  """
  GET /api/user/<uid>/replies?page=&limit=&userId=&type=
  type: reply_created | reply_target | reply_like
  """
  try:
    parsed = _parse_user_list_query(uid)
    if parsed is None:
      return error('参数错误', code=400, http_status=400)
    page, limit, skip = parsed
    rtype = (request.args.get('type') or '').strip()

    if rtype == 'reply_target':
      ReplyMain = aliased(TopicReply)
      ReplyTarget = aliased(TopicReply)
      base_q = (
        db.session.query(TopicReplyTarget, ReplyMain.topic_id, ReplyMain.created)
        .join(ReplyMain, TopicReplyTarget.reply_id == ReplyMain.id)
        .join(ReplyTarget, TopicReplyTarget.target_reply_id == ReplyTarget.id)
        .filter(
          ReplyTarget.user_id == uid,
          ReplyMain.user_id != uid,
        )
        .order_by(TopicReplyTarget.created.desc())
      )
      total = base_q.count()
      rows = base_q.offset(skip).limit(limit).all()
      replies = [
        {
          'topicId': tid,
          'content': tgt.content,
          'created': cr.isoformat() if cr else None,
        }
        for tgt, tid, cr in rows
      ]
      return jsonify({'replies': replies, 'totalCount': total})

    if rtype == 'reply_created':
      q = TopicReply.query.filter_by(user_id=uid)
    elif rtype == 'reply_like':
      liked_ids = [
        row[0]
        for row in db.session.query(TopicReplyLike.topic_reply_id)
        .filter_by(user_id=uid)
        .distinct()
        .all()
      ]
      if not liked_ids:
        return jsonify({'replies': [], 'totalCount': 0})
      q = TopicReply.query.filter(TopicReply.id.in_(liked_ids))
    else:
      return error('无效的类型参数', code=400, http_status=400)

    total = q.count()
    rows = q.order_by(TopicReply.created.desc()).offset(skip).limit(limit).all()
    replies = _format_replies_created_batch(rows)
    return jsonify({'replies': replies, 'totalCount': total})
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_user_bp.route('/<int:uid>/topics', methods=['GET'])
def list_user_topics(uid: int):
  """
  GET /api/user/<uid>/topics?page=&limit=&userId=&type=
  type: topic | topic_like | topic_upvote | topic_favorite | topic_hide
  """
  try:
    parsed = _parse_user_list_query(uid)
    if parsed is None:
      return error('参数错误', code=400, http_status=400)
    page, limit, skip = parsed
    ttype = (request.args.get('type') or '').strip()

    if ttype == 'topic_hide':
      viewer = get_uid_from_refresh_cookie()
      if viewer != uid:
        return jsonify({'topics': [], 'totalCount': 0})
      q = Topic.query.filter_by(user_id=uid, status=1)
      total = q.count()
      rows = (
        q.order_by(Topic.created.desc())
        .offset(skip)
        .limit(limit)
        .all()
      )
      topics = [
        {
          'id': t.id,
          'title': t.title,
          'created': t.created.isoformat() if t.created else None,
        }
        for t in rows
      ]
      return jsonify({'topics': topics, 'totalCount': total})

    base_filter = [Topic.status != 1]
    if _nsfw_cookie_mode() == 'sfw':
      base_filter.append(Topic.is_nsfw == False)  # noqa: E712

    if ttype == 'topic':
      q = Topic.query.filter(Topic.user_id == uid, *base_filter)
    elif ttype == 'topic_like':
      tids = [
        row[0]
        for row in db.session.query(TopicLike.topic_id)
        .filter_by(user_id=uid)
        .distinct()
        .all()
      ]
      if not tids:
        return jsonify({'topics': [], 'totalCount': 0})
      q = Topic.query.filter(Topic.id.in_(tids), *base_filter)
    elif ttype == 'topic_upvote':
      tids = [
        row[0]
        for row in db.session.query(TopicUpvote.topic_id)
        .filter_by(user_id=uid)
        .distinct()
        .all()
      ]
      if not tids:
        return jsonify({'topics': [], 'totalCount': 0})
      q = Topic.query.filter(Topic.id.in_(tids), *base_filter)
    elif ttype == 'topic_favorite':
      tids = [
        row[0]
        for row in db.session.query(TopicFavorite.topic_id)
        .filter_by(user_id=uid)
        .distinct()
        .all()
      ]
      if not tids:
        return jsonify({'topics': [], 'totalCount': 0})
      q = Topic.query.filter(Topic.id.in_(tids), *base_filter)
    else:
      return error('无效的类型参数', code=400, http_status=400)

    total = q.count()
    rows = q.order_by(Topic.created.desc()).offset(skip).limit(limit).all()
    topics = [
      {
        'id': t.id,
        'title': t.title,
        'created': t.created.isoformat() if t.created else None,
      }
      for t in rows
    ]
    return jsonify({'topics': topics, 'totalCount': total})
  except Exception as e:
    return error(str(e), code=500, http_status=500)


def _mask_email_display(email: str) -> str:
  """与 server/api/user/email.get.ts 一致"""
  if not email or '@' not in email:
    return '~~~~~~~~~'
  at_idx = email.index('@')
  local = email[:at_idx]
  domain = email[at_idx:]
  masked_local = local[:2] + '~~~~~~~'
  return masked_local + domain


@kun_user_bp.route('/email', methods=['GET'])
def get_user_email_masked():
  """
  GET /api/user/email
  登录用户当前邮箱脱敏字符串（JSON 字符串，与 $fetch 解析一致）
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)
  user = User.query.filter_by(id=uid).first()
  if not user:
    return error('未找到该用户', code=404, http_status=404)
  return jsonify(_mask_email_display(user.email or ''))


_USERNAME_PUT_PATTERN = re.compile(
  r'^[\w!~_@#$%^&*()+=\-]{1,17}$',
  re.UNICODE,
)


@kun_user_bp.route('/username', methods=['PUT'])
def update_username():
  """
  PUT /api/user/username
  body: { username }
  与 server/api/user/username.put.ts 对齐：17 萌萌点、小写落库、重名校验
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)

  data = request.get_json() or {}
  raw = (data.get('username') or '').strip()
  new_name = raw.lower()
  if not new_name or len(new_name) > 17 or not _USERNAME_PUT_PATTERN.match(new_name):
    return error('非法的用户名', code=400, http_status=400)

  user = User.query.filter_by(id=uid).first()
  if not user or user.status != 0:
    return error('未找到该用户', code=404, http_status=404)

  if user.name == new_name:
    return jsonify('Moe Moe')

  if (user.moemoepoint or 0) < 17:
    return error('更改用户名需要 17 萌萌点, 您的萌萌点不足', code=233, http_status=400)

  if User.query.filter(User.name == new_name, User.id != uid).first():
    return error('您的用户名已经被使用, 请换一个', code=400, http_status=400)

  user.name = new_name
  user.moemoepoint = (user.moemoepoint or 0) - 17
  db.session.commit()
  return jsonify('Moe Moe')


_PASSWORD_PUT_PATTERN = re.compile(
  r'^(?=.*[a-zA-Z])(?=.*[0-9])[\w!@#$%^&*()+=\\/-]{6,107}$',
)
_PASSWORD_FORMAT_MSG = (
  '密码的长度为 6 到 107 位，必须包含至少一个英文字符和一个数字，'
  '可以选择性的包含 @!#$%^&*()_-+=\\ 等特殊字符'
)


@kun_user_bp.route('/password', methods=['PUT'])
def update_password():
  """
  PUT /api/user/password
  body: { oldPassword, newPassword }
  与 server/api/user/password.put.ts 对齐：bcrypt cost 7
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)

  data = request.get_json() or {}
  old_pw = data.get('oldPassword') or ''
  new_pw = data.get('newPassword') or ''

  if not _PASSWORD_PUT_PATTERN.match(old_pw):
    return error(f'旧密码格式错误，{_PASSWORD_FORMAT_MSG}', code=400, http_status=400)
  if not _PASSWORD_PUT_PATTERN.match(new_pw):
    return error(f'新密码格式错误，{_PASSWORD_FORMAT_MSG}', code=400, http_status=400)

  user = User.query.filter_by(id=uid).first()
  if not user or user.status != 0:
    return error('未找到用户', code=404, http_status=404)

  if not user.check_password(old_pw):
    return error('旧密码错误', code=400, http_status=400)

  new_hash = bcrypt.hashpw(
    new_pw.encode('utf-8'),
    bcrypt.gensalt(rounds=7),
  ).decode('utf-8')
  user.password = new_hash
  db.session.commit()
  return jsonify('Moe Moe')


@kun_user_bp.route('/<int:uid>/comments', methods=['GET'])
def list_user_comments(uid: int):
  """
  GET /api/user/<uid>/comments?page=&limit=&userId=&type=
  type: comment_created | comment_target | comment_like
  """
  try:
    parsed = _parse_user_list_query(uid)
    if parsed is None:
      return error('参数错误', code=400, http_status=400)
    page, limit, skip = parsed
    ctype = (request.args.get('type') or '').strip()

    if ctype == 'comment_created':
      q = TopicComment.query.filter_by(user_id=uid)
    elif ctype == 'comment_target':
      q = TopicComment.query.filter_by(target_user_id=uid)
    elif ctype == 'comment_like':
      liked_cids = [
        row[0]
        for row in db.session.query(TopicCommentLike.topic_comment_id)
        .filter_by(user_id=uid)
        .distinct()
        .all()
      ]
      if not liked_cids:
        return jsonify({'comments': [], 'totalCount': 0})
      q = TopicComment.query.filter(TopicComment.id.in_(liked_cids))
    else:
      return error('无效的类型参数', code=400, http_status=400)

    total = q.count()
    rows = q.order_by(TopicComment.created.desc()).offset(skip).limit(limit).all()
    comments = [
      {
        'topicId': c.topic_id,
        'content': c.content,
        'created': c.created.isoformat() if c.created else None,
      }
      for c in rows
    ]
    return jsonify({'comments': comments, 'totalCount': total})
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_user_bp.route('/avatar', methods=['POST'])
def update_avatar():
  """
  POST /api/user/avatar
  form-data: avatar=<file>
  return: avatar link (string)
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)

  user = User.query.filter_by(id=uid).first()
  if not user or user.status != 0:
    return error('用户不存在或已被禁用', code=401, http_status=401)

  avatar_file = request.files.get('avatar')
  if not avatar_file:
    return error('读取图片错误', code=400, http_status=400)

  avatar_bytes = avatar_file.read()
  if not avatar_bytes:
    return error('读取图片错误', code=400, http_status=400)

  # 直接落盘到项目 public，保证前端可通过 /avatar/... 访问
  # current_app.root_path: <repo>/backend/app
  # 项目根目录应为 parents[1] => <repo>
  project_root = Path(current_app.root_path).resolve().parents[1]
  avatar_dir = project_root / 'public' / 'avatar' / f'user_{uid}'
  avatar_dir.mkdir(parents=True, exist_ok=True)

  avatar_path = avatar_dir / 'avatar.webp'
  avatar_mini_path = avatar_dir / 'avatar-100.webp'

  # 为了保证接口可用：即便上传源不是 webp，也先按 webp 文件名存储
  # 前端依赖 avatar.webp -> avatar-100.webp 的约定
  avatar_path.write_bytes(avatar_bytes)
  avatar_mini_path.write_bytes(avatar_bytes)

  image_link = f'/avatar/user_{uid}/avatar.webp'
  user.avatar = image_link
  db.session.commit()

  return jsonify(image_link)


@kun_user_bp.route('/status', methods=['GET'])
def user_status():
  """
  GET /api/user/status
  返回顶部栏所需用户状态
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)

  user = User.query.filter_by(id=uid).first()
  if not user:
    return error('未找到该用户', code=404, http_status=404)

  from app.routes.kun_message import user_has_new_message

  response_data = {
    'moemoepoints': user.moemoepoint or 0,
    'isCheckIn': (user.daily_check_in == 1),
    'hasNewMessage': user_has_new_message(uid),
  }
  return jsonify(response_data)


def _actor_from_cookie():
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return None, error('用户登录失效', code=205, http_status=401)
  u = User.query.get(uid)
  if not u or u.status != 0:
    return None, error('用户不存在或已被禁用', code=401, http_status=401)
  return u, None


@kun_user_bp.route('/<int:uid>/ban', methods=['PUT'])
def ban_user(uid):
  """
  PUT /api/user/:uid/ban?userId=
  与 server/api/user/[uid]/ban.put.ts 一致：toggle status 0/1，需 role>=2。
  """
  actor, err = _actor_from_cookie()
  if err:
    return err
  if int(actor.role) < 2:
    return error('您没有权限操作用户', code=403, http_status=403)

  qid = request.args.get('userId', type=int)
  target_id = qid if qid is not None else uid
  if qid is not None and qid != uid:
    return error('参数不一致', code=400, http_status=400)

  target = User.query.get(target_id)
  if not target:
    return error('用户不存在', code=404, http_status=404)
  if int(target.role) > 1:
    return error('不能操作一个管理员', code=400, http_status=400)

  cur = int(target.status or 0)
  target.status = 0 if cur == 1 else 1
  db.session.commit()
  return jsonify('Moemoe update user status successfully!')


@kun_user_bp.route('/<int:uid>/permanent', methods=['DELETE'])
def delete_user_permanent(uid):
  """
  DELETE /api/user/:uid/permanent?userId=
  与 server/api/user/[uid]/permanent.delete.ts 一致：需 role>2（即 >=3）。
  """
  actor, err = _actor_from_cookie()
  if err:
    return err
  if int(actor.role) <= 2:
    return error('您没有权限删除用户', code=403, http_status=403)

  qid = request.args.get('userId', type=int)
  target_id = qid if qid is not None else uid
  if qid is not None and qid != uid:
    return error('参数不一致', code=400, http_status=400)

  target = User.query.get(target_id)
  if not target:
    return error('用户不存在', code=404, http_status=404)
  if int(target.role) > 1:
    return error('不能删除一个管理员', code=400, http_status=400)

  try:
    purge_user_for_permanent_delete(target_id)
    db.session.delete(target)
    db.session.commit()
  except SQLAlchemyError as e:
    db.session.rollback()
    current_app.logger.exception('永久删除用户失败 user_id=%s', target_id)
    return error('删除用户失败，请查看服务端日志', code=500, http_status=500)

  return jsonify('Moemoe delete user successfully!')

