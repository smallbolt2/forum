"""
应用配置
"""
import os
from dotenv import load_dotenv

load_dotenv()


class Config:
    """基础配置"""
    # 优先使用与 Nuxt 项目一致的 JWT_SECRET，便于前后端对齐
    SECRET_KEY = os.environ.get('SECRET_KEY') or os.environ.get('JWT_SECRET') or 'dev-secret-key-change-in-production'

    # JWT 配置（与 Nuxt 端保持同名）
    JWT_ISS = os.environ.get("JWT_ISS", "KUN VISUAL NOVEL ISS")
    JWT_AUD = os.environ.get("JWT_AUD", "KUN VISUAL NOVEL KUNGALGAMER")
    JWT_SECRET = os.environ.get("JWT_SECRET", SECRET_KEY)

    # 邮件相关配置（用于验证码、通知等）
    MAIL_FROM = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_FROM")
    MAIL_HOST = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_HOST")
    MAIL_PORT = int(os.environ.get("KUN_VISUAL_NOVEL_EMAIL_PORT", "587"))
    MAIL_USERNAME = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_ACCOUNT")
    MAIL_PASSWORD = os.environ.get("KUN_VISUAL_NOVEL_EMAIL_PASSWORD")

    # 优先使用已有项目里的 SQL Server 连接串：
    # - 如果设置了 KUN_DATABASE_URL，则自动适配为 SQLAlchemy 可用的 mssql+pyodbc URL
    # - 否则退回到 DATABASE_URL，最后再使用本地默认 blog_db
    kun_db_url = os.environ.get("KUN_DATABASE_URL")
    if kun_db_url:
        # 期望格式示例：
        # sqlserver://127.0.0.1:1433;database=kungalgame;user=sa;password=xxx;trustServerCertificate=true;encrypt=false
        # 简单从中提取主机、端口、数据库名和账号密码，拼成 SQLAlchemy URL
        try:
            # 去掉前缀
            raw = kun_db_url.split("://", 1)[1]
            host_part, params_part = raw.split(";", 1)
            host, port = host_part.split(":")
            params = dict(
                kv.split("=", 1) for kv in params_part.split(";") if "=" in kv
            )
            user = params.get("user", "sa")
            password = params.get("password", "qq893779731")
            database = params.get("database", "kungalgame")
            driver = os.environ.get(
                "MSSQL_ODBC_DRIVER",
                "ODBC Driver 17 for SQL Server"
            )
            SQLALCHEMY_DATABASE_URI = (
                f"mssql+pyodbc://{user}:{password}@{host}:{port}/"
                f"{database}?driver={driver.replace(' ', '+')}"
            )
        except Exception:
            # 解析失败时退回到 DATABASE_URL
            SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
                'mssql+pyodbc://sa:893779731@localhost:1433/kungalgame?driver=ODBC+Driver+17+for+SQL+Server'
    else:
        SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
            'mssql+pyodbc://sa:893779731@localhost:1433/kungalgame?driver=ODBC+Driver+17+for+SQL+Server'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ECHO = False  # 是否打印SQL语句
    
    # 分页配置
    POSTS_PER_PAGE = 10


class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_ECHO = True


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

