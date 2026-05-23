"""
邮箱验证码（对齐 Nitro useStorage + sendVerificationCodeEmail）
开发环境：注册发码时在终端打印验证码；未配置 SMTP 时仍返回 salt 便于联调。
"""

from __future__ import annotations

import os
import secrets
import smtplib
import threading
import time
from email.mime.text import MIMEText
from email.utils import formataddr

_CODE_CHARSET = '023456789abcdefghjkmnopqrstuvwxyzABCDEFGHJKLMNOPQRSTUVWXYZ'

_lock = threading.RLock()
# key -> (value: str, expire_monotonic: float)
_store: dict[str, tuple[str, float]] = {}


def _monotonic_now() -> float:
  return time.monotonic()


def _purge_expired_locked() -> None:
  t = _monotonic_now()
  dead = [k for k, (_, exp) in _store.items() if exp <= t]
  for k in dead:
    del _store[k]


def generate_random_code(length: int = 7) -> str:
  return ''.join(secrets.choice(_CODE_CHARSET) for _ in range(length))


def should_log_verification_code(app) -> bool:
  """开发联调：是否在终端输出验证码（默认跟随 DEBUG，可用环境变量强制开启）。"""
  env = os.environ.get('KUN_LOG_VERIFICATION_CODE', '').strip().lower()
  if env in ('1', 'true', 'yes', 'on'):
    return True
  if env in ('0', 'false', 'no', 'off'):
    return False
  return bool(app.config.get('LOG_VERIFICATION_CODE', app.debug))


def log_register_verification_code(app, email: str, code: str, salt: str) -> None:
  """注册发码：写入 Flask 日志并 print 到运行 python run.py 的终端。"""
  if not should_log_verification_code(app):
    return
  msg = (
    f'[注册验证码] email={email} code={code} '
    f'salt(前8)={salt[:8]} — 有效期 10 分钟'
  )
  app.logger.warning(msg)
  print(msg, flush=True)


def rate_throttled(email: str, ip: str, ttl_sec: float = 30.0) -> bool:
  """若邮箱或 IP 在冷却期内，返回 True（应拒绝发送）。"""
  k1 = f'limit:email:{email.lower()}'
  k2 = f'limit:ip:{ip or "unknown"}'
  now = _monotonic_now()
  with _lock:
    _purge_expired_locked()
    if k1 in _store and _store[k1][1] > now:
      return True
    if k2 in _store and _store[k2][1] > now:
      return True
    return False


def rate_mark_sent(email: str, ip: str, ttl_sec: float = 30.0) -> None:
  now = _monotonic_now()
  exp = now + ttl_sec
  with _lock:
    _store[f'limit:email:{email.lower()}'] = ('1', exp)
    _store[f'limit:ip:{ip or "unknown"}'] = ('1', exp)


def set_verification_code(salt: str, email: str, code: str, ttl_sec: int = 600) -> None:
  """与 Nitro 一致：键为 ``{salt}:{email}``"""
  key = f'{salt}:{email.lower()}'
  with _lock:
    _purge_expired_locked()
    _store[key] = (code, _monotonic_now() + float(ttl_sec))


def verify_verification_code(salt: str, email: str, user_code: str) -> bool:
  key = f'{salt}:{email.lower()}'
  with _lock:
    _purge_expired_locked()
    row = _store.get(key)
    if not row:
      return False
    code, exp = row
    if exp <= _monotonic_now():
      del _store[key]
      return False
    return user_code == code


def remove_verification_code(salt: str, email: str) -> None:
  key = f'{salt}:{email.lower()}'
  with _lock:
    _store.pop(key, None)


def _send_smtp_text(app, to_addr: str, subject: str, body: str) -> None:
  host = app.config.get('MAIL_HOST')
  port = int(app.config.get('MAIL_PORT') or 587)
  user = app.config.get('MAIL_USERNAME')
  password = app.config.get('MAIL_PASSWORD')
  mail_from = app.config.get('MAIL_FROM') or 'KUN Visual Novel'

  if not host or not user or not password:
    raise RuntimeError('mail_not_configured')

  msg = MIMEText(body, 'plain', 'utf-8')
  msg['Subject'] = subject
  msg['From'] = formataddr((str(mail_from), user))
  msg['To'] = to_addr

  with smtplib.SMTP(host, port, timeout=30) as smtp:
    smtp.starttls()
    smtp.login(user, password)
    smtp.send_message(msg)


def send_reset_email_verification(app, email: str, code: str) -> None:
  body = (
    f'Your verification code is\n{code}\n'
    'You are resetting your email. Please do not disclose this verification code.'
  )
  _send_smtp_text(
    app,
    email,
    'KUN Visual Novel Verification Code',
    body,
  )


def send_register_email_verification(app, email: str, code: str) -> None:
  body = (
    f'Your verification code is\n{code}\n'
    'You are registering KUN Visual Novel. Please do not disclose this verification code.'
  )
  _send_smtp_text(
    app,
    email,
    'KUN Visual Novel Verification Code',
    body,
  )
