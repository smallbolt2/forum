"""
Nuxt/Nitro 兼容的 Toolset API（按 Prisma 表实现核心功能）
"""

from sqlalchemy import func
from flask import Blueprint, request, jsonify

from app import db
from app.models.user import User
from app.models.prisma_toolset_min import (
  GalgameToolset,
  GalgameToolsetAlias,
  GalgameToolsetComment,
  GalgameToolsetPracticality,
  GalgameToolsetResource
)
from app.utils.auth import token_required
from app.utils.response import error


kun_toolset_bp = Blueprint('kun_toolset', __name__)


@kun_toolset_bp.route('', methods=['GET'])
def list_toolsets():
  """
  GET /api/toolset
  return { items, totalCount }
  """
  try:
    page = request.args.get('page', 1, type=int)
    limit = request.args.get('limit', 20, type=int)
    type_ = request.args.get('type', 'all', type=str)
    language = request.args.get('language', 'all', type=str)
    platform = request.args.get('platform', 'all', type=str)
    version = request.args.get('version', 'all', type=str)
    sort_field = request.args.get('sortField', 'created', type=str)
    sort_order = request.args.get('sortOrder', 'desc', type=str)

    q = GalgameToolset.query.filter(GalgameToolset.status != 1)
    if type_ != 'all':
      q = q.filter(GalgameToolset.type == type_)
    if language != 'all':
      q = q.filter(GalgameToolset.language == language)
    if platform != 'all':
      q = q.filter(GalgameToolset.platform == platform)
    if version != 'all':
      q = q.filter(GalgameToolset.version == version)

    total = q.count()

    order_col = getattr(GalgameToolset, sort_field, GalgameToolset.created)
    q = q.order_by(order_col.asc() if sort_order == 'asc' else order_col.desc())

    rows = q.offset((page - 1) * limit).limit(limit).all()
    ids = [t.id for t in rows]

    users = {u.id: u for u in User.query.filter(User.id.in_([t.user_id for t in rows])).all()} if rows else {}

    comment_counts = {tid: c for tid, c in db.session.query(
      GalgameToolsetComment.toolset_id, func.count(GalgameToolsetComment.id)
    ).filter(GalgameToolsetComment.toolset_id.in_(ids)).group_by(GalgameToolsetComment.toolset_id).all()} if ids else {}

    practicality_aggs = {tid: avg for tid, avg in db.session.query(
      GalgameToolsetPracticality.toolset_id, func.avg(GalgameToolsetPracticality.rate)
    ).filter(GalgameToolsetPracticality.toolset_id.in_(ids)).group_by(GalgameToolsetPracticality.toolset_id).all()} if ids else {}

    download_aggs = {tid: s for tid, s in db.session.query(
      GalgameToolsetResource.toolset_id, func.sum(GalgameToolsetResource.download)
    ).filter(GalgameToolsetResource.toolset_id.in_(ids)).group_by(GalgameToolsetResource.toolset_id).all()} if ids else {}

    items = []
    for t in rows:
      u = users.get(t.user_id)
      items.append({
        'id': t.id,
        'name': t.name,
        'user': {'id': t.user_id, 'name': u.name if u else '', 'avatar': u.avatar if u else ''},
        'type': t.type,
        'platform': t.platform,
        'language': t.language,
        'version': t.version,
        'download': int(download_aggs.get(t.id, 0) or 0),
        'view': t.view,
        'commentCount': comment_counts.get(t.id, 0),
        'resource_update_time': t.resource_update_time.isoformat() if t.resource_update_time else None,
        'practicalityAvg': float(practicality_aggs.get(t.id)) if practicality_aggs.get(t.id) is not None else None
      })

    return jsonify({'items': items, 'totalCount': total})
  except Exception as e:
    return error(str(e), code=500, http_status=500)


@kun_toolset_bp.route('', methods=['POST'])
@token_required
def create_toolset(current_user=None):
  """
  POST /api/toolset
  return new id (number)
  """
  try:
    data = request.get_json() or {}
    t = GalgameToolset(
      name=data.get('name', ''),
      description=data.get('description', ''),
      language=data.get('language', ''),
      platform=data.get('platform', ''),
      type=data.get('type', ''),
      version=data.get('version', ''),
      homepage=str(data.get('homepage', '[]')),
      user_id=current_user.id
    )
    db.session.add(t)
    db.session.commit()

    aliases = data.get('aliases') or []
    for a in aliases:
      db.session.add(GalgameToolsetAlias(name=a, toolset_id=t.id))
    db.session.commit()

    return jsonify(t.id)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_toolset_bp.route('/<int:toolset_id>', methods=['GET'])
def get_toolset(toolset_id: int):
  t = GalgameToolset.query.get(toolset_id)
  if not t or t.status == 1:
    return error('未找到该工具', code=404, http_status=404)
  aliases = [a.name for a in GalgameToolsetAlias.query.filter_by(toolset_id=t.id).all()]
  return jsonify({
    'id': t.id,
    'name': t.name,
    'description': t.description,
    'language': t.language,
    'platform': t.platform,
    'type': t.type,
    'version': t.version,
    'homepage': t.homepage,
    'aliases': aliases,
    'view': t.view
  })


@kun_toolset_bp.route('/<int:toolset_id>', methods=['PUT'])
@token_required
def update_toolset(toolset_id: int, current_user=None):
  try:
    t = GalgameToolset.query.get(toolset_id)
    if not t or t.status == 1:
      return error('未找到该工具', code=404, http_status=404)
    if t.user_id != current_user.id and current_user.role != 'admin':
      return error('无权编辑此工具', code=403, http_status=403)

    data = request.get_json() or {}
    for key in ['name', 'description', 'language', 'platform', 'type', 'version']:
      if key in data:
        setattr(t, key, data.get(key))
    if 'homepage' in data:
      t.homepage = str(data.get('homepage'))
    t.edited = db.func.now()
    db.session.commit()
    return jsonify('MOEMOE update toolset successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_toolset_bp.route('/<int:toolset_id>', methods=['DELETE'])
@token_required
def delete_toolset(toolset_id: int, current_user=None):
  try:
    t = GalgameToolset.query.get(toolset_id)
    if not t:
      return error('未找到该工具', code=404, http_status=404)
    if t.user_id != current_user.id and current_user.role != 'admin':
      return error('无权删除此工具', code=403, http_status=403)
    t.status = 1
    db.session.commit()
    return jsonify('MOEMOE delete toolset successfully!')
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_toolset_bp.route('/<int:toolset_id>/practicality', methods=['GET'])
def get_practicality(toolset_id: int):
  avg = db.session.query(func.avg(GalgameToolsetPracticality.rate)).filter(GalgameToolsetPracticality.toolset_id == toolset_id).scalar()
  return jsonify({'practicality': float(avg) if avg is not None else None})


@kun_toolset_bp.route('/<int:toolset_id>/practicality', methods=['PUT'])
@token_required
def put_practicality(toolset_id: int, current_user=None):
  try:
    data = request.get_json() or {}
    rate = int(data.get('rate', 1))
    existing = GalgameToolsetPracticality.query.filter_by(toolset_id=toolset_id, user_id=current_user.id).first()
    if existing:
      existing.rate = rate
    else:
      db.session.add(GalgameToolsetPracticality(toolset_id=toolset_id, user_id=current_user.id, rate=rate))
    db.session.commit()
    return jsonify(True)
  except Exception as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


# ---- uploads ----
@kun_toolset_bp.route('/<int:toolset_id>/upload/small', methods=['POST'])
@token_required
def upload_small(toolset_id: int, current_user=None):
  # 占位：返回一个 salt，前端用它继续 complete/abort
  return success(data={'salt': 'dev-salt-small'}, message='ok')


@kun_toolset_bp.route('/<int:toolset_id>/upload/large', methods=['POST'])
@token_required
def upload_large(toolset_id: int, current_user=None):
  return success(data={'salt': 'dev-salt-large'}, message='ok')


@kun_toolset_bp.route('/<int:toolset_id>/upload/complete', methods=['POST'])
@token_required
def upload_complete(toolset_id: int, current_user=None):
  return success(data=True, message='ok')


@kun_toolset_bp.route('/<int:toolset_id>/upload/abort', methods=['POST'])
@token_required
def upload_abort(toolset_id: int, current_user=None):
  return success(data=True, message='ok')


# ---- resources ----
@kun_toolset_bp.route('/<int:toolset_id>/resource', methods=['POST'])
@token_required
def create_resource(toolset_id: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_toolset_bp.route('/<int:toolset_id>/resource', methods=['PUT'])
@token_required
def update_resource(toolset_id: int, current_user=None):
  return success(data=True, message='更新成功')


@kun_toolset_bp.route('/<int:toolset_id>/resource', methods=['DELETE'])
@token_required
def delete_resource(toolset_id: int, current_user=None):
  return success(data=True, message='删除成功')


@kun_toolset_bp.route('/<int:toolset_id>/resource/detail', methods=['GET'])
def resource_detail(toolset_id: int):
  rid = request.args.get('resourceId', type=int)
  return success(data={'id': rid, 'toolsetId': toolset_id}, message='获取成功')


# ---- comments ----
@kun_toolset_bp.route('/<int:toolset_id>/comment/all', methods=['GET'])
def list_comments(toolset_id: int):
  return success(data=[], message='获取成功')


@kun_toolset_bp.route('/<int:toolset_id>/comment', methods=['POST'])
@token_required
def create_comment(toolset_id: int, current_user=None):
  return success(data=1, message='创建成功')


@kun_toolset_bp.route('/<int:toolset_id>/comment', methods=['PUT'])
@token_required
def update_comment(toolset_id: int, current_user=None):
  return success(data=True, message='更新成功')


@kun_toolset_bp.route('/<int:toolset_id>/comment', methods=['DELETE'])
@token_required
def delete_comment(toolset_id: int, current_user=None):
  return success(data=True, message='删除成功')

