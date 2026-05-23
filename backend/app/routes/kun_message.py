"""
Nuxt/Nitro 兼容的消息 API — server/api/message/*
"""

from datetime import datetime

from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from app import db
from app.models.user import User
from app.models.prisma_message import Message, SystemMessage
from app.models.prisma_chat import (
  ChatRoom,
  ChatRoomParticipant,
  ChatMessage,
  ChatMessageReadBy,
)
from app.utils.response import error
from app.utils.kun_auth_cookie import get_uid_from_refresh_cookie
from app.utils.auth import token_required
from app.utils.kun_message_util import generate_room_id

kun_message_bp = Blueprint('kun_message', __name__)


def _uid_from_cookie():
  uid = get_uid_from_refresh_cookie()
  if not uid:
    return None, error('用户登录失效', code=205, http_status=401)
  return uid, None


def _user_brief(user: User | None) -> dict:
  if not user:
    return {'id': 0, 'name': '', 'avatar': ''}
  return {'id': user.id, 'name': user.name, 'avatar': user.avatar or ''}


def _iso(dt):
  return dt.isoformat() if dt else ''


def _format_message(row: Message, sender: User | None) -> dict:
  return {
    'id': row.id,
    'sender': _user_brief(sender),
    'receiverUid': row.receiver_id,
    'link': row.link or '',
    'content': row.content or '',
    'status': row.status,
    'type': row.type,
    'created': _iso(row.created),
  }


@kun_message_bp.route('', methods=['GET'])
def list_messages():
  """GET /api/message — 通知消息列表"""
  uid, err = _uid_from_cookie()
  if err:
    return err

  page = request.args.get('page', 1, type=int)
  limit = min(request.args.get('limit', 30, type=int), 30)
  sort_order = request.args.get('sortOrder', 'desc')
  msg_type = (request.args.get('type') or '').strip()

  q = Message.query.filter_by(receiver_id=uid)
  if msg_type:
    q = q.filter_by(type=msg_type)

  total = q.count()
  if sort_order == 'asc':
    q = q.order_by(Message.created.asc())
  else:
    q = q.order_by(Message.created.desc())

  rows = q.offset((page - 1) * limit).limit(limit).all()
  sender_ids = {r.sender_id for r in rows}
  senders = {
    u.id: u for u in User.query.filter(User.id.in_(sender_ids)).all()
  } if sender_ids else {}

  messages = [_format_message(r, senders.get(r.sender_id)) for r in rows]
  return jsonify({'messages': messages, 'totalCount': total})


@kun_message_bp.route('/system/read', methods=['PUT'])
@token_required
def read_all_notice_messages(current_user=None):
  """PUT /api/message/system/read — 将当前用户全部通知标为已读"""
  try:
    Message.query.filter_by(receiver_id=current_user.id).update(
      {Message.status: 'read'}, synchronize_session=False
    )
    db.session.commit()
    return jsonify('MOEMOE read all messages successfully!')
  except SQLAlchemyError as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_message_bp.route('/<int:message_id>', methods=['DELETE'])
@token_required
def delete_message(message_id, current_user=None):
  """DELETE /api/message/:id?messageId="""
  mid = request.args.get('messageId', type=int) or message_id
  row = Message.query.filter_by(id=mid, receiver_id=current_user.id).first()
  if not row:
    return error('未找到消息', code=404, http_status=404)
  try:
    db.session.delete(row)
    db.session.commit()
    return jsonify('MOEMOE delete message successfully!')
  except SQLAlchemyError as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_message_bp.route('/nav/system', methods=['GET'])
def nav_system():
  """GET /api/message/nav/system — 侧栏：通知 + 系统消息摘要"""
  uid, err = _uid_from_cookie()
  if err:
    return err

  latest = (
    Message.query.filter_by(receiver_id=uid)
    .order_by(Message.created.desc())
    .first()
  )
  message_count = Message.query.filter_by(receiver_id=uid).count()
  unread_count = Message.query.filter_by(
    receiver_id=uid, status='unread'
  ).count()

  latest_sys = SystemMessage.query.order_by(SystemMessage.created.desc()).first()
  sys_count = SystemMessage.query.count()
  sys_unread = SystemMessage.query.filter_by(status='unread').count()

  return jsonify([
    {
      'chatroomName': '',
      'content': (latest.content[:100] if latest and latest.content else ''),
      'lastMessageTime': _iso(latest.created) if latest else '',
      'count': message_count,
      'unreadCount': unread_count,
      'route': 'notice',
      'title': '消息',
      'avatar': '',
    },
    {
      'chatroomName': '',
      'content': '',
      'lastMessageTime': _iso(latest_sys.created) if latest_sys else '',
      'count': sys_count,
      'unreadCount': sys_unread,
      'route': 'system',
      'title': '系统通知',
      'avatar': '',
    },
  ])


@kun_message_bp.route('/nav/contact', methods=['GET'])
def nav_contact():
  """GET /api/message/nav/contact — 侧栏：私信会话列表"""
  uid, err = _uid_from_cookie()
  if err:
    return err

  rooms = (
    ChatRoom.query.join(
      ChatRoomParticipant,
      ChatRoomParticipant.chat_room_id == ChatRoom.id,
    )
    .filter(
      ChatRoomParticipant.user_id == uid,
      ChatRoom.last_message_sender_id.isnot(None),
      ChatRoom.last_message_sender_id != 0,
      ChatRoom.last_message_time.isnot(None),
    )
    .order_by(ChatRoom.last_message_time.desc())
    .all()
  )

  if not rooms:
    return jsonify([])

  aside = []
  for room in rooms:
    participants = ChatRoomParticipant.query.filter_by(
      chat_room_id=room.id
    ).all()
    user_ids = [p.user_id for p in participants]
    users_map = {
      u.id: u for u in User.query.filter(User.id.in_(user_ids)).all()
    }

    title = room.name
    avatar = room.avatar or ''
    route = room.name

    if room.type == 'private':
      other = next((p for p in participants if p.user_id != uid), None)
      if other and other.user_id in users_map:
        ou = users_map[other.user_id]
        title = ou.name
        avatar = ou.avatar or ''
        route = str(ou.id)

    unread = (
      ChatMessage.query.filter(
        ChatMessage.chat_room_id == room.id,
        ChatMessage.sender_id != uid,
        ~ChatMessage.id.in_(
          db.session.query(ChatMessageReadBy.chat_message_id).filter(
            ChatMessageReadBy.user_id == uid
          )
        ),
      ).count()
    )
    total_msgs = ChatMessage.query.filter_by(chat_room_id=room.id).count()

    aside.append({
      'chatroomName': room.name,
      'content': room.last_message_content or '',
      'lastMessageTime': _iso(room.last_message_time),
      'count': total_msgs,
      'unreadCount': unread,
      'route': route,
      'title': title,
      'avatar': avatar,
    })

  return jsonify(aside)


@kun_message_bp.route('/admin', methods=['GET'])
def list_system_messages():
  """GET /api/message/admin — 系统公告列表"""
  rows = SystemMessage.query.order_by(SystemMessage.created.desc()).all()
  admin_ids = {r.user_id for r in rows}
  admins = {
    u.id: u for u in User.query.filter(User.id.in_(admin_ids)).all()
  } if admin_ids else {}

  data = []
  for row in rows:
    admin = admins.get(row.user_id)
    data.append({
      'id': row.id,
      'status': row.status,
      'content': {
        'en-us': row.content_en_us or '',
        'ja-jp': row.content_ja_jp or '',
        'zh-cn': row.content_zh_cn or '',
        'zh-tw': row.content_zh_tw or '',
      },
      'admin': _user_brief(admin),
      'created': _iso(row.created),
    })
  return jsonify(data)


@kun_message_bp.route('/admin/read', methods=['PUT'])
@token_required
def read_all_system_messages(current_user=None):
  """PUT /api/message/admin/read"""
  try:
    SystemMessage.query.update(
      {SystemMessage.status: 'read'}, synchronize_session=False
    )
    db.session.commit()
    return jsonify('MOEMOE read all messages successfully!')
  except SQLAlchemyError as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


@kun_message_bp.route('/chat/history', methods=['GET'])
def chat_history():
  """GET /api/message/chat/history"""
  uid, err = _uid_from_cookie()
  if err:
    return err

  receiver_uid = request.args.get('receiverUid', type=int)
  page = request.args.get('page', 1, type=int)
  limit = min(request.args.get('limit', 30, type=int), 30)

  if not receiver_uid:
    return error('缺少 receiverUid', code=400, http_status=400)
  if receiver_uid == uid:
    return error('不能给自己发送消息', code=400, http_status=400)

  room_name = generate_room_id(receiver_uid, uid)
  room = ChatRoom.query.filter_by(name=room_name).first()

  if not room:
    room = ChatRoom(name=room_name, type='private')
    db.session.add(room)
    db.session.flush()
    db.session.add(ChatRoomParticipant(chat_room_id=room.id, user_id=uid))
    db.session.add(
      ChatRoomParticipant(chat_room_id=room.id, user_id=receiver_uid)
    )
    db.session.commit()
    return jsonify([])

  rows = (
    ChatMessage.query.filter_by(chatroom_name=room_name)
    .order_by(ChatMessage.id.desc())
    .offset((page - 1) * limit)
    .limit(limit)
    .all()
  )

  for msg in rows:
    exists = ChatMessageReadBy.query.filter_by(
      chat_message_id=msg.id, user_id=uid
    ).first()
    if not exists:
      db.session.add(
        ChatMessageReadBy(chat_message_id=msg.id, user_id=uid)
      )

  sender_ids = {m.sender_id for m in rows}
  senders = {
    u.id: u for u in User.query.filter(User.id.in_(sender_ids)).all()
  } if sender_ids else {}

  msg_ids = [m.id for m in rows]
  read_rows = (
    ChatMessageReadBy.query.filter(
      ChatMessageReadBy.chat_message_id.in_(msg_ids)
    ).all()
    if msg_ids
    else []
  )
  reader_ids = {r.user_id for r in read_rows}
  readers = {
    u.id: u for u in User.query.filter(User.id.in_(reader_ids)).all()
  } if reader_ids else {}
  read_by_map: dict[int, list] = {}
  for r in read_rows:
    read_by_map.setdefault(r.chat_message_id, []).append(
      _user_brief(readers.get(r.user_id))
    )

  messages = []
  for msg in reversed(rows):
    messages.append({
      'id': msg.id,
      'chatroomName': msg.chatroom_name,
      'sender': _user_brief(senders.get(msg.sender_id)),
      'readBy': read_by_map.get(msg.id, []),
      'receiverUid': msg.receiver_id,
      'content': msg.content,
      'isRecall': bool(msg.is_recall),
      'created': _iso(msg.created),
      'recallTime': _iso(msg.recall_time),
      'editTime': _iso(msg.edit_time),
    })

  try:
    db.session.commit()
  except SQLAlchemyError as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)

  return jsonify(messages)


@kun_message_bp.route('/chat/send', methods=['POST'])
@token_required
def chat_send(current_user=None):
  """POST /api/message/chat/send — 发送私信"""
  try:
    data = request.get_json() or {}
    receiver_uid = int(
      data.get('receiverUid') or data.get('receiverId') or 0
    )
    content = (data.get('content') or '').strip()

    if not receiver_uid:
      return error('缺少 receiverUid', code=400, http_status=400)
    if receiver_uid == current_user.id:
      return error('不能给自己发送消息', code=400, http_status=400)
    if not content:
      return error('消息内容不可为空', code=400, http_status=400)
    if len(content) > 1007:
      return error('消息最大长度不可超过 1007 个字符', code=400, http_status=400)

    receiver = User.query.get(receiver_uid)
    if not receiver:
      return error('未找到该用户', code=404, http_status=404)

    room_name = generate_room_id(receiver_uid, current_user.id)
    room = ChatRoom.query.filter_by(name=room_name).first()
    if not room:
      room = ChatRoom(name=room_name, type='private')
      db.session.add(room)
      db.session.flush()
      db.session.add(
        ChatRoomParticipant(chat_room_id=room.id, user_id=current_user.id)
      )
      db.session.add(
        ChatRoomParticipant(chat_room_id=room.id, user_id=receiver_uid)
      )

    msg = ChatMessage(
      chatroom_name=room_name,
      content=content[:1000],
      chat_room_id=room.id,
      sender_id=current_user.id,
      receiver_id=receiver_uid,
    )
    db.session.add(msg)
    db.session.flush()

    db.session.add(
      ChatMessageReadBy(chat_message_id=msg.id, user_id=current_user.id)
    )

    room.last_message_content = content[:1000]
    room.last_message_time = datetime.utcnow()
    room.last_message_sender_id = current_user.id
    room.last_message_sender_name = current_user.name or ''

    db.session.commit()

    return jsonify({
      'id': msg.id,
      'chatroomName': msg.chatroom_name,
      'sender': _user_brief(current_user),
      'readBy': [_user_brief(current_user)],
      'receiverUid': receiver_uid,
      'content': msg.content,
      'isRecall': False,
      'created': _iso(msg.created),
      'recallTime': None,
      'editTime': None,
    })
  except (TypeError, ValueError):
    return error('参数错误', code=400, http_status=400)
  except SQLAlchemyError as e:
    db.session.rollback()
    return error(str(e), code=500, http_status=500)


def user_has_new_message(uid: int) -> bool:
  """与 server/api/user/status.get.ts 一致"""
  if Message.query.filter_by(receiver_id=uid, status='unread').first():
    return True
  if SystemMessage.query.filter_by(status='unread').first():
    return True
  unread_chat = (
    db.session.query(ChatMessage.id)
    .join(ChatRoom, ChatRoom.id == ChatMessage.chat_room_id)
    .join(
      ChatRoomParticipant,
      ChatRoomParticipant.chat_room_id == ChatRoom.id,
    )
    .filter(
      ChatRoomParticipant.user_id == uid,
      ChatMessage.sender_id != uid,
      ~ChatMessage.id.in_(
        db.session.query(ChatMessageReadBy.chat_message_id).filter(
          ChatMessageReadBy.user_id == uid
        )
      ),
    )
    .first()
  )
  return unread_chat is not None
