"""
数据库连接测试脚本
用于测试SQL Server数据库连接是否成功
"""
import sys
from app import create_app, db
from app.config import config

def test_database_connection():
    """测试数据库连接"""
    print("=" * 50)
    print("开始测试SQL Server数据库连接...")
    print("=" * 50)
    print("注意：请确保已安装ODBC Driver for SQL Server")
    print("下载地址：https://docs.microsoft.com/en-us/sql/connect/odbc/download-odbc-driver-for-sql-server")
    print("=" * 50)

    try:
        # 创建Flask应用
        app = create_app(config['development'])

        with app.app_context():
            # 尝试连接数据库
            print("\n1. 正在连接数据库...")
            try:
                # 使用session测试连接
                db.session.execute(db.text("SELECT 1"))
                db.session.commit()
                print("   ✓ 数据库连接成功！")
            except Exception as e:
                print(f"   ❌ 连接失败: {str(e)}")
                raise

            # 检查当前数据库
            print("\n2. 检查当前数据库...")
            try:
                result = db.session.execute(db.text("SELECT DB_NAME()"))
                current_db = result.fetchone()[0]
                print(f"   ✓ 当前数据库: {current_db}")
            except Exception as e:
                print(f"   ⚠ 无法获取数据库名: {str(e)}")

            # 检查表是否存在
            print("\n3. 检查数据表...")
            try:
                result = db.session.execute(db.text("""
                    SELECT TABLE_NAME
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_TYPE = 'BASE TABLE'
                """))
                tables = [row[0] for row in result]

                if tables:
                    print(f"   ✓ 找到 {len(tables)} 个数据表:")
                    for table in tables:
                        print(f"      - {table}")
                else:
                    print("   ⚠ 未找到数据表")
                    print("   提示：请执行 database/init.sql 初始化数据库（需要适配SQL Server）")
            except Exception as e:
                print(f"   ⚠ 无法查询表: {str(e)}")

            # 测试查询（尝试查询categories表，如果存在）
            print("\n4. 测试查询操作...")
            try:
                result = db.session.execute(db.text("""
                    SELECT COUNT(*) as count
                    FROM INFORMATION_SCHEMA.TABLES
                    WHERE TABLE_NAME = 'categories'
                """))
                if result.fetchone()[0] > 0:
                    result = db.session.execute(db.text("SELECT COUNT(*) as count FROM categories"))
                    count = result.fetchone()[0]
                    print(f"   ✓ 分类表查询成功，当前有 {count} 条记录")
                else:
                    print("   ⚠ categories表不存在，跳过查询测试")
            except Exception as e:
                print(f"   ⚠ 查询失败: {str(e)}")
                print("   提示：如果表不存在，请执行 database/init.sql 初始化数据库（需要适配SQL Server）")

            print("\n" + "=" * 50)
            print("✓ 数据库连接测试完成！")
            print("=" * 50)
            return True

    except Exception as e:
        print("\n" + "=" * 50)
        print("❌ 数据库连接失败！")
        print("=" * 50)
        print(f"\n错误信息: {str(e)}")
        print("\n可能的原因:")
        print("1. SQL Server服务未启动")
        print("2. 数据库连接信息错误（用户名、密码、数据库名、主机、端口）")
        print("3. 数据库 'blog_db' 不存在，请先在SQL Server中创建")
        print("4. ODBC Driver for SQL Server未安装")
        print("5. pyodbc未安装，请运行: pip install pyodbc")
        print("\n请检查:")
        print("- backend/app/config.py 中的数据库连接配置")
        print("  当前配置: " + app.config['SQLALCHEMY_DATABASE_URI'])
        print("- SQL Server服务是否运行")
        print("- 数据库是否已创建")
        print("\n解决步骤:")
        print("1. 确保SQL Server服务已启动")
        print("2. 在SQL Server中创建blog_db数据库")
        print("3. 检查连接字符串中的用户名、密码、主机、端口是否正确")
        print("4. 安装ODBC Driver for SQL Server（如果尚未安装）")
        print("5. 运行: pip install -r requirements.txt 安装pyodbc")
        print("=" * 50)
        return False

if __name__ == '__main__':
    success = test_database_connection()
    sys.exit(0 if success else 1)