#!/usr/bin/env python3
"""
测试浏览量IP去重功能
"""

from app import create_app
from app.models.post import Post
from app.models.post_view import PostView
from datetime import datetime, timedelta

def test_view_counting():
    """测试浏览量统计"""
    app = create_app()
    with app.app_context():
        try:
            # 获取第一篇文章
            post = Post.query.filter_by(status=1).first()
            if not post:
                print("没有找到已发布的文章")
                return

            print(f"测试文章: {post.title} (ID: {post.id})")
            print(f"初始浏览量: {post.views}")

            # 模拟同一个IP多次访问
            test_ip = "192.168.1.100"

            # 第一次访问
            from app import db
            view_record = PostView(
                post_id=post.id,
                ip_address=test_ip,
                user_agent="Test Browser"
            )
            db.session.add(view_record)
            post.views += 1
            db.session.commit()

            print(f"第一次访问后浏览量: {post.views}")

            # 第二次访问（应该不增加浏览量）
            # 检查是否在24小时内已经访问过
            twenty_four_hours_ago = datetime.utcnow() - timedelta(hours=24)
            existing_view = PostView.query.filter_by(
                post_id=post.id,
                ip_address=test_ip
            ).filter(PostView.viewed_at >= twenty_four_hours_ago).first()

            if not existing_view:
                post.views += 1
                view_record = PostView(
                    post_id=post.id,
                    ip_address=test_ip,
                    user_agent="Test Browser 2"
                )
                db.session.add(view_record)

            db.session.commit()
            print(f"第二次访问后浏览量: {post.views}")

            # 显示该IP的浏览记录
            views = PostView.query.filter_by(post_id=post.id, ip_address=test_ip).all()
            print(f"IP {test_ip} 的浏览记录数量: {len(views)}")

        except Exception as e:
            print(f"测试出错: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    test_view_counting()