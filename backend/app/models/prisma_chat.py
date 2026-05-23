from datetime import datetime

from app import db


class ChatRoom(db.Model):
  __tablename__ = 'chat_room'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(255), unique=True, default='')
  avatar = db.Column(db.String(500), default='')
  type = db.Column(db.String(50), nullable=False)
  last_message_content = db.Column(db.String(1000), default='')
  last_message_time = db.Column(db.DateTime, nullable=True)
  last_message_sender_id = db.Column(db.Integer, nullable=True)
  last_message_sender_name = db.Column(db.String(255), default='')
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatRoomParticipant(db.Model):
  __tablename__ = 'chat_room_participant'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  chat_room_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessage(db.Model):
  __tablename__ = 'chat_message'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  chatroom_name = db.Column(db.String(255), nullable=False)
  content = db.Column(db.String(1000), nullable=False)
  is_recall = db.Column(db.Boolean, default=False)
  recall_time = db.Column(db.DateTime, nullable=True)
  edit_time = db.Column(db.DateTime, nullable=True)
  chat_room_id = db.Column(db.Integer, nullable=False)
  sender_id = db.Column(db.Integer, nullable=False)
  receiver_id = db.Column(db.Integer, nullable=True)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ChatMessageReadBy(db.Model):
  __tablename__ = 'chat_message_read_by'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  read_time = db.Column(db.DateTime, default=datetime.utcnow)
  chat_message_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
