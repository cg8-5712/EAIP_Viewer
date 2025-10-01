"""
用户模型
"""

from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text
from src.models.base import Base, TimestampMixin
from datetime import datetime
import uuid


class User(Base, TimestampMixin):
    """用户模型"""

    __tablename__ = 'users'

    # 主键
    id = Column(Integer, primary_key=True, autoincrement=True)

    # 基本信息
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)

    # 安全字段
    password_hash = Column(String(255), nullable=False)
    password_salt = Column(String(32), nullable=False)

    # 会话管理
    session_token = Column(String(36), nullable=True, unique=True)
    session_expires_at = Column(DateTime, nullable=True)

    # 时间戳（继承自 TimestampMixin）
    last_login_at = Column(DateTime, nullable=True)

    # 状态
    is_active = Column(Boolean, default=True, nullable=False)
    is_guest = Column(Boolean, default=False, nullable=False)

    # 登录失败计数
    login_attempts = Column(Integer, default=0)
    locked_until = Column(DateTime, nullable=True)

    # 用户偏好设置
    preferences = Column(Text, nullable=True)

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}')>"

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.utcnow()
        self.login_attempts = 0

    def increment_login_attempts(self):
        """增加登录失败次数"""
        self.login_attempts += 1
        if self.login_attempts >= 5:
            from datetime import timedelta
            self.locked_until = datetime.utcnow() + timedelta(minutes=15)

    def is_locked(self) -> bool:
        """检查账户是否被锁定"""
        if self.locked_until:
            if datetime.utcnow() < self.locked_until:
                return True
            else:
                self.locked_until = None
                self.login_attempts = 0
        return False

    def generate_session_token(self, remember_me: bool = False):
        """生成会话 Token"""
        self.session_token = str(uuid.uuid4())

        from datetime import timedelta
        if remember_me:
            self.session_expires_at = datetime.utcnow() + timedelta(days=30)
        else:
            self.session_expires_at = datetime.utcnow() + timedelta(hours=24)

        return self.session_token

    def is_session_valid(self) -> bool:
        """检查会话是否有效"""
        if not self.session_token or not self.session_expires_at:
            return False
        return datetime.utcnow() < self.session_expires_at

    def clear_session(self):
        """清除会话"""
        self.session_token = None
        self.session_expires_at = None
