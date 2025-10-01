"""
AIPKG 打包工具
从原始航图目录创建加密的 .aipkg 包
"""

import os
import gzip
import hashlib
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from io import BytesIO

from src.core.aipkg_format import (
    AIPKGHeader,
    FileEntry,
    PackageIndex,
    COMPRESSION_GZIP,
    COMPRESSION_NONE,
    HEADER_SIZE
)
from src.core.encryption_utils import (
    generate_salt,
    generate_iv,
    derive_master_key,
    encrypt_data,
    compute_sha256,
    encode_base64,
    verify_password_strength
)
from src.utils.logger import logger


class AIPKGBuilder:
    """
    AIPKG 包构建器

    负责扫描航图目录，压缩、加密文件，并打包成 .aipkg 格式
    """

    def __init__(self):
        self.compression_level = 6  # gzip 压缩级别 (1-9)
        self.enable_compression = True
        self.master_key: Optional[bytes] = None
        self.master_salt: Optional[bytes] = None

    def create_package(
        self,
        source_dir: str,
        output_path: str,
        password: str,
        eaip_version: Optional[str] = None,
        compression: str = 'gzip',
        compression_level: int = 6,
        progress_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> Dict[str, Any]:
        """
        创建 AIPKG 包

        Args:
            source_dir: 源目录（Terminal 目录）
            output_path: 输出的 .aipkg 文件路径
            password: 加密密码
            eaip_version: EAIP 版本（如 EAIP2025-07.V1.4）
            compression: 压缩算法 ('gzip', 'none')
            compression_level: 压缩级别 (1-9)
            progress_callback: 进度回调函数 (current, total, message)

        Returns:
            打包结果统计
        """
        logger.info("=" * 60)
        logger.info("Starting AIPKG package creation")
        logger.info(f"Source: {source_dir}")
        logger.info(f"Output: {output_path}")
        logger.info("=" * 60)

        # 验证密码强度
        is_valid, error_msg = verify_password_strength(password)
        if not is_valid:
            raise ValueError(f"Weak password: {error_msg}")

        # 设置压缩
        self.enable_compression = (compression.lower() == 'gzip')
        self.compression_level = compression_level

        # 验证源目录
        source_path = Path(source_dir)
        if not source_path.exists():
            raise FileNotFoundError(f"Source directory not found: {source_dir}")

        # 自动检测 EAIP 版本
        if not eaip_version:
            eaip_version = self._detect_eaip_version(source_path)
            logger.info(f"Detected EAIP version: {eaip_version}")

        # 生成加密材料
        self.master_salt = generate_salt()
        self.master_key = derive_master_key(password, self.master_salt)
        logger.info("Generated encryption materials")

        # 扫描文件
        logger.info("Scanning files...")
        if progress_callback:
            progress_callback(0, 100, "扫描文件...")

        file_list = self._scan_files(source_path)
        logger.info(f"Found {len(file_list)} files")

        # 扫描机场和分类
        airports = self._extract_airports(file_list)
        categories = self._get_standard_categories()

        # 创建临时输出文件
        output_path_obj = Path(output_path)
        output_path_obj.parent.mkdir(parents=True, exist_ok=True)
        temp_output = str(output_path_obj) + '.tmp'

        try:
            # 1. 处理所有文件（压缩 + 加密）
            logger.info("Processing and encrypting files...")
            file_entries = []
            encrypted_blocks = []
            current_offset = 0  # 相对于数据区的偏移

            for idx, file_info in enumerate(file_list):
                if progress_callback:
                    progress = int((idx + 1) / len(file_list) * 70)  # 0-70%
                    progress_callback(
                        idx + 1,
                        len(file_list),
                        f"处理文件 {idx + 1}/{len(file_list)}: {file_info['file_name']}"
                    )

                # 处理单个文件
                entry, encrypted_data = self._process_file(file_info, current_offset)
                file_entries.append(entry)
                encrypted_blocks.append(encrypted_data)
                current_offset += len(encrypted_data)

            # 2. 构建索引
            logger.info("Building index...")
            if progress_callback:
                progress_callback(0, 100, "构建索引...")

            package_info = {
                'eaip_version': eaip_version,
                'effective_date': None,
                'expiry_date': None,
                'created_at': datetime.now().isoformat(),
                'airports_count': len(airports),
                'charts_count': len(file_entries),
                'total_size': sum(e.original_size for e in file_entries),
                'compression_ratio': self._calculate_compression_ratio(file_entries)
            }

            index = PackageIndex(
                package_info=package_info,
                airports=airports,
                categories=categories,
                files=file_entries
            )

            # 3. 加密索引
            index_json = index.to_json()
            index_iv = generate_iv()
            encrypted_index, _ = encrypt_data(
                index_json.encode('utf-8'),
                self.master_key,
                index_iv,
                associated_data=b'AIPKG_INDEX_V1'
            )

            # 4. 计算最终偏移
            index_offset = HEADER_SIZE
            index_length = len(encrypted_index)
            data_start_offset = index_offset + index_length

            # 调整所有文件的偏移量（加上 Header 和 Index 的大小）
            for entry in file_entries:
                entry.offset += data_start_offset

            # 重新构建索引（包含更新后的偏移）
            index.files = file_entries
            index_json = index.to_json()
            encrypted_index, _ = encrypt_data(
                index_json.encode('utf-8'),
                self.master_key,
                index_iv,
                associated_data=b'AIPKG_INDEX_V1'
            )

            # 5. 写入所有数据
            logger.info("Writing package...")
            with open(temp_output, 'w+b') as f:  # 使用 w+b 模式，允许读写
                # 写入占位 Header
                placeholder_header = AIPKGHeader()
                f.write(placeholder_header.to_bytes())

                # 写入加密索引
                f.write(encrypted_index)

                # 写入所有数据块
                for idx, encrypted_data in enumerate(encrypted_blocks):
                    if progress_callback:
                        progress = 70 + int((idx + 1) / len(encrypted_blocks) * 20)  # 70-90%
                        progress_callback(idx + 1, len(encrypted_blocks), f"写入数据块 {idx + 1}/{len(encrypted_blocks)}")
                    f.write(encrypted_data)

                # 6. 计算文件哈希
                logger.info("Computing file hash...")
                if progress_callback:
                    progress_callback(0, 100, "计算文件哈希...")

                f.seek(HEADER_SIZE)  # 跳过 Header
                file_hasher = hashlib.sha256()
                while chunk := f.read(8192):
                    file_hasher.update(chunk)
                file_hash = file_hasher.digest()

                # 7. 写入最终 Header
                logger.info("Writing final header...")
                final_header = AIPKGHeader(
                    index_offset=index_offset,
                    index_length=index_length,
                    index_iv=index_iv,
                    master_salt=self.master_salt,
                    file_hash=file_hash,
                    created_timestamp=int(datetime.now().timestamp()),
                    total_files=len(file_entries),
                    total_data_size=sum(e.original_size for e in file_entries),
                    compression_algo=COMPRESSION_GZIP if self.enable_compression else COMPRESSION_NONE,
                    metadata=eaip_version[:128]
                )

                f.seek(0)
                f.write(final_header.to_bytes())

            # 9. 移动到最终位置
            if os.path.exists(output_path):
                os.remove(output_path)
            os.rename(temp_output, output_path)

            if progress_callback:
                progress_callback(100, 100, "打包完成！")

            # 10. 生成统计
            final_size = os.path.getsize(output_path)
            result = {
                'success': True,
                'output_path': output_path,
                'eaip_version': eaip_version,
                'total_files': len(file_entries),
                'airports_count': len(airports),
                'original_size': sum(e.original_size for e in file_entries),
                'compressed_size': sum(e.compressed_size for e in file_entries),
                'final_size': final_size,
                'compression_ratio': self._calculate_compression_ratio(file_entries),
                'created_at': datetime.now().isoformat()
            }

            logger.info("=" * 60)
            logger.info("Package created successfully!")
            logger.info(f"  Output: {output_path}")
            logger.info(f"  Files: {result['total_files']}")
            logger.info(f"  Airports: {result['airports_count']}")
            logger.info(f"  Original size: {result['original_size'] / 1024 / 1024:.2f} MB")
            logger.info(f"  Final size: {result['final_size'] / 1024 / 1024:.2f} MB")
            logger.info(f"  Compression ratio: {result['compression_ratio'] * 100:.1f}%")
            logger.info("=" * 60)

            return result

        except Exception as e:
            logger.error(f"Failed to create package: {e}", exc_info=True)
            # 清理临时文件
            if os.path.exists(temp_output):
                os.remove(temp_output)
            raise

        finally:
            # 清除敏感数据
            self.master_key = None

    def _scan_files(self, terminal_dir: Path) -> List[Dict[str, Any]]:
        """
        扫描 Terminal 目录下的所有 PDF 文件

        Args:
            terminal_dir: Terminal 目录路径

        Returns:
            文件信息列表
        """
        file_list = []

        # 遍历所有机场目录
        for airport_dir in terminal_dir.iterdir():
            if not airport_dir.is_dir():
                continue

            # 机场 ICAO 代码（4 个字符）
            if len(airport_dir.name) != 4:
                continue

            icao = airport_dir.name

            # 遍历各个分类目录
            for category_dir in airport_dir.iterdir():
                if not category_dir.is_dir():
                    continue

                category = self._normalize_category_code(category_dir.name)

                # 扫描 PDF 文件
                for pdf_file in category_dir.glob('*.pdf'):
                    file_info = self._parse_chart_filename(pdf_file, icao, category)
                    if file_info:
                        file_list.append(file_info)

        return sorted(file_list, key=lambda x: (x['airport'], x['category'], x['file_name']))

    def _parse_chart_filename(self, pdf_path: Path, airport: str, category: str) -> Optional[Dict[str, Any]]:
        """
        解析航图文件名，提取元数据

        Args:
            pdf_path: PDF 文件路径
            airport: 机场 ICAO
            category: 分类代码

        Returns:
            文件信息字典
        """
        file_name = pdf_path.name
        file_size = pdf_path.stat().st_size

        # 生成文件 ID
        file_id = f"{airport.lower()}_{category.lower()}_{hashlib.md5(file_name.encode()).hexdigest()[:8]}"

        # 解析文件名
        # 例如: ZBAA-7A01-SID RNAV RWY01-36L-36R(IDKEX).pdf
        chart_number = None
        title = None
        runway = None
        procedure = None

        match = re.match(r'([A-Z]{4}-[\dA-Z]+)-(.+)\.pdf', file_name, re.IGNORECASE)
        if match:
            chart_number = match.group(1).upper()
            title = match.group(2)

            # 提取跑道
            rwy_match = re.search(r'RWY[\s]*([\dLRC-]+)', title, re.IGNORECASE)
            if rwy_match:
                runway = rwy_match.group(1)

            # 提取程序名称
            proc_match = re.search(r'\(([^)]+)\)', title)
            if proc_match:
                procedure = proc_match.group(1)
        else:
            title = file_name.replace('.pdf', '')

        return {
            'id': file_id,
            'airport': airport,
            'category': category,
            'file_path': str(pdf_path.absolute()),
            'file_name': file_name,
            'title': title,
            'chart_number': chart_number,
            'runway': runway,
            'procedure': procedure,
            'file_size': file_size
        }

    def _process_file(self, file_info: Dict[str, Any], offset: int) -> tuple[FileEntry, bytes]:
        """
        处理单个文件：压缩 + 加密

        Args:
            file_info: 文件信息
            offset: 在包中的偏移

        Returns:
            (FileEntry, 加密后的数据)
        """
        # 读取文件
        with open(file_info['file_path'], 'rb') as f:
            pdf_content = f.read()

        original_size = len(pdf_content)

        # 计算原始文件哈希
        file_hash = hashlib.sha256(pdf_content).hexdigest()

        # 压缩
        if self.enable_compression:
            compressed = gzip.compress(pdf_content, compresslevel=self.compression_level)
        else:
            compressed = pdf_content

        compressed_size = len(compressed)

        # 加密
        iv = generate_iv()
        encrypted, _ = encrypt_data(
            compressed,
            self.master_key,
            iv,
            associated_data=file_info['id'].encode('utf-8')
        )

        # 创建文件条目
        entry = FileEntry(
            id=file_info['id'],
            airport=file_info['airport'],
            category=file_info['category'],
            file_name=file_info['file_name'],
            title=file_info['title'],
            chart_number=file_info.get('chart_number'),
            runway=file_info.get('runway'),
            procedure=file_info.get('procedure'),
            offset=offset,
            compressed_size=compressed_size,
            original_size=original_size,
            iv=encode_base64(iv),
            file_hash=file_hash,
            created_at=datetime.now().isoformat()
        )

        logger.debug(
            f"Processed: {file_info['file_name']} "
            f"({original_size} -> {compressed_size} -> {len(encrypted)} bytes)"
        )

        return entry, encrypted

    def _extract_airports(self, file_list: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """提取机场列表"""
        airports_dict = {}

        for file_info in file_list:
            icao = file_info['airport']
            if icao not in airports_dict:
                airports_dict[icao] = {
                    'icao': icao,
                    'name_cn': None,  # 可以从其他来源加载
                    'name_en': None,
                    'file_count': 0
                }
            airports_dict[icao]['file_count'] += 1

        return sorted(airports_dict.values(), key=lambda x: x['icao'])

    def _get_standard_categories(self) -> List[Dict[str, str]]:
        """获取标准航图分类"""
        return [
            {'code': 'ADC', 'name_cn': '机场图', 'name_en': 'Aerodrome Chart'},
            {'code': 'AOC', 'name_cn': '航空器运行图', 'name_en': 'Aircraft Operating Chart'},
            {'code': 'APDC', 'name_cn': '机场停机位图', 'name_en': 'Airport Diagram'},
            {'code': 'GMC', 'name_cn': '地面移动图', 'name_en': 'Ground Movement Chart'},
            {'code': 'PATC', 'name_cn': '精密进近地形图', 'name_en': 'Precision Approach Terrain Chart'},
            {'code': 'SID', 'name_cn': '标准仪表离场', 'name_en': 'Standard Instrument Departure'},
            {'code': 'STAR', 'name_cn': '标准终端进场', 'name_en': 'Standard Terminal Arrival Route'},
            {'code': 'IAC', 'name_cn': '仪表进近图', 'name_en': 'Instrument Approach Chart'},
            {'code': 'FDA', 'name_cn': '最后下降区图', 'name_en': 'Final Descent Area Chart'},
            {'code': 'DATABASE_CODING_TABLE', 'name_cn': '数据库编码表', 'name_en': 'Database Coding Table'},
            {'code': 'WAYPOINT_LIST', 'name_cn': '航路点列表', 'name_en': 'Waypoint List'},
        ]

    def _normalize_category_code(self, category_name: str) -> str:
        """规范化分类代码"""
        return category_name.strip().replace(' ', '_').upper()

    def _detect_eaip_version(self, source_path: Path) -> str:
        """
        自动检测 EAIP 版本

        Args:
            source_path: 源目录

        Returns:
            EAIP 版本字符串
        """
        # 尝试从父目录名解析
        parent = source_path.parent
        if parent.name.startswith('EAIP'):
            return parent.name

        # 尝试从祖父目录
        grandparent = parent.parent
        if grandparent.name.startswith('EAIP'):
            return grandparent.name

        # 默认值
        return f"EAIP{datetime.now().strftime('%Y-%m')}.V1.0"

    def _calculate_compression_ratio(self, file_entries: List[FileEntry]) -> float:
        """计算压缩率"""
        total_original = sum(e.original_size for e in file_entries)
        total_compressed = sum(e.compressed_size for e in file_entries)

        if total_original == 0:
            return 0.0

        return total_compressed / total_original
