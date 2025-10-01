"""
EAIP Viewer - 电子航空情报资料查看器
主程序入口
"""

import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from PyQt6.QtWidgets import QApplication
from PyQt6.QtQml import QQmlApplicationEngine
from PyQt6.QtCore import QUrl, Qt
from PyQt6.QtGui import QIcon

from src.config import config
from src.utils.logger import setup_logger, logger


def main():
    """应用主入口"""

    # 初始化日志系统
    setup_logger()
    logger.info("=" * 60)
    logger.info(f"{config.APP_NAME} v{config.APP_VERSION} 启动中...")
    logger.info(f"环境: {config.APP_ENV}")
    logger.info("=" * 60)

    # 创建 Qt 应用
    app = QApplication(sys.argv)
    app.setApplicationName(config.APP_NAME)
    app.setApplicationVersion(config.APP_VERSION)
    app.setOrganizationName("EAIP Viewer Team")
    app.setOrganizationDomain("github.com/cg8-5712")

    # 设置应用图标（如果存在）
    icon_path = Path(__file__).parent.parent / "resources" / "icons" / "app.ico"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    # 启用高 DPI 缩放
    if hasattr(Qt, 'AA_EnableHighDpiScaling'):
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    if hasattr(Qt, 'AA_UseHighDpiPixmaps'):
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)

    # 创建 QML 引擎
    engine = QQmlApplicationEngine()

    # 连接 QML 警告和错误信号
    def on_qml_warnings(warnings):
        for warning in warnings:
            logger.warning(f"QML 警告: {warning.toString()}")

    engine.warnings.connect(on_qml_warnings)

    # QML 调试模式
    if config.QML_DEBUG:
        logger.info("QML 调试模式已启用")

    # 添加 QML 导入路径
    qml_dir = Path(__file__).parent / "qml"
    engine.addImportPath(str(qml_dir))
    logger.info(f"添加 QML 导入路径: {qml_dir}")

    # 注册 QML 类型和单例
    # TODO: 注册自定义 QML 类型
    # from src.controllers.auth_controller import AuthController
    # qmlRegisterType(AuthController, "EAIP", 1, 0, "AuthController")

    # 设置 QML 上下文属性
    engine.rootContext().setContextProperty("appVersion", config.APP_VERSION)
    engine.rootContext().setContextProperty("isDevelopment", config.is_development())

    # 加载主 QML 文件
    qml_file = Path(__file__).parent / "qml" / "main.qml"
    logger.info(f"加载 QML 文件: {qml_file}")
    engine.load(QUrl.fromLocalFile(str(qml_file)))

    # 检查 QML 加载是否成功
    if not engine.rootObjects():
        logger.error("QML 文件加载失败！请检查上面的 QML 警告信息")
        return -1

    logger.info(f"{config.APP_NAME} 启动成功！")

    # 运行应用事件循环
    exit_code = app.exec()

    logger.info(f"{config.APP_NAME} 已退出，退出码: {exit_code}")
    return exit_code


if __name__ == "__main__":
    sys.exit(main())
