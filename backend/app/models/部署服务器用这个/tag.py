"""
标签模型
"""
from datetime import datetime
from app import db
from app.models.post_tag import post_tags


class Tag(db.Model):
    """标签表"""
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='标签名称')
    slug = db.Column(db.String(50), unique=True, nullable=False, comment='标签别名（URL友好）')
    color = db.Column(db.String(20), comment='标签颜色')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        # 使用查询计算已发布的文章数量
        try:
            # 总是使用直接查询来计算文章数量，避免关系加载问题
            from app.models.post import Post
            post_count = db.session.query(Post).join(post_tags).filter(
                post_tags.c.tag_id == self.id,
                Post.status == 1
            ).count()
        except Exception as e:
            print(f"Error counting posts for tag {self.id} ({self.name}): {e}")
            import traceback
            traceback.print_exc()
            post_count = 0
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'color': self.color,
            'post_count': post_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Tag {self.name}>'

