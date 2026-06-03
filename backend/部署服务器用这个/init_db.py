"""
数据库初始化脚本
"""
from app import create_app
from app.config import config
from app import db  # db 在这里

app = create_app(config['development'])

with app.app_context():
    db.create_all()
    print("[OK] 数据库表创建成功")
    print("[OK] SQLite 数据库文件: ../forum.db (backend 同级目录)")
