from datetime import datetime
from app import db


class GalgameToolset(db.Model):
  __tablename__ = 'galgame_toolset'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.String(500), default='')
  description = db.Column(db.String(2000), default='')
  status = db.Column(db.Integer, default=0)
  view = db.Column(db.Integer, default=0)
  type = db.Column(db.Text, default='')
  language = db.Column(db.Text, default='')
  platform = db.Column(db.Text, default='')
  homepage = db.Column(db.Text, default='[]')
  resource_update_time = db.Column(db.DateTime, default=datetime.utcnow)
  edited = db.Column(db.DateTime, nullable=True)
  version = db.Column(db.String(233), default='')
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameToolsetAlias(db.Model):
  __tablename__ = 'galgame_toolset_alias'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.Text, default='')
  toolset_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameToolsetResource(db.Model):
  __tablename__ = 'galgame_toolset_resource'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  download = db.Column(db.Integer, default=0)
  toolset_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameToolsetComment(db.Model):
  __tablename__ = 'galgame_toolset_comment'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  toolset_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  content = db.Column(db.Text, default='')
  parent_id = db.Column(db.Integer, nullable=True)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class GalgameToolsetPracticality(db.Model):
  __tablename__ = 'galgame_toolset_practicality'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  rate = db.Column(db.Integer, default=1)
  user_id = db.Column(db.Integer, nullable=False)
  toolset_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

