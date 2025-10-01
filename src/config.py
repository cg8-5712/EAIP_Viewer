"""
应用配置模块
从环境变量和配置文件加载配置
"""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# 加载 .env 文件
load_dotenv()

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent


class Config:
    """应用配置类"""

    # ==================== 应用基础配置 ====================
    APP_NAME = "EAIP Viewer"
    APP_VERSION = "0.1.0"
    APP_ENV = os.getenv("APP_ENV", "development")

    # ==================== 目录配置 ====================
    DATA_DIR = BASE_DIR / "data"
    CACHE_DIR = DATA_DIR / "cache"
    CHARTS_DIR = DATA_DIR / "charts"
    LOGS_DIR = BASE_DIR / "logs"

    # 确保目录存在
    DATA_DIR.mkdir(exist_ok=True)
    CACHE_DIR.mkdir(exist_ok=True)
    CHARTS_DIR.mkdir(exist_ok=True)
    LOGS_DIR.mkdir(exist_ok=True)

    # ==================== 数据库配置 ====================
    DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/database.db")

    # ==================== 加密配置 ====================
    ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY", "change-this-in-production")

    # ==================== 日志配置 ====================
    LOG_LEVEL = os.getenv("LOG_LEVEL", "DEBUG")
    LOG_FILE = LOGS_DIR / "eaip_viewer.log"
    LOG_ROTATION = os.getenv("LOG_ROTATION", "10 MB")
    LOG_RETENTION = os.getenv("LOG_RETENTION", "30 days")

    # ==================== OTA 更新配置 ====================
    UPDATE_SERVER_URL = os.getenv("UPDATE_SERVER_URL", "")
    UPDATE_CHECK_INTERVAL = int(os.getenv("UPDATE_CHECK_INTERVAL", "3600"))

    # ==================== QML 配置 ====================
    QML_DEBUG = os.getenv("QML_DEBUG", "0") == "1"
    QML_HOT_RELOAD = os.getenv("QML_HOT_RELOAD", "0") == "1"

    # ==================== 性能配置 ====================
    CACHE_SIZE_MB = int(os.getenv("CACHE_SIZE_MB", "100"))
    MAX_WORKERS = int(os.getenv("MAX_WORKERS", "4"))
    PDF_RENDER_DPI = int(os.getenv("PDF_RENDER_DPI", "150"))

    # ==================== 安全配置 ====================
    SESSION_EXPIRE_DAYS = int(os.getenv("SESSION_EXPIRE_DAYS", "30"))
    MAX_LOGIN_ATTEMPTS = int(os.getenv("MAX_LOGIN_ATTEMPTS", "5"))
    LOCKOUT_MINUTES = int(os.getenv("LOCKOUT_MINUTES", "15"))

    # ==================== 航图类型配置 ====================
    CHART_TYPES = [
        "ADC",      # Aerodrome Chart - 机场图
        "APDC",     # Aircraft Parking/Docking Chart - 机位/停机图
        "GMC",      # Ground Movement Chart - 地面活动图
        "DGS",      # Docking Guidance System - 停靠引导系统图
        "AOC",      # Aircraft Operating Chart - 航空器运行图
        "PATC",     # Precision Approach Terrain Chart - 精密进近地形图
        "FDA",      # Final Descent Area - 燃油排放区域图
        "ATCMAS",   # ATC Minimum Altitude Sector - 空管最低高度扇区图
        "SID",      # Standard Instrument Departure - 标准仪表离场程序图
        "STAR",     # Standard Terminal Arrival Route - 标准进场程序图
        "WAYPOINT LIST",  # 航路点列表
        "DATABASE CODING TABLE",  # 数据库编码表
        "IAC",      # Instrument Approach Chart - 仪表进近图
        "ATCSMAC",  # ATC Surveillance Minimum Altitude Chart - 空管监视最低高度图
    ]

    @classmethod
    def is_development(cls) -> bool:
        """是否为开发环境"""
        return cls.APP_ENV == "development"

    @classmethod
    def is_production(cls) -> bool:
        """是否为生产环境"""
        return cls.APP_ENV == "production"

    @classmethod
    def is_testing(cls) -> bool:
        """是否为测试环境"""
        return cls.APP_ENV == "testing"


# 全局配置实例
config = Config()
