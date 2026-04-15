#!/usr/bin/env python3
"""
清理过期浏览记录脚本
定期清理超过30天的浏览记录
"""

from datetime import datetime, timedelta
from app import create_app
from app.models.post_view import PostView

def cleanup_expired_views():
    """清理30天前的浏览记录"""
    app = create_app()
    with app.app_context():
        try:
            # 计算30天前的时间
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)

            # 删除过期记录
            deleted_count = PostView.query.filter(PostView.viewed_at < thirty_days_ago).delete()

            # 提交更改
            from app import db
            db.session.commit()

            print(f"成功清理 {deleted_count} 条过期浏览记录")
            return deleted_count

        except Exception as e:
            print(f"清理浏览记录时出错: {e}")
            from app import db
            db.session.rollback()
            return 0

if __name__ == "__main__":
    cleanup_expired_views()