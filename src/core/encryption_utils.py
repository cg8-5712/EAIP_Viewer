"""
加密工具函数
提供 AIPKG 包所需的加密、解密功能
"""

import os
import hashlib
import base64
from typing import Tuple, Optional

from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend

from src.utils.logger import logger


# 常量
KEY_SIZE = 32  # 256 bits
IV_SIZE = 12   # 96 bits (推荐用于 AES-GCM)
SALT_SIZE = 32  # 256 bits
PBKDF2_ITERATIONS = 100000  # 100k 迭代


def generate_random_bytes(size: int) -> bytes:
    """
    生成安全的随机字节

    Args:
        size: 字节数

    Returns:
        随机字节
    """
    return os.urandom(size)


def generate_salt() -> bytes:
    """
    生成随机盐值

    Returns:
        32 字节的随机盐值
    """
    return generate_random_bytes(SALT_SIZE)


def generate_iv() -> bytes:
    """
    生成随机 IV（初始化向量）

    Returns:
        12 字节的随机 IV（AES-GCM 推荐长度）
    """
    return generate_random_bytes(IV_SIZE)


def derive_master_key(password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> bytes:
    """
    从用户密码派生 Master Key

    使用 PBKDF2-HMAC-SHA256 算法

    Args:
        password: 用户密码
        salt: 盐值（32 bytes）
        iterations: 迭代次数（默认 100,000）

    Returns:
        32 字节的 Master Key

    Raises:
        ValueError: 如果参数无效
    """
    if not password:
        raise ValueError("Password cannot be empty")

    if len(salt) != SALT_SIZE:
        raise ValueError(f"Invalid salt size: {len(salt)}, expected {SALT_SIZE}")

    if iterations < 10000:
        logger.warning(f"Low iteration count: {iterations}, recommended >= 100000")

    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=KEY_SIZE,
        salt=salt,
        iterations=iterations,
        backend=default_backend()
    )

    master_key = kdf.derive(password.encode('utf-8'))

    logger.debug(f"Derived master key with {iterations} iterations")
    return master_key


def encrypt_data(
    plaintext: bytes,
    key: bytes,
    iv: Optional[bytes] = None,
    associated_data: Optional[bytes] = None
) -> Tuple[bytes, bytes]:
    """
    使用 AES-256-GCM 加密数据

    Args:
        plaintext: 明文数据
        key: 加密密钥（32 bytes）
        iv: 初始化向量（12 bytes），如果为 None 则自动生成
        associated_data: 附加认证数据（AAD），可选

    Returns:
        (加密后的数据, IV)

    Raises:
        ValueError: 如果参数无效
    """
    if len(key) != KEY_SIZE:
        raise ValueError(f"Invalid key size: {len(key)}, expected {KEY_SIZE}")

    # 生成或验证 IV
    if iv is None:
        iv = generate_iv()
    elif len(iv) != IV_SIZE:
        raise ValueError(f"Invalid IV size: {len(iv)}, expected {IV_SIZE}")

    # 创建加密器
    aesgcm = AESGCM(key)

    # 加密数据
    ciphertext = aesgcm.encrypt(iv, plaintext, associated_data)

    logger.debug(f"Encrypted {len(plaintext)} bytes to {len(ciphertext)} bytes")
    return ciphertext, iv


def decrypt_data(
    ciphertext: bytes,
    key: bytes,
    iv: bytes,
    associated_data: Optional[bytes] = None
) -> bytes:
    """
    使用 AES-256-GCM 解密数据

    Args:
        ciphertext: 密文数据（包含 GCM tag）
        key: 解密密钥（32 bytes）
        iv: 初始化向量（12 bytes）
        associated_data: 附加认证数据（AAD），必须与加密时相同

    Returns:
        解密后的明文数据

    Raises:
        ValueError: 如果参数无效
        cryptography.exceptions.InvalidTag: 如果解密失败（数据被篡改或密码错误）
    """
    if len(key) != KEY_SIZE:
        raise ValueError(f"Invalid key size: {len(key)}, expected {KEY_SIZE}")

    if len(iv) != IV_SIZE:
        raise ValueError(f"Invalid IV size: {len(iv)}, expected {IV_SIZE}")

    # 创建解密器
    aesgcm = AESGCM(key)

    # 解密数据
    try:
        plaintext = aesgcm.decrypt(iv, ciphertext, associated_data)
        logger.debug(f"Decrypted {len(ciphertext)} bytes to {len(plaintext)} bytes")
        return plaintext
    except Exception as e:
        logger.error(f"Decryption failed: {e}")
        raise


def compute_sha256(data: bytes) -> bytes:
    """
    计算 SHA-256 哈希

    Args:
        data: 输入数据

    Returns:
        32 字节的哈希值
    """
    return hashlib.sha256(data).digest()


def compute_file_hash(file_path: str, chunk_size: int = 8192) -> str:
    """
    计算文件的 SHA-256 哈希

    Args:
        file_path: 文件路径
        chunk_size: 每次读取的块大小

    Returns:
        哈希值的十六进制字符串
    """
    sha256 = hashlib.sha256()

    with open(file_path, 'rb') as f:
        while chunk := f.read(chunk_size):
            sha256.update(chunk)

    hash_hex = sha256.hexdigest()
    logger.debug(f"Computed file hash: {file_path} -> {hash_hex[:16]}...")
    return hash_hex


def encode_base64(data: bytes) -> str:
    """
    Base64 编码

    Args:
        data: 二进制数据

    Returns:
        Base64 字符串
    """
    return base64.b64encode(data).decode('ascii')


def decode_base64(data: str) -> bytes:
    """
    Base64 解码

    Args:
        data: Base64 字符串

    Returns:
        二进制数据
    """
    return base64.b64decode(data.encode('ascii'))


def verify_password_strength(password: str) -> Tuple[bool, str]:
    """
    验证密码强度

    Args:
        password: 用户密码

    Returns:
        (是否有效, 错误信息)
    """
    import re

    if len(password) < 8:
        return False, "密码长度至少 8 个字符"

    if len(password) < 12:
        logger.warning("密码长度较短，建议至少 12 个字符")

    # 检查字符类型
    has_lower = bool(re.search(r'[a-z]', password))
    has_upper = bool(re.search(r'[A-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))

    if not has_lower:
        return False, "密码必须包含小写字母"

    if not has_upper:
        return False, "密码必须包含大写字母"

    if not has_digit:
        return False, "密码必须包含数字"

    # 特殊字符可选，但建议包含
    if not has_special:
        logger.warning("密码建议包含特殊字符以提高安全性")

    # 检查常见弱密码
    weak_passwords = [
        'password', '12345678', 'qwerty', 'abc123',
        'password123', 'admin123', '88888888'
    ]
    if password.lower() in weak_passwords:
        return False, "密码过于简单，请使用更强的密码"

    return True, ""


class SecureKeyManager:
    """
    安全的密钥管理器

    管理 Master Key 的生命周期，确保密钥只在内存中，不落盘
    """

    def __init__(self):
        self._master_key: Optional[bytes] = None
        self._salt: Optional[bytes] = None

    def derive_key(self, password: str, salt: bytes, iterations: int = PBKDF2_ITERATIONS) -> None:
        """
        派生并存储 Master Key

        Args:
            password: 用户密码
            salt: 盐值
            iterations: PBKDF2 迭代次数
        """
        self._master_key = derive_master_key(password, salt, iterations)
        self._salt = salt
        logger.info("Master key derived and stored in memory")

    def get_key(self) -> bytes:
        """
        获取 Master Key

        Returns:
            Master Key

        Raises:
            ValueError: 如果密钥未初始化
        """
        if self._master_key is None:
            raise ValueError("Master key not initialized")
        return self._master_key

    def is_initialized(self) -> bool:
        """检查密钥是否已初始化"""
        return self._master_key is not None

    def clear(self) -> None:
        """清除 Master Key"""
        if self._master_key is not None:
            # 覆写内存（尝试防止内存残留）
            # 注意：Python 的垃圾回收机制无法保证完全清除
            self._master_key = bytes(len(self._master_key))
            self._master_key = None
            self._salt = None
            logger.info("Master key cleared from memory")

    def __del__(self):
        """析构时自动清除密钥"""
        self.clear()

    def __enter__(self):
        """支持 with 语句"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """退出 with 语句时清除密钥"""
        self.clear()


# 全局密钥管理器实例（可选）
_global_key_manager: Optional[SecureKeyManager] = None


def get_global_key_manager() -> SecureKeyManager:
    """
    获取全局密钥管理器实例

    Returns:
        SecureKeyManager 实例
    """
    global _global_key_manager
    if _global_key_manager is None:
        _global_key_manager = SecureKeyManager()
    return _global_key_manager


def clear_global_key_manager() -> None:
    """清除全局密钥管理器"""
    global _global_key_manager
    if _global_key_manager is not None:
        _global_key_manager.clear()
        _global_key_manager = None
