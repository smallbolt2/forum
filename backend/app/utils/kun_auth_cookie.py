from flask import request, current_app
import jwt


def get_uid_from_refresh_cookie():
  """
  Nuxt 侧使用 cookie `kungalgame-moemoe-refresh-token`。
  这里解析 JWT，返回 uid；解析失败返回 None。
  """
  token = request.cookies.get('kungalgame-moemoe-refresh-token')
  if not token:
    return None
  try:
    payload = jwt.decode(
      token,
      current_app.config['SECRET_KEY'],
      algorithms=['HS256'],
      options={"verify_iss": False, "verify_aud": False}
    )
    return payload.get('uid')
  except Exception:
    return None

