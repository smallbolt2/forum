"""
评论模型
"""
from datetime import datetime
from app import db


class Comment(db.Model):
    """评论表"""
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    content = db.Column(db.Text, nullable=False, comment='评论内容')
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, comment='文章ID')
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='用户ID')
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'), comment='父评论ID（用于回复）')
    status = db.Column(db.Integer, default=1, comment='状态：0-待审核，1-已通过，2-已删除')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    # 关系
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy='dynamic')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'content': self.content,
            'post_id': self.post_id,
            'user_id': self.user_id,
            'user': self.user.to_dict() if self.user else None,
            'parent_id': self.parent_id,
            'status': self.status,
            'replies': [reply.to_dict() for reply in self.replies.filter_by(status=1).all()] if self.replies else [],
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Comment {self.id}>'

