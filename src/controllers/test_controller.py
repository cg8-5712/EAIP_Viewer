"""
测试控制器
用于测试 QML 与 Python 的桥接
"""

from PyQt6.QtCore import pyqtSignal, pyqtSlot, pyqtProperty
from src.controllers.base_controller import BaseController
from src.utils.logger import logger


class TestController(BaseController):
    """测试控制器"""

    # 自定义信号
    messageChanged = pyqtSignal(str)
    counterChanged = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._message = "Hello from Python!"
        self._counter = 0

    # ==================== 属性 ====================

    @pyqtProperty(str, notify=messageChanged)
    def message(self):
        """消息属性（QML 可读）"""
        return self._message

    @message.setter
    def message(self, value):
        """设置消息"""
        if self._message != value:
            self._message = value
            self.messageChanged.emit(value)

    @pyqtProperty(int, notify=counterChanged)
    def counter(self):
        """计数器属性（QML 可读）"""
        return self._counter

    # ==================== 槽函数（QML 可调用）====================

    @pyqtSlot()
    def incrementCounter(self):
        """增加计数器"""
        self._counter += 1
        self.counterChanged.emit(self._counter)
        logger.info(f"计数器增加到: {self._counter}")

    @pyqtSlot()
    def resetCounter(self):
        """重置计数器"""
        self._counter = 0
        self.counterChanged.emit(self._counter)
        logger.info("计数器已重置")

    @pyqtSlot(str, result=str)
    def echo(self, text: str) -> str:
        """回显文本（测试参数和返回值）"""
        result = f"Python 收到: {text}"
        logger.info(result)
        return result

    @pyqtSlot()
    def testError(self):
        """测试错误信号"""
        self.emit_error("这是一个测试错误信息")

    @pyqtSlot()
    def testSuccess(self):
        """测试成功信号"""
        self.emit_success("操作成功！")

    @pyqtSlot()
    def testLoading(self):
        """测试加载状态"""
        self.set_loading(True)
        logger.info("加载状态设置为 True")

        # 模拟异步操作
        from PyQt6.QtCore import QTimer
        QTimer.singleShot(2000, lambda: self.set_loading(False))
