"""
设备指纹工具
生成唯一的设备标识符，用于设备绑定
"""

import hashlib
import platform
import uuid
from typing import Optional

from src.utils.logger import logger


def get_machine_id() -> str:
    """
    获取机器唯一标识

    Returns:
        机器 ID（UUID 格式字符串）
    """
    try:
        # 尝试获取机器 UUID（跨平台）
        machine_uuid = uuid.UUID(int=uuid.getnode())
        return str(machine_uuid)
    except Exception as e:
        logger.warning(f"Failed to get machine UUID: {e}")
        # 降级方案：使用主机名
        return platform.node()


def get_device_fingerprint() -> str:
    """
    生成设备指纹

    组合多个设备特征生成唯一指纹：
    - 机器 ID（MAC 地址派生）
    - 操作系统信息
    - CPU 信息

    Returns:
        设备指纹（SHA256 哈希）
    """
    components = []

    # 1. 机器 ID
    try:
        machine_id = get_machine_id()
        components.append(machine_id)
    except Exception as e:
        logger.warning(f"Failed to get machine ID: {e}")

    # 2. 操作系统信息
    try:
        os_info = f"{platform.system()}-{platform.release()}-{platform.version()}"
        components.append(os_info)
    except Exception as e:
        logger.warning(f"Failed to get OS info: {e}")

    # 3. CPU 信息
    try:
        cpu_info = platform.processor()
        components.append(cpu_info)
    except Exception as e:
        logger.warning(f"Failed to get CPU info: {e}")

    # 4. 主机名
    try:
        hostname = platform.node()
        components.append(hostname)
    except Exception as e:
        logger.warning(f"Failed to get hostname: {e}")

    # 组合并生成哈希
    fingerprint_data = "|".join(components)
    fingerprint = hashlib.sha256(fingerprint_data.encode('utf-8')).hexdigest()

    logger.debug(f"Generated device fingerprint: {fingerprint[:16]}...")
    return fingerprint


def verify_device_fingerprint(stored_fingerprint: str) -> bool:
    """
    验证设备指纹是否匹配

    Args:
        stored_fingerprint: 存储的设备指纹

    Returns:
        是否匹配
    """
    current_fingerprint = get_device_fingerprint()
    match = current_fingerprint == stored_fingerprint

    if not match:
        logger.warning("Device fingerprint mismatch!")
        logger.debug(f"Stored: {stored_fingerprint[:16]}...")
        logger.debug(f"Current: {current_fingerprint[:16]}...")

    return match


def get_device_info() -> dict:
    """
    获取设备详细信息（用于调试和审计）

    Returns:
        设备信息字典
    """
    return {
        'fingerprint': get_device_fingerprint(),
        'machine_id': get_machine_id(),
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'hostname': platform.node(),
        'python_version': platform.python_version()
    }
