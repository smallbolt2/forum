"""
KUN Visual Novel - Prisma(sqlserver) topic 表映射
"""

from datetime import datetime
from app import db


class Topic(db.Model):
    """
    对应 prisma/schema/topic.prisma 的 model topic
    表名：topic
    """

    __tablename__ = 'topic'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(233), nullable=False)
    content = db.Column(db.Text, nullable=False)
    view = db.Column(db.Integer, default=0)
    is_nsfw = db.Column(db.Boolean, default=False)
    status = db.Column(db.Integer, default=0)
    category = db.Column(db.Text, nullable=False)
    status_update_time = db.Column(db.DateTime, default=datetime.utcnow)
    edited = db.Column(db.DateTime, nullable=True)
    upvote_time = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    best_answer_id = db.Column(db.Integer, nullable=True)
    pinned_reply_id = db.Column(db.Integer, nullable=True)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<Topic {self.title}>'
