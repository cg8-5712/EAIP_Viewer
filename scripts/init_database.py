"""
数据库初始化脚本
创建数据库表结构
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from src.core.database import db_manager
from src.utils.logger import setup_logger, logger


def init_database():
    """初始化数据库"""
    setup_logger()

    logger.info("=" * 60)
    logger.info("开始初始化数据库")
    logger.info("=" * 60)

    try:
        # 创建所有表
        db_manager.init_database()

        logger.info("✅ 数据库初始化成功！")
        logger.info("=" * 60)

        return 0

    except Exception as e:
        logger.error(f"❌ 数据库初始化失败: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(init_database())
