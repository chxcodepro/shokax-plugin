"""主窗口"""
from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QSystemTrayIcon,
    QMenu,
    QKeySequenceEdit,
)
from PySide6.QtCore import Signal, Qt
from PySide6.QtGui import QIcon, QAction, QKeySequence

from src.ui.styles import MAIN_WINDOW_STYLE


def parse_key_sequence(seq: QKeySequence) -> dict | None:
    """解析 QKeySequence 为热键配置"""
    if seq.isEmpty():
        return None

    key_str = seq.toString()
    if not key_str:
        return None

    parts = key_str.split("+")
    modifiers = []
    key = None

    for part in parts:
        part_lower = part.lower().strip()
        if part_lower in ("ctrl", "control"):
            modifiers.append("ctrl")
        elif part_lower in ("alt",):
            modifiers.append("alt")
        elif part_lower in ("shift",):
            modifiers.append("shift")
        elif part_lower == "space":
            key = "space"
        elif part_lower == "`":
            key = "grave"
        elif part_lower == "tab":
            key = "tab"
        elif len(part) == 1:
            key = part.lower()
        else:
            key = part_lower

    if not modifiers or not key:
        return None

    return {"modifiers": modifiers, "key": key}


def hotkey_to_display(hotkey: dict) -> str:
    """热键配置转显示文本"""
    parts = [m.capitalize() for m in hotkey.get("modifiers", [])]
    key = hotkey.get("key", "")
    key_map = {"space": "空格", "grave": "`", "tab": "Tab"}
    parts.append(key_map.get(key, key.upper()))
    return "+".join(parts)


def hotkey_to_sequence(hotkey: dict) -> QKeySequence:
    """热键配置转 QKeySequence"""
    parts = []
    for m in hotkey.get("modifiers", []):
        if m == "ctrl":
            parts.append("Ctrl")
        elif m == "alt":
            parts.append("Alt")
        elif m == "shift":
            parts.append("Shift")

    key = hotkey.get("key", "")
    key_map = {"space": "Space", "grave": "`", "tab": "Tab"}
    parts.append(key_map.get(key, key.upper()))

    return QKeySequence("+".join(parts))


class MainWindow(QMainWindow):
    """主窗口"""

    start_requested = Signal()
    stop_requested = Signal()
    hotkey_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._current_hotkey: dict = {"modifiers": ["ctrl"], "key": "space"}
        self._init_ui()
        self._init_tray()

    def _init_ui(self):
        self.setWindowTitle("shokaX plugin")
        self.setFixedSize(280, 200)
        self.setStyleSheet(MAIN_WINDOW_STYLE)

        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)

        central = QWidget()
        self.setCentralWidget(central)

        layout = QVBoxLayout(central)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # 标题
        title = QLabel("shokaX plugin")
        title.setObjectName("title")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)

        # 快捷键设置
        hotkey_layout = QHBoxLayout()
        hotkey_layout.setSpacing(8)

        hotkey_label = QLabel("快捷键:")
        hotkey_label.setObjectName("status")
        hotkey_layout.addWidget(hotkey_label)

        self._hotkey_edit = QKeySequenceEdit()
        self._hotkey_edit.setFixedWidth(150)
        self._hotkey_edit.editingFinished.connect(self._on_hotkey_edit_finished)
        hotkey_layout.addWidget(self._hotkey_edit)

        hotkey_layout.addStretch()
        layout.addLayout(hotkey_layout)

        # 状态
        self._status_label = QLabel("状态: 已停止")
        self._status_label.setObjectName("status")
        self._status_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self._status_label)

        # 按钮
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._toggle_btn = QPushButton("启动")
        self._toggle_btn.setFixedWidth(100)
        self._toggle_btn.clicked.connect(self._on_toggle)
        btn_layout.addWidget(self._toggle_btn)

        btn_layout.addStretch()
        layout.addLayout(btn_layout)

        layout.addStretch()

    def _init_tray(self):
        """初始化系统托盘"""
        self._tray = QSystemTrayIcon(self)

        menu = QMenu()

        self._tray_toggle_action = QAction("启动", self)
        self._tray_toggle_action.triggered.connect(self._on_toggle)
        menu.addAction(self._tray_toggle_action)

        menu.addSeparator()

        show_action = QAction("显示窗口", self)
        show_action.triggered.connect(self._show_window)
        menu.addAction(show_action)

        quit_action = QAction("退出", self)
        quit_action.triggered.connect(self._on_quit)
        menu.addAction(quit_action)

        self._tray.setContextMenu(menu)
        self._tray.activated.connect(self._on_tray_activated)
        self._tray.show()

    def set_icon(self, icon: QIcon):
        """设置图标"""
        self.setWindowIcon(icon)
        self._tray.setIcon(icon)

    def _on_toggle(self):
        """切换启动/停止状态"""
        if self._is_running:
            self.stop_requested.emit()
        else:
            self.start_requested.emit()

    def _on_hotkey_edit_finished(self):
        """快捷键编辑完成"""
        seq = self._hotkey_edit.keySequence()
        hotkey = parse_key_sequence(seq)

        if hotkey:
            self._current_hotkey = hotkey
            self.hotkey_changed.emit(hotkey)
            self._update_status_text()
        else:
            # 无效输入，恢复原值
            self._hotkey_edit.setKeySequence(hotkey_to_sequence(self._current_hotkey))

    def set_hotkey(self, hotkey: dict):
        """设置当前快捷键"""
        self._current_hotkey = hotkey
        self._hotkey_edit.setKeySequence(hotkey_to_sequence(hotkey))

    def _update_status_text(self):
        """更新状态文本"""
        display = hotkey_to_display(self._current_hotkey)
        if self._is_running:
            self._status_label.setText(f"状态: 运行中 ({display})")
        else:
            self._status_label.setText("状态: 已停止")

    def set_running(self, running: bool):
        """设置运行状态"""
        self._is_running = running
        if running:
            self._toggle_btn.setText("停止")
            self._toggle_btn.setObjectName("stop_btn")
            self._tray_toggle_action.setText("停止")
            self._tray.setToolTip("shokaX plugin - 运行中")
            self._hotkey_edit.setEnabled(False)
        else:
            self._toggle_btn.setText("启动")
            self._toggle_btn.setObjectName("")
            self._tray_toggle_action.setText("启动")
            self._tray.setToolTip("shokaX plugin - 已停止")
            self._hotkey_edit.setEnabled(True)

        self._update_status_text()
        self._toggle_btn.setStyleSheet(MAIN_WINDOW_STYLE)

    def _on_tray_activated(self, reason):
        """托盘图标激活"""
        if reason == QSystemTrayIcon.DoubleClick:
            self._show_window()

    def _show_window(self):
        """显示窗口"""
        self.show()
        self.activateWindow()
        self.raise_()

    def _on_quit(self):
        """退出程序"""
        from PySide6.QtWidgets import QApplication
        QApplication.quit()

    def closeEvent(self, event):
        """关闭窗口时最小化到托盘"""
        event.ignore()
        self.hide()
        self._tray.showMessage(
            "shokaX plugin",
            "程序已最小化到托盘，双击图标可打开",
            QSystemTrayIcon.Information,
            2000,
        )
