"""
混合安全管理器
集成在线认证和离线缓存，提供统一的认证接口
"""

from typing import Optional, Dict, Any
from datetime import datetime

from src.core.auth_client import SyncAuthClient, AuthenticationError, NetworkError
from src.core.offline_credential import OfflineCredentialManager, OfflineCredential
from src.core.device_fingerprint import get_device_fingerprint, get_device_info
from src.core.encryption_utils import SecureKeyManager
from src.utils.logger import logger


class HybridSecurityManager:
    """
    混合安全管理器

    提供在线/离线自适应认证：
    - 优先在线验证
    - 网络不可用时降级到离线模式
    - 离线凭证有效期：7天
    """

    # 硬编码的 Distribution Password（从打包时的密码）
    # 注意：这个应该通过代码混淆或其他方式保护
    # TODO: 改为你在打包时使用的密码
    _DISTRIBUTION_PASSWORD = "Aviation2025!ComplexServerPassword"

    def __init__(
        self,
        server_url: Optional[str] = None,
        offline_cache_days: int = 7
    ):
        """
        初始化

        Args:
            server_url: 认证服务器 URL
            offline_cache_days: 离线缓存有效期（天）
        """
        self.auth_client = SyncAuthClient(server_url)
        self.credential_manager = OfflineCredentialManager(offline_cache_days)
        self.key_manager = SecureKeyManager()

        self.current_user: Optional[Dict[str, Any]] = None
        self.current_token: Optional[str] = None
        self.is_online_mode: bool = False

    def authenticate(self, username: str, password: str) -> bool:
        """
        用户认证（在线/离线自适应）

        Args:
            username: 用户名
            password: 密码

        Returns:
            是否认证成功
        """
        # 1. 检查网络连接
        if self.auth_client.check_network():
            # 在线模式
            return self._online_authenticate(username, password)
        else:
            # 离线模式
            logger.info("Network unavailable, switching to offline mode")
            return self._offline_authenticate(username, password)

    def _online_authenticate(self, username: str, password: str) -> bool:
        """在线认证"""
        try:
            # 获取设备指纹
            device_fp = get_device_fingerprint()

            # 调用认证 API
            response = self.auth_client.login(username, password, device_fp)

            if response.get('success'):
                # 保存认证信息
                self.current_token = response.get('token')
                self.current_user = response.get('user')
                self.is_online_mode = True

                # 缓存凭证（用于离线使用）
                self.credential_manager.save_credential(
                    username=username,
                    password=password,
                    token=self.current_token,
                    user_info=self.current_user
                )

                # 派生 Distribution Key
                self._derive_distribution_key(self.current_token)

                logger.info(f"Online authentication successful: {username}")
                return True

        except AuthenticationError as e:
            logger.error(f"Authentication failed: {e}")
            return False

        except NetworkError as e:
            # 网络错误，降级到离线模式
            logger.warning(f"Network error, falling back to offline mode: {e}")
            return self._offline_authenticate(username, password)

        return False

    def _offline_authenticate(self, username: str, password: str) -> bool:
        """离线认证（使用缓存）"""
        try:
            # 加载缓存凭证
            credential = self.credential_manager.load_credential(username, password)

            if not credential:
                logger.error("No cached credential found, online authentication required")
                return False

            # 验证凭证是否过期
            expires_at = datetime.fromisoformat(credential.expires_at)
            if datetime.now() > expires_at:
                logger.error("Cached credential expired, online authentication required")
                return False

            # 认证成功
            self.current_token = credential.token
            self.current_user = credential.user_info
            self.is_online_mode = False

            # 派生 Distribution Key
            self._derive_distribution_key(credential.token)

            logger.info(f"Offline authentication successful: {username}")
            logger.info(f"Credential expires at: {credential.expires_at}")

            return True

        except Exception as e:
            logger.error(f"Offline authentication failed: {e}", exc_info=True)
            return False

    def _derive_distribution_key(self, user_token: str) -> None:
        """
        派生 Distribution Key

        使用用户令牌解密内置的 Distribution Password
        """
        # 在实际应用中，Distribution Password 应该加密存储
        # 这里简化处理，直接使用
        dist_password = self._DISTRIBUTION_PASSWORD

        # 派生密钥（用于解密 AIPKG）
        # 注意：这里应该使用一个固定的 salt（打包时的 salt）
        # 暂时使用 Distribution Password 本身
        import hashlib
        salt = hashlib.sha256(dist_password.encode('utf-8')).digest()

        from src.core.encryption_utils import derive_master_key
        self.key_manager.derive_key(dist_password, salt)

        logger.debug("Distribution key derived")

    def get_distribution_password(self) -> str:
        """
        获取 Distribution Password

        只有认证成功后才能获取

        Returns:
            Distribution Password

        Raises:
            ValueError: 如果未认证
        """
        if not self.is_authenticated():
            raise ValueError("Not authenticated")

        return self._DISTRIBUTION_PASSWORD

    def is_authenticated(self) -> bool:
        """检查是否已认证"""
        return self.current_user is not None

    def logout(self) -> None:
        """用户登出"""
        if self.is_online_mode and self.current_token:
            try:
                self.auth_client.logout(self.current_token)
            except Exception as e:
                logger.warning(f"Logout API call failed: {e}")

        # 清除内存中的数据
        self.current_user = None
        self.current_token = None
        self.key_manager.clear()

        logger.info("User logged out")

    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """获取当前用户信息"""
        return self.current_user

    def get_device_info(self) -> Dict[str, Any]:
        """获取设备信息（用于调试）"""
        return get_device_info()

    @classmethod
    def set_distribution_password(cls, password: str) -> None:
        """
        设置 Distribution Password

        在应用初始化时调用（从配置或加密存储读取）

        Args:
            password: Distribution Password
        """
        cls._DISTRIBUTION_PASSWORD = password
        logger.info("Distribution password configured")


# 全局单例（可选）
_global_security_manager: Optional[HybridSecurityManager] = None


def get_security_manager() -> HybridSecurityManager:
    """
    获取全局安全管理器实例

    Returns:
        HybridSecurityManager 实例
    """
    global _global_security_manager
    if _global_security_manager is None:
        _global_security_manager = HybridSecurityManager()
    return _global_security_manager


def init_security(distribution_password: str, server_url: Optional[str] = None) -> None:
    """
    初始化安全系统

    Args:
        distribution_password: Distribution Password（打包时的密码）
        server_url: 认证服务器 URL
    """
    HybridSecurityManager.set_distribution_password(distribution_password)

    global _global_security_manager
    _global_security_manager = HybridSecurityManager(server_url)

    logger.info("Security system initialized")
