"""
航图数据模型
管理 EAIP 航图文件的数据库模型
"""

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base, TimestampMixin


class ChartVersion(Base, TimestampMixin):
    """EAIP 版本信息"""

    __tablename__ = "chart_versions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_name = Column(String(100), unique=True, nullable=False, index=True, comment="版本名称，如 EAIP2025-07.V1.4")
    effective_date = Column(DateTime, nullable=True, comment="生效日期")
    expiry_date = Column(DateTime, nullable=True, comment="过期日期")
    data_path = Column(String(500), nullable=False, comment="数据目录路径")
    is_active = Column(Boolean, default=True, comment="是否激活")
    description = Column(Text, nullable=True, comment="版本描述")

    # 关系
    airports = relationship("Airport", back_populates="version", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ChartVersion(id={self.id}, version_name='{self.version_name}')>"


class Airport(Base, TimestampMixin):
    """机场信息"""

    __tablename__ = "airports"

    id = Column(Integer, primary_key=True, autoincrement=True)
    version_id = Column(Integer, ForeignKey("chart_versions.id", ondelete="CASCADE"), nullable=False)
    icao_code = Column(String(4), nullable=False, index=True, comment="ICAO 代码，如 ZBAA")
    name_cn = Column(String(200), nullable=True, comment="中文名称")
    name_en = Column(String(200), nullable=True, comment="英文名称")
    data_path = Column(String(500), nullable=False, comment="机场数据目录路径")

    # 关系
    version = relationship("ChartVersion", back_populates="airports")
    charts = relationship("Chart", back_populates="airport", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Airport(id={self.id}, icao='{self.icao_code}', name='{self.name_cn}')>"


class ChartCategory(Base, TimestampMixin):
    """航图分类"""

    __tablename__ = "chart_categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(50), unique=True, nullable=False, index=True, comment="分类代码")
    name_cn = Column(String(100), nullable=False, comment="中文名称")
    name_en = Column(String(100), nullable=True, comment="英文名称")
    description = Column(Text, nullable=True, comment="描述")
    sort_order = Column(Integer, default=0, comment="排序顺序")

    # 关系
    charts = relationship("Chart", back_populates="category")

    def __repr__(self):
        return f"<ChartCategory(id={self.id}, code='{self.code}', name='{self.name_cn}')>"


class Chart(Base, TimestampMixin):
    """航图文件"""

    __tablename__ = "charts"

    id = Column(Integer, primary_key=True, autoincrement=True)
    airport_id = Column(Integer, ForeignKey("airports.id", ondelete="CASCADE"), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("chart_categories.id"), nullable=False, index=True)

    file_name = Column(String(500), nullable=False, comment="文件名")
    file_path = Column(String(1000), nullable=False, comment="文件完整路径")
    title = Column(String(500), nullable=True, comment="航图标题")

    # 附加信息
    runway = Column(String(50), nullable=True, comment="适用跑道，如 RWY36R")
    procedure = Column(String(200), nullable=True, comment="程序名称，如 IDKEX, GUVBA")
    chart_number = Column(String(50), nullable=True, comment="图号，如 ZBAA-1A-ADC")

    # 文件信息
    file_size = Column(Integer, nullable=True, comment="文件大小（字节）")
    page_count = Column(Integer, nullable=True, comment="PDF 页数")

    # 缓存信息
    thumbnail_path = Column(String(1000), nullable=True, comment="缩略图路径")

    # 元数据
    metadata_json = Column(Text, nullable=True, comment="其他元数据（JSON格式）")

    # 关系
    airport = relationship("Airport", back_populates="charts")
    category = relationship("ChartCategory", back_populates="charts")

    def __repr__(self):
        return f"<Chart(id={self.id}, title='{self.title}', file='{self.file_name}')>"


# 航图分类的标准数据
STANDARD_CATEGORIES = [
    {"code": "ADC", "name_cn": "机场图", "name_en": "Aerodrome Chart", "sort_order": 1},
    {"code": "AOC", "name_cn": "航空器运行图", "name_en": "Aircraft Operating Chart", "sort_order": 2},
    {"code": "APDC", "name_cn": "机场停机位图", "name_en": "Airport Diagram", "sort_order": 3},
    {"code": "GMC", "name_cn": "地面移动图", "name_en": "Ground Movement Chart", "sort_order": 4},
    {"code": "PATC", "name_cn": "精密进近地形图", "name_en": "Precision Approach Terrain Chart", "sort_order": 5},
    {"code": "SID", "name_cn": "标准仪表离场", "name_en": "Standard Instrument Departure", "sort_order": 6},
    {"code": "STAR", "name_cn": "标准终端进场", "name_en": "Standard Terminal Arrival Route", "sort_order": 7},
    {"code": "IAC", "name_cn": "仪表进近图", "name_en": "Instrument Approach Chart", "sort_order": 8},
    {"code": "FDA", "name_cn": "最后下降区图", "name_en": "Final Descent Area Chart", "sort_order": 9},
    {"code": "DATABASE_CODING_TABLE", "name_cn": "数据库编码表", "name_en": "Database Coding Table", "sort_order": 10},
    {"code": "WAYPOINT_LIST", "name_cn": "航路点列表", "name_en": "Waypoint List", "sort_order": 11},
]
