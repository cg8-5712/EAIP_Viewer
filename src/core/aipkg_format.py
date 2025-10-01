"""
AIPKG 文件格式定义
定义 .aipkg 文件的二进制格式和相关数据结构
"""

import struct
import json
from typing import Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


# 常量定义
MAGIC_NUMBER = b'AIPK'
CURRENT_VERSION_MAJOR = 1
CURRENT_VERSION_MINOR = 0
HEADER_SIZE = 512

# 压缩算法
COMPRESSION_NONE = 0
COMPRESSION_GZIP = 1
COMPRESSION_ZSTD = 2

# 加密算法
ENCRYPTION_AES_256_GCM = 1


@dataclass
class AIPKGHeader:
    """
    AIPKG 文件头结构 (512 bytes)

    Attributes:
        magic: 魔数 "AIPK" (4 bytes)
        version_major: 主版本号 (2 bytes)
        version_minor: 次版本号 (2 bytes)
        index_offset: 索引块起始位置 (8 bytes)
        index_length: 索引块长度 (8 bytes)
        index_iv: 索引加密 IV (32 bytes)
        master_salt: 主密钥派生盐值 (32 bytes)
        file_hash: 文件哈希 (64 bytes)
        created_timestamp: 创建时间戳 (8 bytes)
        total_files: 总文件数 (8 bytes)
        total_data_size: 总数据大小 (8 bytes)
        compression_algo: 压缩算法 (4 bytes)
        encryption_algo: 加密算法 (4 bytes)
        metadata: 元数据 JSON (128 bytes)
        reserved: 保留字段 (200 bytes)
    """

    magic: bytes = MAGIC_NUMBER
    version_major: int = CURRENT_VERSION_MAJOR
    version_minor: int = CURRENT_VERSION_MINOR
    index_offset: int = 0
    index_length: int = 0
    index_iv: bytes = b''
    master_salt: bytes = b''
    file_hash: bytes = b''
    created_timestamp: int = 0
    total_files: int = 0
    total_data_size: int = 0
    compression_algo: int = COMPRESSION_GZIP
    encryption_algo: int = ENCRYPTION_AES_256_GCM
    metadata: str = ''
    reserved: bytes = b''

    def __post_init__(self):
        """初始化后验证"""
        if not self.created_timestamp:
            self.created_timestamp = int(datetime.now().timestamp())

        # 确保字节字段长度正确
        if len(self.index_iv) == 0:
            self.index_iv = b'\x00' * 32
        if len(self.master_salt) == 0:
            self.master_salt = b'\x00' * 32
        if len(self.file_hash) == 0:
            self.file_hash = b'\x00' * 64
        if len(self.reserved) == 0:
            self.reserved = b'\x00' * 200

    def to_bytes(self) -> bytes:
        """
        将 Header 转换为二进制格式

        Returns:
            512 字节的二进制数据
        """
        # 截断或填充 metadata 到 128 字节
        metadata_bytes = self.metadata.encode('utf-8')[:128]
        metadata_bytes = metadata_bytes.ljust(128, b'\x00')

        # 打包数据
        data = struct.pack(
            '<4sHHQQ32s32s64sQQQII128s200s',
            self.magic,
            self.version_major,
            self.version_minor,
            self.index_offset,
            self.index_length,
            self.index_iv,
            self.master_salt,
            self.file_hash,
            self.created_timestamp,
            self.total_files,
            self.total_data_size,
            self.compression_algo,
            self.encryption_algo,
            metadata_bytes,
            self.reserved
        )

        assert len(data) == HEADER_SIZE, f"Header size mismatch: {len(data)} != {HEADER_SIZE}"
        return data

    @classmethod
    def from_bytes(cls, data: bytes) -> 'AIPKGHeader':
        """
        从二进制数据解析 Header

        Args:
            data: 512 字节的二进制数据

        Returns:
            AIPKGHeader 对象

        Raises:
            ValueError: 如果数据格式错误
        """
        if len(data) != HEADER_SIZE:
            raise ValueError(f"Invalid header size: {len(data)}, expected {HEADER_SIZE}")

        # 解包数据
        unpacked = struct.unpack(
            '<4sHHQQ32s32s64sQQQII128s200s',
            data
        )

        magic = unpacked[0]
        if magic != MAGIC_NUMBER:
            raise ValueError(f"Invalid magic number: {magic}, expected {MAGIC_NUMBER}")

        # 解析 metadata
        metadata_bytes = unpacked[13].rstrip(b'\x00')
        metadata = metadata_bytes.decode('utf-8', errors='ignore')

        return cls(
            magic=magic,
            version_major=unpacked[1],
            version_minor=unpacked[2],
            index_offset=unpacked[3],
            index_length=unpacked[4],
            index_iv=unpacked[5],
            master_salt=unpacked[6],
            file_hash=unpacked[7],
            created_timestamp=unpacked[8],
            total_files=unpacked[9],
            total_data_size=unpacked[10],
            compression_algo=unpacked[11],
            encryption_algo=unpacked[12],
            metadata=metadata,
            reserved=unpacked[14]
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'version': f'{self.version_major}.{self.version_minor}',
            'index_offset': self.index_offset,
            'index_length': self.index_length,
            'created_at': datetime.fromtimestamp(self.created_timestamp).isoformat(),
            'total_files': self.total_files,
            'total_data_size': self.total_data_size,
            'compression_algo': self._get_compression_name(),
            'encryption_algo': self._get_encryption_name(),
            'metadata': self.metadata
        }

    def _get_compression_name(self) -> str:
        """获取压缩算法名称"""
        names = {
            COMPRESSION_NONE: 'none',
            COMPRESSION_GZIP: 'gzip',
            COMPRESSION_ZSTD: 'zstd'
        }
        return names.get(self.compression_algo, 'unknown')

    def _get_encryption_name(self) -> str:
        """获取加密算法名称"""
        names = {
            ENCRYPTION_AES_256_GCM: 'AES-256-GCM'
        }
        return names.get(self.encryption_algo, 'unknown')


@dataclass
class FileEntry:
    """
    文件条目信息

    Attributes:
        id: 文件唯一 ID
        airport: 机场 ICAO 代码
        category: 航图分类
        file_name: 文件名
        title: 标题
        chart_number: 图号
        runway: 跑道
        procedure: 程序名称
        offset: 在包中的字节偏移
        compressed_size: 压缩后大小
        original_size: 原始大小
        iv: 加密 IV
        file_hash: 文件哈希
        page_count: 页数
        created_at: 创建时间
    """

    id: str
    airport: str
    category: str
    file_name: str
    title: str
    chart_number: Optional[str] = None
    runway: Optional[str] = None
    procedure: Optional[str] = None
    offset: int = 0
    compressed_size: int = 0
    original_size: int = 0
    iv: str = ''  # Base64 编码
    file_hash: str = ''  # Hex 编码
    page_count: int = 0
    created_at: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典（用于 JSON 序列化）"""
        return {
            'id': self.id,
            'airport': self.airport,
            'category': self.category,
            'file_name': self.file_name,
            'title': self.title,
            'chart_number': self.chart_number,
            'runway': self.runway,
            'procedure': self.procedure,
            'offset': self.offset,
            'compressed_size': self.compressed_size,
            'original_size': self.original_size,
            'iv': self.iv,
            'file_hash': self.file_hash,
            'page_count': self.page_count,
            'created_at': self.created_at
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'FileEntry':
        """从字典创建"""
        return cls(**data)


@dataclass
class PackageIndex:
    """
    包索引数据结构

    Attributes:
        package_info: 包信息
        airports: 机场列表
        categories: 分类列表
        files: 文件列表
    """

    package_info: Dict[str, Any]
    airports: list
    categories: list
    files: list

    def to_json(self) -> str:
        """转换为 JSON 字符串"""
        data = {
            'package_info': self.package_info,
            'airports': self.airports,
            'categories': self.categories,
            'files': [f.to_dict() if isinstance(f, FileEntry) else f for f in self.files]
        }
        return json.dumps(data, ensure_ascii=False, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'PackageIndex':
        """从 JSON 字符串解析"""
        data = json.loads(json_str)

        # 将文件字典转换为 FileEntry 对象
        files = [FileEntry.from_dict(f) if isinstance(f, dict) else f for f in data['files']]

        return cls(
            package_info=data['package_info'],
            airports=data['airports'],
            categories=data['categories'],
            files=files
        )

    def get_file_by_id(self, file_id: str) -> Optional[FileEntry]:
        """根据 ID 获取文件条目"""
        for f in self.files:
            entry = f if isinstance(f, FileEntry) else FileEntry.from_dict(f)
            if entry.id == file_id:
                return entry
        return None


def validate_header(header: AIPKGHeader) -> tuple[bool, str]:
    """
    验证 Header 有效性

    Args:
        header: AIPKGHeader 对象

    Returns:
        (是否有效, 错误信息)
    """
    # 检查魔数
    if header.magic != MAGIC_NUMBER:
        return False, f"Invalid magic number: {header.magic}"

    # 检查版本
    if header.version_major > CURRENT_VERSION_MAJOR:
        return False, f"Unsupported version: {header.version_major}.{header.version_minor}"

    # 检查索引偏移
    if header.index_offset < HEADER_SIZE:
        return False, f"Invalid index offset: {header.index_offset}"

    # 检查索引长度
    if header.index_length == 0:
        return False, "Index length is zero"

    # 检查 IV 和 Salt
    if len(header.index_iv) != 32:
        return False, f"Invalid index IV length: {len(header.index_iv)}"

    if len(header.master_salt) != 32:
        return False, f"Invalid master salt length: {len(header.master_salt)}"

    return True, ""
