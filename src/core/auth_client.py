"""
在线认证客户端
与服务器通信，验证用户身份
"""

import aiohttp
import asyncio
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from src.utils.logger import logger
from src.config import config


class AuthenticationError(Exception):
    """认证错误"""
    pass


class NetworkError(Exception):
    """网络错误"""
    pass


class AuthClient:
    """认证客户端"""

    def __init__(self, server_url: Optional[str] = None):
        """
        初始化认证客户端

        Args:
            server_url: 服务器 URL，如果为 None 则使用配置文件中的 URL
        """
        self.server_url = server_url or config.UPDATE_SERVER_URL or "http://localhost:8000"
        self.timeout = aiohttp.ClientTimeout(total=10)  # 10秒超时

    async def check_network(self) -> bool:
        """
        检查网络连接

        Returns:
            是否可以连接到服务器
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(f"{self.server_url}/api/health") as response:
                    return response.status == 200
        except Exception as e:
            logger.debug(f"Network check failed: {e}")
            return False

    async def login(
        self,
        username: str,
        password: str,
        device_fingerprint: str
    ) -> Dict[str, Any]:
        """
        用户登录

        Args:
            username: 用户名
            password: 密码
            device_fingerprint: 设备指纹

        Returns:
            登录响应（包含 token）

        Raises:
            AuthenticationError: 认证失败
            NetworkError: 网络错误
        """
        try:
            payload = {
                'username': username,
                'password': password,
                'device_fingerprint': device_fingerprint,
                'app_version': config.APP_VERSION
            }

            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.post(
                    f"{self.server_url}/api/auth/login",
                    json=payload
                ) as response:
                    data = await response.json()

                    if response.status == 200 and data.get('success'):
                        logger.info(f"Login successful: {username}")
                        return data

                    elif response.status == 401:
                        error_msg = data.get('error', '用户名或密码错误')
                        raise AuthenticationError(error_msg)

                    elif response.status == 403:
                        error_msg = data.get('error', '无访问权限')
                        raise AuthenticationError(error_msg)

                    else:
                        error_msg = data.get('error', '登录失败')
                        raise AuthenticationError(error_msg)

        except aiohttp.ClientError as e:
            logger.error(f"Network error during login: {e}")
            raise NetworkError(f"网络连接失败: {e}")

        except asyncio.TimeoutError:
            logger.error("Login request timeout")
            raise NetworkError("请求超时，请检查网络连接")

    async def verify_token(self, token: str) -> bool:
        """
        验证 Token 有效性

        Args:
            token: JWT Token

        Returns:
            Token 是否有效
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                headers = {'Authorization': f'Bearer {token}'}

                async with session.get(
                    f"{self.server_url}/api/auth/verify",
                    headers=headers
                ) as response:
                    data = await response.json()
                    return response.status == 200 and data.get('valid', False)

        except Exception as e:
            logger.error(f"Token verification failed: {e}")
            return False

    async def logout(self, token: str) -> bool:
        """
        用户登出

        Args:
            token: JWT Token

        Returns:
            是否成功
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                headers = {'Authorization': f'Bearer {token}'}

                async with session.post(
                    f"{self.server_url}/api/auth/logout",
                    headers=headers
                ) as response:
                    return response.status == 200

        except Exception as e:
            logger.error(f"Logout failed: {e}")
            return False

    async def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """
        获取用户信息

        Args:
            token: JWT Token

        Returns:
            用户信息字典，失败返回 None
        """
        try:
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                headers = {'Authorization': f'Bearer {token}'}

                async with session.get(
                    f"{self.server_url}/api/user/info",
                    headers=headers
                ) as response:
                    if response.status == 200:
                        return await response.json()
                    return None

        except Exception as e:
            logger.error(f"Failed to get user info: {e}")
            return None


# 同步包装器（用于非异步环境）
class SyncAuthClient:
    """同步认证客户端（包装异步客户端）"""

    def __init__(self, server_url: Optional[str] = None):
        self.client = AuthClient(server_url)
        self.loop = None

    def _run_async(self, coro):
        """运行异步函数"""
        if self.loop is None:
            self.loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self.loop)

        return self.loop.run_until_complete(coro)

    def check_network(self) -> bool:
        """检查网络连接（同步）"""
        try:
            return self._run_async(self.client.check_network())
        except Exception:
            return False

    def login(self, username: str, password: str, device_fingerprint: str) -> Dict[str, Any]:
        """用户登录（同步）"""
        return self._run_async(self.client.login(username, password, device_fingerprint))

    def verify_token(self, token: str) -> bool:
        """验证 Token（同步）"""
        return self._run_async(self.client.verify_token(token))

    def logout(self, token: str) -> bool:
        """用户登出（同步）"""
        return self._run_async(self.client.logout(token))

    def get_user_info(self, token: str) -> Optional[Dict[str, Any]]:
        """获取用户信息（同步）"""
        return self._run_async(self.client.get_user_info(token))

    def __del__(self):
        """清理事件循环"""
        if self.loop is not None:
            try:
                self.loop.close()
            except Exception:
                pass
