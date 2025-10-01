"""
日志配置模块
使用 loguru 配置应用日志
"""

import sys
from loguru import logger
from src.config import config


def setup_logger():
    """配置日志系统"""

    # 移除默认的日志处理器
    logger.remove()

    # 控制台日志（开发环境）
    if config.is_development():
        logger.add(
            sys.stderr,
            format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>",
            level=config.LOG_LEVEL,
            colorize=True,
        )

    # 文件日志
    logger.add(
        config.LOG_FILE,
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level=config.LOG_LEVEL,
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        compression="zip",
        encoding="utf-8",
    )

    # 错误日志单独文件
    logger.add(
        config.LOGS_DIR / "errors.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation=config.LOG_ROTATION,
        retention=config.LOG_RETENTION,
        compression="zip",
        encoding="utf-8",
    )

    logger.info(f"日志系统已初始化 - Level: {config.LOG_LEVEL}")
    logger.info(f"日志文件: {config.LOG_FILE}")


# 导出 logger 实例
__all__ = ["logger", "setup_logger"]
