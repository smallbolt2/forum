"""
话题编辑器内嵌图片上传（兼容原 Nitro POST /api/image/topic）
"""

import re
import time
from pathlib import Path

from flask import Blueprint, request, jsonify, current_app

from app import db
from app.models.user import User
from app.utils.response import error
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie


kun_image_bp = Blueprint('kun_image', __name__)

# 与 app/config/upload.ts 中 KUN_VISUAL_NOVEL_USER_DAILY_UPLOAD_IMAGE_LIMIT 一致
KUN_USER_DAILY_UPLOAD_IMAGE_LIMIT = 50
# 原 Nitro 校验：未压缩前小于 10MB
MAX_TOPIC_IMAGE_BYTES = 10 * 1024 * 1024


def _safe_filename_segment(name: str, max_len: int = 50) -> str:
  s = re.sub(r'[^a-zA-Z0-9_-]', '_', (name or '').strip()) or 'user'
  return s[:max_len]


@kun_image_bp.route('/topic', methods=['POST'])
def upload_topic_image():
  """
  POST /api/image/topic
  form-data: image=<file>
  成功：返回图片相对路径字符串（JSON 字符串），与 $fetch 解析一致
  """
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return error('用户登录失效', code=205, http_status=401)

  user = User.query.filter_by(id=uid).first()
  if not user or user.status != 0:
    return error('用户不存在或已被禁用', code=401, http_status=401)

  if (user.daily_image_count or 0) >= KUN_USER_DAILY_UPLOAD_IMAGE_LIMIT:
    return error(
      f'您今日上传图片已达到 {KUN_USER_DAILY_UPLOAD_IMAGE_LIMIT} 张上限',
      code=233,
      http_status=400,
    )

  image_file = request.files.get('image')
  if not image_file:
    return error('读取图片数据错误', code=400, http_status=400)

  raw = image_file.read()
  if not raw:
    return error('读取图片数据错误', code=400, http_status=400)
  if len(raw) > MAX_TOPIC_IMAGE_BYTES:
    return error('图片大小应该小于 10MB', code=400, http_status=400)

  base = _safe_filename_segment(user.name)
  new_name = f'{base}-{int(time.time() * 1000)}.webp'

  project_root = Path(current_app.root_path).resolve().parents[1]
  topic_dir = project_root / 'public' / 'topic' / f'user_{uid}'
  topic_dir.mkdir(parents=True, exist_ok=True)

  out_path = topic_dir / new_name
  out_path.write_bytes(raw)

  rel = f'/topic/user_{uid}/{new_name}'
  user.daily_image_count = (user.daily_image_count or 0) + 1
  db.session.commit()

  return jsonify(rel)
