#!/usr/bin/env python3
"""
插入示例数据脚本
用于向SQL Server数据库插入示例分类和标签数据
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app, db
from app.config import config
from app.models.category import Category
from app.models.tag import Tag

def insert_sample_data():
    """插入示例数据"""
    print("=" * 50)
    print("开始插入示例数据...")
    print("=" * 50)

    try:
        # 创建Flask应用
        app = create_app(config['development'])

        with app.app_context():
            # 检查表是否存在
            print("\n1. 检查数据库表...")
            try:
                # 尝试查询表是否存在
                db.session.execute(db.text("SELECT 1 FROM categories WHERE 1=0"))
                db.session.execute(db.text("SELECT 1 FROM tags WHERE 1=0"))
                print("   ✓ 数据库表检查通过")
            except Exception as e:
                print(f"   ❌ 表检查失败: {str(e)}")
                print("   请确保数据库表已创建，可以运行:")
                print("   - database\\init_sqlserver.sql (SQL脚本)")
                print("   - flask db upgrade (Flask-Migrate)")
                return False

            # 检查并插入分类数据
            print("\n2. 插入示例分类...")
            categories_data = [
                {'name': '技术分享', 'slug': 'tech', 'description': '技术相关的文章', 'order': 1},
                {'name': '生活随笔', 'slug': 'life', 'description': '生活感悟和随笔', 'order': 2},
                {'name': '学习笔记', 'slug': 'study', 'description': '学习过程中的笔记', 'order': 3},
                {'name': '项目经验', 'slug': 'project', 'description': '项目开发经验分享', 'order': 4}
            ]

            category_count = 0
            for cat_data in categories_data:
                # 检查是否已存在
                existing = Category.query.filter_by(slug=cat_data['slug']).first()
                if not existing:
                    category = Category(
                        name=cat_data['name'],
                        slug=cat_data['slug'],
                        description=cat_data['description'],
                        order=cat_data['order']
                    )
                    db.session.add(category)
                    category_count += 1
                    print(f"   + 添加分类: {cat_data['name']} ({cat_data['slug']})")

            # 检查并插入标签数据
            print("\n3. 插入示例标签...")
            tags_data = [
                {'name': 'Python', 'slug': 'python', 'color': '#3776ab'},
                {'name': 'Vue.js', 'slug': 'vuejs', 'color': '#4fc08d'},
                {'name': 'Flask', 'slug': 'flask', 'color': '#000000'},
                {'name': 'MySQL', 'slug': 'mysql', 'color': '#00758f'},
                {'name': '前端开发', 'slug': 'frontend', 'color': '#61dafb'},
                {'name': '后端开发', 'slug': 'backend', 'color': '#f7df1e'}
            ]

            tag_count = 0
            for tag_data in tags_data:
                # 检查是否已存在
                existing = Tag.query.filter_by(slug=tag_data['slug']).first()
                if not existing:
                    tag = Tag(
                        name=tag_data['name'],
                        slug=tag_data['slug'],
                        color=tag_data['color']
                    )
                    db.session.add(tag)
                    tag_count += 1
                    print(f"   + 添加标签: {tag_data['name']} ({tag_data['slug']})")

            # 提交事务
            if category_count > 0 or tag_count > 0:
                db.session.commit()
                print(f"\n   ✓ 成功插入 {category_count} 个分类和 {tag_count} 个标签")
            else:
                print("\n   ⚠ 所有示例数据已存在，无需插入")

            # 显示当前数据统计
            print("\n4. 当前数据统计:")
            total_categories = Category.query.count()
            total_tags = Tag.query.count()
            print(f"   分类总数: {total_categories}")
            print(f"   标签总数: {total_tags}")

            # 显示分类列表
            print("\n   分类列表:")
            categories = Category.query.order_by(Category.order).all()
            for cat in categories:
                print(f"     - {cat.name} ({cat.slug}): {cat.description}")

            # 显示标签列表
            print("\n   标签列表:")
            tags = Tag.query.order_by(Tag.name).all()
            for tag in tags:
                print(f"     - {tag.name} ({tag.slug}): {tag.color or '无颜色'}")

            print("\n" + "=" * 50)
            print("✓ 示例数据插入完成！")
            print("=" * 50)
            return True

    except Exception as e:
        print(f"\n❌ 插入数据时发生错误: {str(e)}")
        print("\n可能的原因:")
        print("1. 数据库连接失败")
        print("2. 数据库表不存在")
        print("3. 数据格式错误")
        print("\n建议:")
        print("1. 运行 python test_db_connection.py 测试数据库连接")
        print("2. 检查数据库表是否已创建")
        print("3. 查看数据库日志获取详细错误信息")
        return False

def main():
    """主函数"""
    print("个人博客系统 - 示例数据插入工具")
    print("=" * 50)
    print("此工具将向数据库插入示例分类和标签数据。")
    print("=" * 50)

    response = input("\n是否继续？(y/N): ").strip().lower()
    if response != 'y' and response != 'yes':
        print("操作已取消。")
        return 1

    if insert_sample_data():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())