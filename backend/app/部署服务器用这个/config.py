"""
应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv()

# 获取项目根目录（backend 的上级目录）
basedir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))


class Config:
    """基础配置"""
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET') or 'dev-secret-key-change-in-production'

    # JWT 配置
    JWT_ISS = os.environ.get("JWT_ISS", "KUN VISUAL NOVEL ISS")
    JWT_AUD = os.environ.get("JWT_AUD", "KUN VISUAL NOVEL KUNGALGAMER")
    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)

    # 邮件相关配置
    MAIL_FROM = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_FROM")
    MAIL_HOST = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_HOST")
    MAIL_PORT = int(os.environ.get("KUN_VISUAL_NOVEL_EMAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_ACCOUNT")
    MAIL_PASSWORD = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_PASSWORD")

    # ============ 数据库配置（SQLite）============
    # 数据库文件放在 backend 同级目录下，方便备份
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///' + os.path.join(basedir, 'forum.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False
    
    # 分页配置
    POSTS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True
    LOG_VERIFICATION_CODE = True


class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False
    SQLALCHEMY_ECHO = False


# 配置字典
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}