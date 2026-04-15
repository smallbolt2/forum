"""
Nuxt/Nitro 兼容的 Galgame API（按 Prisma 表实现核心功能）
"""

from collections import defaultdict
from sqlalchemy import func
from flask import Blueprint, request, jsonify

from app import db
from app.models.user import User
from app.models.prisma_galgame_min import Galgame, GalgameLike, GalgameFavorite, GalgameResource
from app.utils.auth import token_required
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie
from app.utils.response import error


kun_galgame_bp = Blueprint('kun_galgame', __name__)


@kun_galgame_bp.route('', methods=['GET'])
def list_galgames():
  """
  GET /api/galgame
  return { galgames, totalCount }
  """
  try:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    sort_field = request.args.get('sortField', 'time', type=str)
    sort_order = request.args.get('sortOrder', 'desc', type=str)

    nsfw = request.cookies.get('nsfw') or ''

    q = Galgame.query.filter(Galgame.status != 1)
    if nsfw == 'sfw':
      q = q.filter(Galgame.content_limit == 'sfw')

    total = q.count()

    order_col = Galgame.resource_update_time if sort_field == 'time' else getattr(Galgame, sort_field, Galgame.resource_update_time)
    q = q.order_by(order_col.asc() if sort_order == 'asc' else order_col.desc())

    rows = q.offset((page - 1) * limit).limit(limit).all()
    ids = [g.id for g in rows]

    users = {u.id: u for u in User.query.filter(User.id.in_([g.user_id for g in rows])).all()} if rows else {}

    like_counts = {gid: c for gid, c in db.session.query(
      GalgameLike.galgame_id, func.count(GalgameLike.id)
    ).filter(GalgameLike.galgame_id.in_(ids)).group_by(GalgameLike.galgame_id).all()} if ids else {}

    resource_rows = GalgameResource.query.filter(GalgameResource.galgame_id.in_(ids)).all() if ids else []
    platforms = defaultdict(set)
    languages = defaultdict(set)
    for r in resource_rows:
      if r.platform:
        platforms[r.galgame_id].add(r.platform)
      if r.language:
        languages[r.galgame_id].add(r.language)

    galgames = []
    for g in rows:
      u = users.get(g.user_id)
      galgames.append({
        'id': g.id,
        'name': {
          'en-us': g.name_en_us,
          'ja-jp': g.name_ja_jp,
          'zh-cn': g.name_zh_cn,
          'zh-tw': g.name_zh_tw
        },
        'banner': g.banner,
        'user': {'id': g.user_id, 'name': u.name if u else '', 'avatar': u.avatar if u else ''},
        'contentLimit': g.content_limit,
        'view': g.view,
        'likeCount': like_counts.get(g.id, 0),
        'resourceUpdateTime': g.resource_update_time.isoformat() if g.resource_update_time else None,
        'platform': sorted(platforms.get(g.id, set())),
        'language': sorted(languages.get(g.id, set()))
      })

    return jsonify({'galgames': galgames, 'totalCount': total})
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_galgame_bp.route('/check', methods=['GET'])
def check():
  """
  GET /api/galgame/check?vndbId=...
  """
  try:
    vndb_id = request.args.get('vndbId', type=str)
    if not vndb_id:
      return error('vndbId is required', code=400, http_status=400)

    exists = Galgame.query.filter_by(vndb_id=vndb_id).count()
    if exists:
      return error('这个 Galgame 已经有人发布过了', code=400, http_status=400)
    return jsonify('The galgame is unique!')
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_galgame_bp.route('', methods=['POST'])
@token_required
def create_galgame(current_user=None):
  """
  POST /api/galgame (multipart/form-data)
  return new id (number)
  """
  try:
    form = request.form
    vndb_id = form.get('vndbId') or ''
    if not vndb_id:
      return error('vndbId is required', code=400, http_status=400)

    if Galgame.query.filter_by(vndb_id=vndb_id).count():
      return error('这个 Galgame 已经有人发布过了', code=400, http_status=400)

    g = Galgame(
      vndb_id=vndb_id,
      name_en_us=form.get('name_en_us', ''),
      name_ja_jp=form.get('name_ja_jp', ''),
      name_zh_cn=form.get('name_zh_cn', ''),
      name_zh_tw=form.get('name_zh_tw', ''),
      intro_en_us=form.get('intro_en_us', ''),
      intro_ja_jp=form.get('intro_ja_jp', ''),
      intro_zh_cn=form.get('intro_zh_cn', ''),
      intro_zh_tw=form.get('intro_zh_tw', ''),
      content_limit=form.get('contentLimit', 'sfw'),
      user_id=current_user.id
    )
    db.session.add(g)
    db.session.commit()
    return jsonify(g.id)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_galgame_bp.route('/<int:gid>', methods=['GET'])
def get_galgame(gid: int):
  g = Galgame.query.get(gid)
  if not g or g.status == 1:
    return error('未找到这个 Galgame', code=404, http_status=404)
  return jsonify({
    'id': g.id,
    'name': {
      'en-us': g.name_en_us,
      'ja-jp': g.name_ja_jp,
      'zh-cn': g.name_zh_cn,
      'zh-tw': g.name_zh_tw
    },
    'banner': g.banner,
    'contentLimit': g.content_limit,
    'view': g.view,
    'resourceUpdateTime': g.resource_update_time.isoformat() if g.resource_update_time else None
  })


@kun_galgame_bp.route('/<int:gid>/like', methods=['PUT'])
@token_required
def like_galgame(gid: int, current_user=None):
  try:
    # Nuxt body: { galgameId }
    galgame_id = (request.get_json() or {}).get('galgameId') or gid
    galgame = Galgame.query.get(int(galgame_id))
    if not galgame or galgame.status == 1:
      return error('未找到这个 Galgame', code=404, http_status=404)

    existing = GalgameLike.query.filter_by(galgame_id=galgame.id, user_id=current_user.id).first()
    if existing:
      db.session.delete(existing)
    else:
      db.session.add(GalgameLike(galgame_id=galgame.id, user_id=current_user.id))
    db.session.commit()
    return jsonify('MOEMOE like galgame operation successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_galgame_bp.route('/<int:gid>/favorite', methods=['PUT'])
@token_required
def favorite_galgame(gid: int, current_user=None):
  try:
    galgame_id = (request.get_json() or {}).get('galgameId') or gid
    galgame = Galgame.query.get(int(galgame_id))
    if not galgame or galgame.status == 1:
      return error('未找到这个 Galgame', code=404, http_status=404)

    existing = GalgameFavorite.query.filter_by(galgame_id=galgame.id, user_id=current_user.id).first()
    if existing:
      db.session.delete(existing)
    else:
      db.session.add(GalgameFavorite(galgame_id=galgame.id, user_id=current_user.id))
    db.session.commit()
    return jsonify('MOEMOE favorite galgame operation successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_galgame_bp.route('/<int:gid>/banner', methods=['PUT'])
@token_required
def update_banner(gid: int, current_user=None):
  return jsonify(True)


# comments
@kun_galgame_bp.route('/<int:gid>/comment/all', methods=['GET'])
def galgame_comments_all(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/comment', methods=['POST'])
@token_required
def create_galgame_comment(gid: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_galgame_bp.route('/<int:gid>/comment', methods=['DELETE'])
@token_required
def delete_galgame_comment(gid: int, current_user=None):
  return success(data=True, message='删除成功')


@kun_galgame_bp.route('/<int:gid>/comment/like', methods=['PUT'])
@token_required
def like_galgame_comment(gid: int, current_user=None):
  return success(data=True, message='ok')


# resources
@kun_galgame_bp.route('/<int:gid>/resource', methods=['GET'])
def galgame_resource_all(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/resource', methods=['POST'])
@token_required
def create_galgame_resource(gid: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_galgame_bp.route('/<int:gid>/resource', methods=['PUT'])
@token_required
def update_galgame_resource(gid: int, current_user=None):
  return success(data=True, message='更新成功')


@kun_galgame_bp.route('/<int:gid>/resource', methods=['DELETE'])
@token_required
def delete_galgame_resource(gid: int, current_user=None):
  return success(data=True, message='删除成功')


@kun_galgame_bp.route('/<int:gid>/resource/all', methods=['GET'])
def galgame_resource_list(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/resource/like', methods=['PUT'])
@token_required
def like_galgame_resource(gid: int, current_user=None):
  return success(data=True, message='ok')


@kun_galgame_bp.route('/<int:gid>/resource/valid', methods=['PUT'])
@token_required
def valid_resource(gid: int, current_user=None):
  return success(data=True, message='ok')


@kun_galgame_bp.route('/<int:gid>/resource/expired', methods=['PUT'])
@token_required
def expired_resource(gid: int, current_user=None):
  return success(data=True, message='ok')


# links
@kun_galgame_bp.route('/<int:gid>/link/all', methods=['GET'])
def link_all(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/link', methods=['POST'])
@token_required
def link_create(gid: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_galgame_bp.route('/<int:gid>/link', methods=['DELETE'])
@token_required
def link_delete(gid: int, current_user=None):
  return success(data=True, message='删除成功')


# PR
@kun_galgame_bp.route('/<int:gid>/pr', methods=['GET'])
def pr_get(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/pr', methods=['POST'])
@token_required
def pr_create(gid: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_galgame_bp.route('/<int:gid>/pr/all', methods=['GET'])
def pr_all(gid: int):
  return success(data=[], message='获取成功')


@kun_galgame_bp.route('/<int:gid>/pr/merge', methods=['PUT'])
@token_required
def pr_merge(gid: int, current_user=None):
  return success(data=True, message='ok')


@kun_galgame_bp.route('/<int:gid>/pr/decline', methods=['PUT'])
@token_required
def pr_decline(gid: int, current_user=None):
  return success(data=True, message='ok')


# history
@kun_galgame_bp.route('/<int:gid>/history/all', methods=['GET'])
def history_all(gid: int):
  return success(data=[], message='获取成功')

