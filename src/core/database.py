"""
数据库管理模块
提供数据库连接和会话管理
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from contextlib import contextmanager
from src.config import config
from src.utils.logger import logger


class DatabaseManager:
    """数据库管理器（单例模式）"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True

        # 创建数据库引擎
        self.engine = create_engine(
            config.DATABASE_URL,
            echo=config.is_development(),  # 开发环境打印 SQL
            pool_pre_ping=True,  # 连接池健康检查
            pool_recycle=3600,  # 连接回收时间
        )

        # 创建会话工厂
        self.Session = scoped_session(
            sessionmaker(
                bind=self.engine,
                autocommit=False,
                autoflush=False,
            )
        )

        logger.info(f"数据库已连接: {config.DATABASE_URL}")

    @contextmanager
    def session_scope(self):
        """
        提供事务性会话上下文管理器

        用法:
            with DatabaseSession() as session:
                user = session.query(User).first()
                session.commit()
        """
        session = self.Session()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"数据库会话错误: {e}")
            raise
        finally:
            session.close()

    def init_database(self):
        """初始化数据库（创建表）"""
        from src.models.base import Base
        from src.models.user import User  # 导入所有模型

        logger.info("正在初始化数据库...")
        Base.metadata.create_all(self.engine)
        logger.info("数据库初始化完成")

    def drop_all(self):
        """删除所有表（危险操作！）"""
        from src.models.base import Base

        logger.warning("正在删除所有数据库表...")
        Base.metadata.drop_all(self.engine)
        logger.warning("所有表已删除")


# 全局数据库管理器实例
db_manager = DatabaseManager()

# 导出会话上下文管理器
DatabaseSession = db_manager.session_scope

__all__ = ["DatabaseManager", "DatabaseSession", "db_manager"]
