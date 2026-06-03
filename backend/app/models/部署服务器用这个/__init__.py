"""
数据模型
"""
from app.models.user import User
from app.models.post import Post
from app.models.topic import Topic
from app.models.category import Category
from app.models.tag import Tag
from app.models.post_tag import post_tags
from app.models.comment import Comment
from app.models.post_like import PostLike
from app.models.post_view import PostView

__all__ = ['User', 'Post', 'Topic', 'Category', 'Tag', 'post_tags', 'Comment', 'PostLike', 'PostView']

