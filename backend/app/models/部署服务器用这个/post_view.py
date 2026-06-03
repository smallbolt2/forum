"""
浏览记录模型
"""
from datetime import datetime
from app import db


class PostView(db.Model):
    """文章浏览记录表"""
    __tablename__ = 'post_views'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False, comment='文章ID')
    ip_address = db.Column(db.String(45), nullable=False, comment='IP地址')
    user_agent = db.Column(db.String(255), comment='用户代理')
    viewed_at = db.Column(db.DateTime, default=datetime.utcnow, comment='浏览时间')

    # 关系
    post = db.relationship('Post', backref='views_records', lazy=True)

    def __repr__(self):
        return f'<PostView {self.post_id}:{self.ip_address}>'