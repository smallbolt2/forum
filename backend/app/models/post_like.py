"""
文章点赞记录模型
"""
from datetime import datetime
from app import db


class PostLike(db.Model):
    """文章点赞记录表"""
    __tablename__ = 'post_likes'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, comment='文章ID')
    ip_address = db.Column(db.String(45), nullable=False, comment='IP地址')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='点赞时间')
    
    # 关系
    post = db.relationship('Post', backref='likes_records', lazy=True)
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'post_id': self.post_id,
            'ip_address': self.ip_address,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }