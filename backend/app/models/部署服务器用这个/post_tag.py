"""
文章-标签关联表
"""
from app import db

post_tags = db.Table('post_tags',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True, comment='文章ID'),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'), primary_key=True, comment='标签ID')
)

