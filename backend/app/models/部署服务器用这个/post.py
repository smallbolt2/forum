"""
文章模型
"""
from datetime import datetime
from app import db


class Post(db.Model):
    """文章表"""
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(200), nullable=False, comment='标题')
    content = db.Column(db.Text, nullable=False, comment='内容')
    summary = db.Column(db.Text, comment='摘要')
    cover_image = db.Column(db.String(255), comment='封面图片URL')
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='作者ID')
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), comment='分类ID')
    status = db.Column(db.Integer, default=1, comment='状态：0-草稿，1-已发布，2-已删除')
    views = db.Column(db.Integer, default=0, comment='浏览量')
    likes = db.Column(db.Integer, default=0, comment='点赞数')
    is_top = db.Column(db.Boolean, default=False, comment='是否置顶')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    published_at = db.Column(db.DateTime, default=datetime.utcnow, comment='发布时间')
    
    # 关系
    category = db.relationship('Category', backref='posts', lazy=True)
    tags = db.relationship('Tag', secondary='post_tags', backref='posts', lazy='dynamic')
    comments = db.relationship('Comment', backref='post', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典（简化版）"""
        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'author_id': self.author_id,
            'category_id': self.category_id,
            'status': self.status,
            'views': self.views,
            'likes': self.likes,
            'is_top': self.is_top,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
        }
    
    def to_full_dict(self):
        """转换为字典（完整版，包含所有关系数据）"""
        # 获取作者信息
        author_dict = None
        if self.author:
            try:
                author_dict = self.author.to_dict()
            except Exception as e:
                print(f"Error getting author dict: {e}")
                author_dict = None

        # 获取分类信息
        category_dict = None
        if self.category:
            try:
                category_dict = self.category.to_dict()
            except Exception as e:
                print(f"Error getting category dict: {e}")
                category_dict = None

        # 获取标签信息
        tags_list = []
        if self.tags:
            try:
                tags_list = [tag.to_dict() for tag in self.tags.all()]
            except Exception as e:
                print(f"Error getting tags dict: {e}")
                tags_list = []

        # 获取评论信息（只获取已发布的顶级评论）
        comments_list = []
        if self.comments:
            try:
                comments_list = [comment.to_dict() for comment in self.comments.filter_by(status=1, parent_id=None).all()]
            except Exception as e:
                print(f"Error getting comments dict: {e}")
                comments_list = []

        # 计算评论总数
        comment_count = 0
        try:
            comment_count = self.comments.filter_by(status=1).count()
        except Exception as e:
            print(f"Error counting comments: {e}")
            comment_count = 0

        return {
            'id': self.id,
            'title': self.title,
            'content': self.content,
            'summary': self.summary,
            'cover_image': self.cover_image,
            'author_id': self.author_id,
            'author': author_dict,
            'category_id': self.category_id,
            'category': category_dict,
            'tags': tags_list,
            'comments': comments_list,
            'status': self.status,
            'views': self.views,
            'likes': self.likes,
            'is_top': self.is_top,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'published_at': self.published_at.strftime('%Y-%m-%d %H:%M:%S') if self.published_at else None,
            'comment_count': comment_count
        }
    
    def __repr__(self):
        return f'<Post {self.title}>'
