from datetime import datetime

from app import db


class Message(db.Model):
  __tablename__ = 'message'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  content = db.Column(db.String(233), default='')
  link = db.Column(db.String(100), default='')
  status = db.Column(db.String(20), default='unread')
  type = db.Column(db.String(50), nullable=False)
  sender_id = db.Column(db.Integer, nullable=False)
  receiver_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class SystemMessage(db.Model):
  __tablename__ = 'system_message'

  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  content_en_us = db.Column(db.Text, default='')
  content_ja_jp = db.Column(db.Text, default='')
  content_zh_cn = db.Column(db.Text, default='')
  content_zh_tw = db.Column(db.Text, default='')
  status = db.Column(db.String(20), default='unread')
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
