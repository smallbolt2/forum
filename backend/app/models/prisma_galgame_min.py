from datetime import datetime
from app import db


class Galgame(db.Model):
  __tablename__ = 'galgame'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  vndb_id = db.Column(db.String(10), unique=True)
  name_en_us = db.Column(db.String(1000), default='')
  name_ja_jp = db.Column(db.String(1000), default='')
  name_zh_cn = db.Column(db.String(1000), default='')
  name_zh_tw = db.Column(db.String(1000), default='')
  banner = db.Column(db.String(233), default='')
  intro_en_us = db.Column(db.Text, default='')
  intro_ja_jp = db.Column(db.Text, default='')
  intro_zh_cn = db.Column(db.Text, default='')
  intro_zh_tw = db.Column(db.Text, default='')
  content_limit = db.Column(db.String(10), default='sfw')
  status = db.Column(db.Integer, default=0)
  view = db.Column(db.Integer, default=0)
  resource_update_time = db.Column(db.DateTime, default=datetime.utcnow)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameLike(db.Model):
  __tablename__ = 'galgame_like'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  galgame_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameFavorite(db.Model):
  __tablename__ = 'galgame_favorite'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  galgame_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameResource(db.Model):
  __tablename__ = 'galgame_resource'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  platform = db.Column(db.Text, default='')
  language = db.Column(db.Text, default='')
  galgame_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

