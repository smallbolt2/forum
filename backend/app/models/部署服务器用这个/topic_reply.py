"""
KUN Visual Novel - Prisma(sqlserver) topic_reply 表映射
"""

from datetime import datetime
from app import db


class TopicReply(db.Model):
    """
    对应 prisma/schema/topic-reply.prisma 的 model topic_reply
    表名：topic_reply
    """

    __tablename__ = 'topic_reply'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, default='')
    floor = db.Column(db.Integer, default=0)
    edited = db.Column(db.DateTime, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<TopicReply {self.id}>'
