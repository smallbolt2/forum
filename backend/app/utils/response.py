from flask import jsonify


def success(data=None, message='成功', code=200, http_status=200):
  """
  统一成功响应：
  {
    "code": code,
    "message": message,
    "data": ...
  }
  """
  return jsonify({
    'code': code,
    'message': message,
    'data': data
  }), http_status


def error(message='错误', code=500, http_status=500, data=None):
  """
  统一错误响应
  """
  return jsonify({
    'code': code,
    'message': message,
    'data': data
  }), http_status

