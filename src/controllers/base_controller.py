"""
基础控制器类
所有 QML 控制器的基类
"""

from PyQt6.QtCore import QObject, pyqtSignal, pyqtSlot
from src.utils.logger import logger


class BaseController(QObject):
    """
    控制器基类

    提供通用的错误处理和信号机制
    """

    # 通用信号
    errorOccurred = pyqtSignal(str)  # 错误信号
    successMessage = pyqtSignal(str)  # 成功消息信号
    loadingChanged = pyqtSignal(bool)  # 加载状态变化

    def __init__(self, parent=None):
        super().__init__(parent)
        self._is_loading = False

    def emit_error(self, message: str):
        """发射错误信号"""
        logger.error(f"{self.__class__.__name__}: {message}")
        self.errorOccurred.emit(message)

    def emit_success(self, message: str):
        """发射成功消息信号"""
        logger.info(f"{self.__class__.__name__}: {message}")
        self.successMessage.emit(message)

    def set_loading(self, loading: bool):
        """设置加载状态"""
        if self._is_loading != loading:
            self._is_loading = loading
            self.loadingChanged.emit(loading)

    @property
    def is_loading(self) -> bool:
        """获取加载状态"""
        return self._is_loading
