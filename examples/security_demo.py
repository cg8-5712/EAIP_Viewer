"""
混合安全方案使用示例
演示如何使用混合安全管理器
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from src.core.hybrid_security import HybridSecurityManager, init_security
from src.utils.logger import setup_logger, logger


def example_basic_usage():
    """示例 1：基本使用"""
    print("\n" + "=" * 60)
    print("示例 1：基本使用")
    print("=" * 60)

    # 1. 初始化安全系统
    # 注意：这个密码应该是打包 .aipkg 时使用的密码
    DISTRIBUTION_PASSWORD = "Aviation2025!ComplexPassword"
    init_security(DISTRIBUTION_PASSWORD, server_url="http://localhost:8000")

    # 2. 获取安全管理器
    manager = HybridSecurityManager()

    # 3. 用户登录
    username = input("请输入用户名: ")
    password = input("请输入密码: ")

    if manager.authenticate(username, password):
        print("✅ 登录成功！")
        print(f"当前用户: {manager.get_current_user()}")
        print(f"在线模式: {manager.is_online_mode}")

        # 4. 获取 Distribution Password（用于解密 AIPKG）
        dist_password = manager.get_distribution_password()
        print(f"Distribution Password 已准备好，可以解密 AIPKG")

        # 5. 登出
        manager.logout()
        print("已登出")

    else:
        print("❌ 登录失败")


def example_offline_mode():
    """示例 2：离线模式测试"""
    print("\n" + "=" * 60)
    print("示例 2：离线模式测试")
    print("=" * 60)

    # 1. 首次在线登录
    print("\n步骤 1：首次在线登录（缓存凭证）")
    DISTRIBUTION_PASSWORD = "Aviation2025!ComplexPassword"
    manager = HybridSecurityManager(offline_cache_days=7)
    manager.set_distribution_password(DISTRIBUTION_PASSWORD)

    username = "testuser"
    password = "TestPassword123!"

    # 模拟在线登录成功
    print("尝试在线登录...")
    success = manager.authenticate(username, password)
    print(f"在线登录: {'成功' if success else '失败'}")

    if not success:
        print("⚠️ 在线登录失败，可能是：")
        print("   1. 服务器未启动")
        print("   2. 用户名密码错误")
        print("   3. 网络连接问题")
        return

    print("\n步骤 2：模拟离线环境")
    # 创建新的管理器实例（模拟应用重启 + 离线）
    manager2 = HybridSecurityManager(server_url="http://offline-test-invalid-url")
    manager2.set_distribution_password(DISTRIBUTION_PASSWORD)

    print("尝试离线登录（使用缓存）...")
    success2 = manager2.authenticate(username, password)

    if success2:
        print("✅ 离线登录成功！")
        print(f"用户信息: {manager2.get_current_user()}")
        print(f"凭证有效期至: {manager2.credential_manager.load_credential(username, password).expires_at}")
    else:
        print("❌ 离线登录失败")


def example_device_fingerprint():
    """示例 3：设备指纹"""
    print("\n" + "=" * 60)
    print("示例 3：设备指纹信息")
    print("=" * 60)

    from src.core.device_fingerprint import get_device_info

    info = get_device_info()

    print("\n设备信息：")
    for key, value in info.items():
        print(f"  {key}: {value}")


def example_credential_management():
    """示例 4：凭证管理"""
    print("\n" + "=" * 60)
    print("示例 4：凭证管理")
    print("=" * 60)

    from src.core.offline_credential import OfflineCredentialManager

    manager = OfflineCredentialManager(cache_days=7)

    # 保存测试凭证
    print("\n保存测试凭证...")
    success = manager.save_credential(
        username="testuser",
        password="TestPassword123!",
        token="dummy_token_12345",
        user_info={"username": "testuser", "email": "test@example.com"}
    )
    print(f"保存: {'成功' if success else '失败'}")

    # 加载凭证
    print("\n加载凭证...")
    credential = manager.load_credential("testuser", "TestPassword123!")

    if credential:
        print("✅ 凭证加载成功")
        print(f"  用户名: {credential.username}")
        print(f"  创建时间: {credential.created_at}")
        print(f"  过期时间: {credential.expires_at}")
    else:
        print("❌ 凭证加载失败")

    # 查看所有缓存
    print("\n所有缓存的凭证文件：")
    cached = manager.get_all_cached_users()
    for cache_file in cached:
        print(f"  - {cache_file.name}")

    # 清理过期凭证
    print("\n清理过期凭证...")
    count = manager.cleanup_expired()
    print(f"清理了 {count} 个过期凭证")

    # 删除测试凭证
    print("\n删除测试凭证...")
    manager.delete_credential("testuser")
    print("已删除")


def main():
    """主函数"""
    setup_logger()

    print("\n" + "=" * 60)
    print("混合安全方案示例程序")
    print("=" * 60)

    while True:
        print("\n请选择示例：")
        print("  1. 基本使用")
        print("  2. 离线模式测试")
        print("  3. 设备指纹信息")
        print("  4. 凭证管理")
        print("  0. 退出")

        choice = input("\n请输入选项: ").strip()

        if choice == "1":
            example_basic_usage()
        elif choice == "2":
            example_offline_mode()
        elif choice == "3":
            example_device_fingerprint()
        elif choice == "4":
            example_credential_management()
        elif choice == "0":
            print("再见！")
            break
        else:
            print("无效选项，请重试")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n程序被用户中断")
    except Exception as e:
        logger.error(f"程序异常: {e}", exc_info=True)
        print(f"\n错误: {e}")
