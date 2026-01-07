"""应用控制器"""
import sys
from PySide6.QtWidgets import QApplication
from PySide6.QtCore import QTimer
from PySide6.QtGui import QIcon, QPixmap, QPainter, QColor

from src.ui.main_window import MainWindow
from src.ui.popup_panel import PopupPanel
from src.core.hotkey import HotkeyManager
from src.core.output import output_text
from src.core.config import load_config, save_config


def create_default_icon() -> QIcon:
    """创建默认图标"""
    pixmap = QPixmap(32, 32)
    pixmap.fill(QColor(0, 0, 0, 0))

    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.setBrush(QColor("#1a73e8"))
    painter.setPen(QColor("#1a73e8"))
    painter.drawEllipse(2, 2, 28, 28)

    painter.setPen(QColor("#ffffff"))
    font = painter.font()
    font.setPixelSize(18)
    font.setBold(True)
    painter.setFont(font)
    painter.drawText(pixmap.rect(), 0x84, "X")  # AlignCenter
    painter.end()

    return QIcon(pixmap)


class App:
    """应用程序"""

    def __init__(self):
        self._app = QApplication(sys.argv)
        self._app.setQuitOnLastWindowClosed(False)

        self._config = load_config()

        self._main_window = MainWindow()
        self._popup = PopupPanel()
        self._hotkey = HotkeyManager()

        self._setup_connections()
        self._setup_icon()
        self._apply_config()

    def _setup_connections(self):
        """设置信号连接"""
        self._main_window.start_requested.connect(self._start)
        self._main_window.stop_requested.connect(self._stop)
        self._main_window.hotkey_changed.connect(self._on_hotkey_changed)
        self._hotkey.triggered.connect(self._on_hotkey)
        self._popup.output_selected.connect(self._on_output)

    def _setup_icon(self):
        """设置图标"""
        icon = create_default_icon()
        self._main_window.set_icon(icon)

    def _apply_config(self):
        """应用配置"""
        hotkey = self._config.get("hotkey", {})
        self._hotkey.set_hotkey(
            hotkey.get("modifiers", ["ctrl"]),
            hotkey.get("key", "space")
        )
        self._main_window.set_hotkey(hotkey)

    def _on_hotkey_changed(self, hotkey: dict):
        """快捷键变更"""
        self._config["hotkey"] = hotkey
        save_config(self._config)
        self._hotkey.set_hotkey(
            hotkey.get("modifiers", ["ctrl"]),
            hotkey.get("key", "space")
        )

    def _start(self):
        """启动服务"""
        self._hotkey.start()
        self._main_window.set_running(True)

    def _stop(self):
        """停止服务"""
        self._hotkey.stop()
        self._main_window.set_running(False)

    def _on_hotkey(self):
        """热键触发"""
        # 使用QTimer延迟显示，避免和热键冲突
        QTimer.singleShot(50, self._popup.show_at_cursor)

    def _on_output(self, text: str, offset: int):
        """输出文本"""
        # 延迟输出，确保面板已隐藏
        QTimer.singleShot(100, lambda: output_text(text, offset))

    def run(self) -> int:
        """运行应用"""
        self._main_window.show()
        return self._app.exec()
