#!/usr/bin/env python3
"""
Flask-Migrate 初始化脚本（跨平台版本）
用于初始化数据库迁移环境并创建初始迁移。
"""

import os
import sys
import subprocess
import shutil

def run_command(cmd, description):
    """运行命令并检查结果"""
    print(f"→ {description}...")
    print(f"  执行: {cmd}")

    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        if result.stdout:
            print(f"  输出: {result.stdout.strip()}")
        print(f"  ✓ 成功")
        return True
    except subprocess.CalledProcessError as e:
        print(f"  ❌ 失败: {e.stderr.strip() if e.stderr else str(e)}")
        return False

def check_virtualenv():
    """检查是否在虚拟环境中"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    if not in_venv:
        print("⚠ 警告：未检测到虚拟环境")
        print("建议先激活虚拟环境：")
        print("  Windows: venv\\Scripts\\activate")
        print("  Linux/Mac: source venv/bin/activate")
        response = input("是否继续？(y/N): ").strip().lower()
        if response != 'y':
            print("操作已取消。")
            return False
    return True

def main():
    print("=" * 50)
    print("Flask-Migrate 初始化脚本")
    print("=" * 50)

    # 检查虚拟环境
    if not check_virtualenv():
        return 1

    # 设置环境变量
    os.environ['FLASK_APP'] = 'run.py'
    print(f"✓ 设置 FLASK_APP={os.environ['FLASK_APP']}")

    # 检查 migrations 目录
    migrations_dir = "migrations"
    if os.path.exists(migrations_dir):
        print(f"⚠ migrations 目录已存在")
        print("\n选项：")
        print("  1. 删除现有 migrations 目录并重新初始化")
        print("  2. 跳过初始化，直接生成迁移脚本")
        print("  3. 退出")

        choice = input("\n请选择 (1/2/3): ").strip()

        if choice == '1':
            print("删除现有 migrations 目录...")
            try:
                shutil.rmtree(migrations_dir)
                print("  ✓ 目录已删除")
            except Exception as e:
                print(f"  ❌ 删除失败: {e}")
                return 1

            # 初始化迁移仓库
            if not run_command("flask db init", "初始化迁移仓库"):
                return 1

        elif choice == '2':
            print("跳过初始化...")
        else:
            print("操作已取消。")
            return 1
    else:
        # 初始化迁移仓库
        if not run_command("flask db init", "初始化迁移仓库"):
            return 1

    # 生成迁移脚本
    print("\n生成初始迁移脚本...")
    migrate_cmd = 'flask db migrate -m "Initial migration for SQL Server"'

    # 尝试生成迁移
    success = run_command(migrate_cmd, "生成迁移脚本")

    if not success:
        print("\n⚠ 迁移脚本生成失败，可能的原因：")
        print("  1. 数据库连接失败")
        print("  2. 数据库已存在表结构")
        print("  3. 模型定义有问题")
        print("\n如果数据库已存在表结构，可以尝试标记当前状态：")
        print("  flask db stamp head")

        response = input("\n是否尝试标记当前数据库状态？(y/N): ").strip().lower()
        if response == 'y':
            if not run_command("flask db stamp head", "标记数据库当前状态"):
                return 1
        else:
            return 1

    # 应用迁移
    print("\n应用迁移到数据库...")
    if not run_command("flask db upgrade", "应用迁移"):
        print("\n⚠ 迁移应用失败，请检查：")
        print("  1. 数据库连接配置")
        print("  2. 数据库用户权限")
        print("  3. 迁移脚本中的语法错误")
        return 1

    print("\n" + "=" * 50)
    print("✓ 迁移初始化完成！")
    print("=" * 50)
    print("\n后续操作：")
    print("  1. 修改模型后，运行: flask db migrate -m '描述变更'")
    print("  2. 应用迁移: flask db upgrade")
    print("  3. 回滚迁移: flask db downgrade")
    print("  4. 查看迁移历史: flask db history")
    print("  5. 查看当前版本: flask db current")
    print("\n提示：确保数据库连接配置正确，可在 app/config.py 中修改。")

    return 0

if __name__ == "__main__":
    sys.exit(main())