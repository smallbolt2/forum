"""
分类模型
"""
from datetime import datetime
from app import db


class Category(db.Model):
    """分类表"""
    __tablename__ = 'categories'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(50), unique=True, nullable=False, comment='分类名称')
    slug = db.Column(db.String(50), unique=True, nullable=False, comment='分类别名（URL友好）')
    description = db.Column(db.Text, comment='分类描述')
    order = db.Column(db.Integer, default=0, comment='排序')
    created_at = db.Column(db.DateTime, default=datetime.utcnow, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, comment='更新时间')
    
    def to_dict(self):
        """转换为字典"""
        # 使用查询计算已发布的文章数量（更高效）
        # 延迟导入避免循环导入
        try:
            from app.models.post import Post
            post_count = Post.query.filter_by(category_id=self.id, status=1).count()
        except Exception as e:
            print(f"Error counting posts in category {self.id}: {e}")
            import traceback
            traceback.print_exc()
            post_count = 0
        return {
            'id': self.id,
            'name': self.name,
            'slug': self.slug,
            'description': self.description,
            'order': self.order,
            'post_count': post_count,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None
        }
    
    def __repr__(self):
        return f'<Category {self.name}>'

