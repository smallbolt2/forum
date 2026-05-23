"""
Nuxt/Nitro 兼容的 Activity API

映射自 server/api/activity/*
"""

import json

from flask import Blueprint, request

from app.utils.activity_timeline import get_activity_timeline_data
from app.utils.response import success, error

kun_activity_bp = Blueprint('kun_activity', __name__)


def _parse_nsfw_cookie() -> bool:
  """与前端 KUNGalgameSettings.showKUNGalgameContentLimit 对齐，默认仅 SFW"""
  raw = request.cookies.get('KUNGalgameSettings')
  if not raw:
    return True
  try:
    settings = json.loads(raw)
    return settings.get('showKUNGalgameContentLimit', 'sfw') == 'sfw'
  except (json.JSONDecodeError, TypeError):
    return True


@kun_activity_bp.route('/timeline', methods=['GET'])
def activity_timeline():
  page = request.args.get('page', 1, type=int)
  limit = request.args.get('limit', 50, type=int)

  if page < 1 or page > 9999999:
    return error('页码无效', code=400, http_status=400)
  if limit < 1 or limit > 50:
    return error('每页条数须在 1–50 之间', code=400, http_status=400)

  is_sfw = _parse_nsfw_cookie()
  payload = get_activity_timeline_data(page, limit, is_sfw=is_sfw)

  return success(data=payload, message='获取成功')
