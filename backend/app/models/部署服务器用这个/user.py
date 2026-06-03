"""
KUN Visual Novel - Prisma(sqlserver) user 表映射
"""

from datetime import datetime
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
import bcrypt


class User(db.Model):
    """
    对应 prisma/schema/user.prisma 的 model user
    表名：user
    """

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(255), unique=True, nullable=False)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.Text, nullable=False)
    ip = db.Column(db.Text, default='')
    avatar = db.Column(db.Text, default='')
    role = db.Column(db.Integer, default=1)
    status = db.Column(db.Integer, default=0)
    moemoepoint = db.Column(db.Integer, default=7)
    bio = db.Column(db.String(107), default='')
    daily_check_in = db.Column(db.Integer, default=0)
    daily_image_count = db.Column(db.Integer, default=0)
    daily_toolset_upload_count = db.Column(db.Integer, default=0)

    created = db.Column(db.DateTime, default=datetime.utcnow)
    updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, raw_password: str):
        # Prisma 侧存的是 bcrypt hash；这里保留兼容：如果你传入明文则 hash，传入已 hash 则直接存
        if raw_password.startswith('$2a$') or raw_password.startswith('$2b$') or raw_password.startswith('$2y$'):
            self.password = raw_password
        else:
            self.password = generate_password_hash(raw_password)

    def check_password(self, raw_password: str) -> bool:
        if raw_password is None:
            return False
        if isinstance(raw_password, bytes):
            raw_password = raw_password.decode('utf-8', errors='strict')

        stored = self.password
        if stored is None:
            return False
        if isinstance(stored, (bytes, bytearray, memoryview)):
            stored = bytes(stored).decode('utf-8', errors='ignore')
        else:
            stored = str(stored)
        # MSSQL nvarchar/text 偶发首尾空白会破坏 bcrypt 校验
        stored = stored.strip()
        if not stored:
            return False

        # Prisma/Node bcrypt 常见前缀（含 $2y$ PHP 系）
        if stored.startswith(('$2a$', '$2b$', '$2y$')):
            try:
                pw = raw_password.encode('utf-8')
                # 哈希为纯 ASCII，用 ascii 编码更贴近 Node 侧字节序列
                return bcrypt.checkpw(pw, stored.encode('ascii'))
            except Exception:
                try:
                    return bcrypt.checkpw(raw_password.encode('utf-8'), stored.encode('utf-8'))
                except Exception:
                    return False

        # fallback: werkzeug pbkdf2/scrypt 等
        try:
            return check_password_hash(stored, raw_password)
        except Exception:
            return False

    def to_dict(self):
        # 对齐 Nuxt 常用的 KunUser 结构
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'avatar': self.avatar,
            'role': self.role,
            'status': self.status,
            'moemoepoint': self.moemoepoint,
            'bio': self.bio,
            'daily_check_in': self.daily_check_in,
            'daily_toolset_upload_count': self.daily_toolset_upload_count,
            'created': self.created.isoformat() if self.created else None,
            'updated': self.updated.isoformat() if self.updated else None
        }

    def __repr__(self):
        return f'<User {self.name}>'

