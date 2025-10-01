"""
离线凭证缓存管理
安全存储用户凭证，支持离线使用
"""

import json
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict

from src.core.encryption_utils import encrypt_data, decrypt_data, derive_master_key, generate_salt
from src.core.device_fingerprint import get_device_fingerprint
from src.config import config
from src.utils.logger import logger


@dataclass
class OfflineCredential:
    """离线凭证"""
    username: str
    password_hash: str  # 密码哈希（不存储明文）
    token: str  # JWT token
    device_fingerprint: str
    created_at: str  # ISO format
    expires_at: str  # ISO format
    user_info: Dict[str, Any]  # 用户信息


class OfflineCredentialManager:
    """离线凭证管理器"""

    def __init__(self, cache_days: int = 7):
        """
        初始化

        Args:
            cache_days: 缓存有效期（天）
        """
        self.cache_days = cache_days
        self.cache_dir = config.DATA_DIR / "credentials"
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def _get_cache_path(self, username: str) -> Path:
        """获取缓存文件路径"""
        # 使用用户名哈希作为文件名（隐私保护）
        username_hash = hashlib.sha256(username.encode('utf-8')).hexdigest()[:16]
        return self.cache_dir / f"{username_hash}.credential"

    def _derive_encryption_key(self, password: str) -> bytes:
        """
        派生加密密钥

        使用密码 + 设备指纹派生，确保只有本设备可以解密
        """
        device_fp = get_device_fingerprint()
        salt = (password + device_fp).encode('utf-8')
        # 使用较少的迭代次数（因为已经有密码验证）
        key = derive_master_key(password, hashlib.sha256(salt).digest(), iterations=10000)
        return key

    def save_credential(
        self,
        username: str,
        password: str,
        token: str,
        user_info: Dict[str, Any]
    ) -> bool:
        """
        保存离线凭证

        Args:
            username: 用户名
            password: 密码（明文，仅用于派生加密密钥）
            token: JWT token
            user_info: 用户信息

        Returns:
            是否成功
        """
        try:
            # 创建凭证对象
            credential = OfflineCredential(
                username=username,
                password_hash=hashlib.sha256(password.encode('utf-8')).hexdigest(),
                token=token,
                device_fingerprint=get_device_fingerprint(),
                created_at=datetime.now().isoformat(),
                expires_at=(datetime.now() + timedelta(days=self.cache_days)).isoformat(),
                user_info=user_info
            )

            # 序列化
            credential_json = json.dumps(asdict(credential), ensure_ascii=False)

            # 加密
            key = self._derive_encryption_key(password)
            encrypted_data, iv = encrypt_data(
                credential_json.encode('utf-8'),
                key,
                associated_data=username.encode('utf-8')
            )

            # 保存到文件
            cache_path = self._get_cache_path(username)
            with open(cache_path, 'wb') as f:
                # 写入 IV（12 bytes）
                f.write(iv)
                # 写入加密数据
                f.write(encrypted_data)

            logger.info(f"Offline credential cached for user: {username}")
            return True

        except Exception as e:
            logger.error(f"Failed to save offline credential: {e}", exc_info=True)
            return False

    def load_credential(self, username: str, password: str) -> Optional[OfflineCredential]:
        """
        加载离线凭证

        Args:
            username: 用户名
            password: 密码（用于验证和解密）

        Returns:
            凭证对象，失败返回 None
        """
        try:
            cache_path = self._get_cache_path(username)

            if not cache_path.exists():
                logger.debug(f"No cached credential found for: {username}")
                return None

            # 读取文件
            with open(cache_path, 'rb') as f:
                iv = f.read(12)  # 读取 IV
                encrypted_data = f.read()  # 读取加密数据

            # 解密
            key = self._derive_encryption_key(password)
            decrypted_data = decrypt_data(
                encrypted_data,
                key,
                iv,
                associated_data=username.encode('utf-8')
            )

            # 解析
            credential_dict = json.loads(decrypted_data.decode('utf-8'))
            credential = OfflineCredential(**credential_dict)

            # 验证密码哈希
            password_hash = hashlib.sha256(password.encode('utf-8')).hexdigest()
            if credential.password_hash != password_hash:
                logger.warning(f"Password mismatch for cached credential: {username}")
                return None

            # 验证设备指纹
            if credential.device_fingerprint != get_device_fingerprint():
                logger.warning(f"Device fingerprint mismatch for: {username}")
                return None

            # 检查是否过期
            expires_at = datetime.fromisoformat(credential.expires_at)
            if datetime.now() > expires_at:
                logger.info(f"Cached credential expired for: {username}")
                self.delete_credential(username)
                return None

            logger.info(f"Loaded offline credential for: {username}")
            return credential

        except Exception as e:
            logger.error(f"Failed to load offline credential: {e}", exc_info=True)
            return None

    def delete_credential(self, username: str) -> bool:
        """
        删除缓存凭证

        Args:
            username: 用户名

        Returns:
            是否成功
        """
        try:
            cache_path = self._get_cache_path(username)
            if cache_path.exists():
                cache_path.unlink()
                logger.info(f"Deleted cached credential for: {username}")
                return True
            return False

        except Exception as e:
            logger.error(f"Failed to delete credential: {e}")
            return False

    def cleanup_expired(self) -> int:
        """
        清理所有过期的凭证

        Returns:
            清理的数量
        """
        count = 0

        try:
            for cache_file in self.cache_dir.glob("*.credential"):
                # 检查文件修改时间
                mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
                if datetime.now() - mtime > timedelta(days=self.cache_days):
                    cache_file.unlink()
                    count += 1
                    logger.debug(f"Deleted expired credential: {cache_file.name}")

            if count > 0:
                logger.info(f"Cleaned up {count} expired credentials")

        except Exception as e:
            logger.error(f"Failed to cleanup credentials: {e}")

        return count

    def get_all_cached_users(self) -> list:
        """
        获取所有缓存的用户（用于调试）

        Returns:
            缓存文件列表
        """
        return list(self.cache_dir.glob("*.credential"))
