"""
数据库基础模型定义
所有模型的基类
"""

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime
from datetime import datetime

# 创建声明式基类
Base = declarative_base()


class TimestampMixin:
    """时间戳混合类"""

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
