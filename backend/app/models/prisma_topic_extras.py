from datetime import datetime
from app import db


class TopicTag(db.Model):
  __tablename__ = 'topic_tag'
  topic_id = db.Column(db.Integer, primary_key=True)
  tag = db.Column(db.String(128), primary_key=True)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicSection(db.Model):
  __tablename__ = 'topic_section'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  name = db.Column(db.Text)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
  #测试学习
  cheshi=db


class TopicSectionRelation(db.Model):
  __tablename__ = 'topic_section_relation'
  topic_id = db.Column(db.Integer, primary_key=True)
  topic_section_id = db.Column(db.Integer, primary_key=True)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicLike(db.Model):
  __tablename__ = 'topic_like'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  topic_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicDislike(db.Model):
  __tablename__ = 'topic_dislike'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  topic_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicFavorite(db.Model):
  __tablename__ = 'topic_favorite'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  topic_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicUpvote(db.Model):
  __tablename__ = 'topic_upvote'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  topic_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicReplyLike(db.Model):
  __tablename__ = 'topic_reply_like'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, nullable=False)
  topic_reply_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicReplyDislike(db.Model):
  __tablename__ = 'topic_reply_dislike'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  user_id = db.Column(db.Integer, nullable=False)
  topic_reply_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicReplyTarget(db.Model):
  __tablename__ = 'topic_reply_target'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  content = db.Column(db.Text, default='')
  reply_id = db.Column(db.Integer, nullable=False)
  target_reply_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicComment(db.Model):
  __tablename__ = 'topic_comment'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  content = db.Column(db.String(1007), default='')
  topic_id = db.Column(db.Integer, nullable=False)
  topic_reply_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  target_user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class TopicCommentLike(db.Model):
  __tablename__ = 'topic_comment_like'
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  topic_comment_id = db.Column(db.Integer, nullable=False)
  user_id = db.Column(db.Integer, nullable=False)
  created = db.Column(db.DateTime, default=datetime.utcnow)
  updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

