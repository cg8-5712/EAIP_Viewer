"""
航图扫描服务
扫描航图目录并建立索引
"""

import os
import re
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from src.utils.logger import logger
from src.config import config


class ChartScanner:
    """航图扫描器"""

    def __init__(self, data_root: Optional[str] = None):
        """
        初始化扫描器

        Args:
            data_root: 航图数据根目录，如果为 None 则使用配置文件中的路径
        """
        self.data_root = Path(data_root) if data_root else Path(config.CHART_DATA_ROOT)

        if not self.data_root.exists():
            logger.warning(f"航图数据根目录不存在: {self.data_root}")

    def scan_versions(self) -> List[Dict]:
        """
        扫描所有 EAIP 版本

        Returns:
            版本信息列表
        """
        versions = []

        if not self.data_root.exists():
            logger.error(f"数据根目录不存在: {self.data_root}")
            return versions

        # 扫描 EAIP* 文件夹
        for item in self.data_root.iterdir():
            if item.is_dir() and item.name.startswith("EAIP"):
                version_info = self._parse_version_info(item)
                if version_info:
                    versions.append(version_info)
                    logger.info(f"发现 EAIP 版本: {version_info['version_name']}")

        return sorted(versions, key=lambda x: x["version_name"], reverse=True)

    def scan_airports(self, version_name: str) -> List[Dict]:
        """
        扫描指定版本下的所有机场

        Args:
            version_name: 版本名称，如 EAIP2025-07.V1.4

        Returns:
            机场信息列表
        """
        airports = []
        version_path = self.data_root / version_name / "Terminal"

        if not version_path.exists():
            logger.warning(f"Terminal 目录不存在: {version_path}")
            return airports

        for airport_dir in version_path.iterdir():
            if airport_dir.is_dir() and len(airport_dir.name) == 4:
                airport_info = self._parse_airport_info(airport_dir)
                if airport_info:
                    airports.append(airport_info)
                    logger.debug(f"发现机场: {airport_info['icao_code']}")

        return sorted(airports, key=lambda x: x["icao_code"])

    def scan_charts(self, airport_path: Path) -> List[Dict]:
        """
        扫描指定机场的所有航图

        Args:
            airport_path: 机场目录路径

        Returns:
            航图信息列表
        """
        charts = []

        if not airport_path.exists():
            logger.warning(f"机场目录不存在: {airport_path}")
            return charts

        # 扫描各个航图分类目录
        for category_dir in airport_path.iterdir():
            if not category_dir.is_dir():
                continue

            category_code = self._normalize_category_code(category_dir.name)

            # 扫描该分类下的所有 PDF 文件
            for pdf_file in category_dir.glob("*.pdf"):
                chart_info = self._parse_chart_info(pdf_file, category_code)
                if chart_info:
                    charts.append(chart_info)

        logger.info(f"扫描到 {len(charts)} 个航图文件: {airport_path.name}")
        return charts

    def _parse_version_info(self, version_path: Path) -> Optional[Dict]:
        """解析版本信息"""
        try:
            # 解析版本名称，如 EAIP2025-07.V1.4
            version_name = version_path.name
            match = re.match(r"EAIP(\d{4})-(\d{2})\.V([\d.]+)", version_name)

            if match:
                year, month, version = match.groups()
                # 假设在该月的第一天生效
                effective_date = datetime(int(year), int(month), 1)
            else:
                effective_date = None

            return {
                "version_name": version_name,
                "effective_date": effective_date,
                "expiry_date": None,  # 需要手动设置或从文件中读取
                "data_path": str(version_path.absolute()),
                "is_active": True,
            }
        except Exception as e:
            logger.error(f"解析版本信息失败: {version_path}, 错误: {e}")
            return None

    def _parse_airport_info(self, airport_path: Path) -> Optional[Dict]:
        """解析机场信息"""
        try:
            icao_code = airport_path.name

            # 尝试从 index.json 读取机场名称
            name_cn = None
            name_en = None

            index_json = airport_path / "index.json"
            if index_json.exists():
                import json

                with open(index_json, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    name_cn = data.get("name_cn")
                    name_en = data.get("name_en")

            # 如果没有 index.json，尝试从 PDF 文件名推断
            if not name_cn:
                pdf_files = list(airport_path.glob(f"{icao_code}-*.pdf"))
                if pdf_files:
                    # 从文件名解析，如 ZBAA-BEIJING-Capital.pdf
                    match = re.match(rf"{icao_code}-(.+)\.pdf", pdf_files[0].name)
                    if match:
                        name_parts = match.group(1).split("-")
                        name_en = " ".join(name_parts) if len(name_parts) > 1 else name_parts[0]

            return {
                "icao_code": icao_code,
                "name_cn": name_cn,
                "name_en": name_en,
                "data_path": str(airport_path.absolute()),
            }
        except Exception as e:
            logger.error(f"解析机场信息失败: {airport_path}, 错误: {e}")
            return None

    def _parse_chart_info(self, pdf_path: Path, category_code: str) -> Optional[Dict]:
        """解析航图文件信息"""
        try:
            file_name = pdf_path.name
            file_size = pdf_path.stat().st_size

            # 解析文件名获取信息
            # 例如: ZBAA-7A01-SID RNAV RWY01-36L-36R(IDKEX).pdf
            # 例如: ZBAA-20A-IAC RNAV CAT-I-II ILS-DME z RWY01.pdf

            chart_number = None
            title = None
            runway = None
            procedure = None

            # 尝试解析图号（如 ZBAA-7A01）
            match = re.match(r"([A-Z]{4}-[\dA-Z]+)-(.+)\.pdf", file_name)
            if match:
                chart_number = match.group(1)
                title = match.group(2)

                # 提取跑道信息
                rwy_match = re.search(r"RWY[\s]*([\dLRC-]+)", title)
                if rwy_match:
                    runway = rwy_match.group(1)

                # 提取程序名称（括号内的内容）
                proc_match = re.search(r"\(([^)]+)\)", title)
                if proc_match:
                    procedure = proc_match.group(1)
            else:
                title = file_name.replace(".pdf", "")

            return {
                "file_name": file_name,
                "file_path": str(pdf_path.absolute()),
                "title": title,
                "chart_number": chart_number,
                "runway": runway,
                "procedure": procedure,
                "category_code": category_code,
                "file_size": file_size,
            }
        except Exception as e:
            logger.error(f"解析航图文件信息失败: {pdf_path}, 错误: {e}")
            return None

    def _normalize_category_code(self, category_name: str) -> str:
        """
        规范化分类代码

        Args:
            category_name: 分类目录名称

        Returns:
            规范化的分类代码
        """
        # 将空格替换为下划线，转大写
        return category_name.strip().replace(" ", "_").upper()


def scan_and_index_charts(version_name: Optional[str] = None) -> Dict:
    """
    扫描并索引航图文件

    Args:
        version_name: 要扫描的版本名称，如果为 None 则扫描默认版本

    Returns:
        扫描结果统计
    """
    scanner = ChartScanner()

    # 如果没有指定版本，使用配置中的默认版本
    if not version_name:
        version_name = config.DEFAULT_EAIP_VERSION

    logger.info(f"开始扫描 EAIP 版本: {version_name}")

    stats = {
        "version": version_name,
        "airports_count": 0,
        "charts_count": 0,
        "categories": set(),
    }

    # 扫描机场
    airports = scanner.scan_airports(version_name)
    stats["airports_count"] = len(airports)

    # 扫描每个机场的航图
    for airport_info in airports:
        airport_path = Path(airport_info["data_path"])
        charts = scanner.scan_charts(airport_path)
        stats["charts_count"] += len(charts)

        for chart in charts:
            stats["categories"].add(chart["category_code"])

    stats["categories"] = list(stats["categories"])

    logger.info(f"扫描完成: {stats['airports_count']} 个机场, {stats['charts_count']} 个航图")

    return stats
