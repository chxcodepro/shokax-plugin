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
    QMessageBox,
    QProgressDialog,
)
from PySide6.QtCore import Signal, Qt, QThread
from PySide6.QtGui import QIcon, QAction, QKeySequence

from src.ui.styles import MAIN_WINDOW_STYLE
from src.core.version import __version__
from src.core.updater import UpdateChecker


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


class UpdateCheckThread(QThread):
    """更新检查线程"""

    update_found = Signal(dict)
    no_update = Signal()

    def run(self):
        update_info = UpdateChecker.check_update()
        if update_info:
            self.update_found.emit(update_info)
        else:
            self.no_update.emit()


class MainWindow(QMainWindow):
    """主窗口"""

    start_requested = Signal()
    stop_requested = Signal()
    hotkey_changed = Signal(dict)

    def __init__(self):
        super().__init__()
        self._is_running = False
        self._current_hotkey: dict = {"modifiers": ["ctrl"], "key": "space"}
        self._update_thread = None
        self._init_ui()
        self._init_tray()
        self._check_update_on_startup()

    def _init_ui(self):
        self.setWindowTitle(f"shokaX plugin v{__version__}")
        self.setFixedSize(280, 220)
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

        check_update_action = QAction("检查更新", self)
        check_update_action.triggered.connect(self._manual_check_update)
        menu.addAction(check_update_action)

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

    def _check_update_on_startup(self):
        """启动时检查更新"""
        self._update_thread = UpdateCheckThread()
        self._update_thread.update_found.connect(self._on_update_found)
        self._update_thread.start()

    def _manual_check_update(self):
        """手动检查更新"""
        self._update_thread = UpdateCheckThread()
        self._update_thread.update_found.connect(self._on_update_found)
        self._update_thread.no_update.connect(self._on_no_update)
        self._update_thread.start()

    def _on_update_found(self, update_info: dict):
        """发现新版本"""
        version = update_info["version"]
        setup_url = update_info.get("setup_url")
        portable_url = update_info.get("portable_url")
        changelog = update_info.get("changelog", "")

        # 判断当前是安装版还是便携版
        is_installed = UpdateChecker.is_installed_version()

        # 选择对应的下载链接
        if is_installed and setup_url:
            download_url = setup_url
            install_type = "安装版"
        elif not is_installed and portable_url:
            download_url = portable_url
            install_type = "便携版"
        else:
            # 如果没有对应版本，使用任意可用的
            download_url = setup_url or portable_url
            install_type = "安装版" if setup_url else "便携版"

        if not download_url:
            QMessageBox.warning(
                self,
                "更新失败",
                "未找到可用的更新文件",
            )
            return

        msg = QMessageBox(self)
        msg.setWindowTitle("发现新版本")
        msg.setIcon(QMessageBox.Information)
        msg.setText(f"发现新版本 v{version} ({install_type})\n\n当前版本: v{__version__}")
        if changelog:
            msg.setDetailedText(changelog)
        msg.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        msg.setDefaultButton(QMessageBox.Yes)
        msg.button(QMessageBox.Yes).setText("立即更新")
        msg.button(QMessageBox.No).setText("稍后提醒")

        if msg.exec() == QMessageBox.Yes:
            self._download_and_install(download_url, is_installed)

    def _on_no_update(self):
        """没有更新"""
        QMessageBox.information(
            self,
            "检查更新",
            f"当前已是最新版本 v{__version__}",
        )

    def _download_and_install(self, url: str, is_installed: bool):
        """下载并安装更新"""
        import os
        import sys
        import tempfile
        import subprocess
        import psutil
        import time

        # 创建进度对话框
        progress = QProgressDialog("正在下载更新...", "取消", 0, 100, self)
        progress.setWindowTitle("更新")
        progress.setWindowModality(Qt.WindowModal)
        progress.setMinimumDuration(0)
        progress.setValue(0)

        # 下载到临时文件
        filename = "shokax_plugin_update_setup.exe" if is_installed else "shokax_plugin_update.exe"
        temp_file = os.path.join(tempfile.gettempdir(), filename)

        def update_progress(current, total):
            if total > 0:
                percent = int((current / total) * 100)
                progress.setValue(percent)

        # 下载
        success = UpdateChecker.download_update(url, temp_file, update_progress)

        progress.close()

        if success:
            if is_installed:
                # 安装版：使用 setup 安装程序
                reply = QMessageBox.question(
                    self,
                    "下载完成",
                    "更新已下载完成，是否立即安装？\n（程序将关闭并启动安装程序）",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    # 获取当前进程 PID，传递给安装程序
                    current_pid = os.getpid()

                    # 启动安装程序，传递当前进程 PID
                    # 安装程序会等待当前进程退出后再继续
                    subprocess.Popen([temp_file, f"/PID={current_pid}"])

                    # 退出当前程序
                    from PySide6.QtWidgets import QApplication
                    QApplication.quit()
            else:
                # 便携版：覆盖安装
                reply = QMessageBox.question(
                    self,
                    "下载完成",
                    "更新已下载完成，是否立即安装？\n（程序将退出，请等待几秒后手动启动新版本）",
                    QMessageBox.Yes | QMessageBox.No,
                )

                if reply == QMessageBox.Yes:
                    current_exe = sys.executable
                    backup_exe = current_exe + ".bak"

                    # 创建批处理脚本来完成替换
                    batch_script = os.path.join(tempfile.gettempdir(), "update_shokax.bat")
                    with open(batch_script, "w", encoding="gbk") as f:
                        f.write("@echo off\n")
                        f.write("echo Waiting for application to close...\n")
                        f.write("timeout /t 2 /nobreak >nul\n")
                        f.write(f'if exist "{current_exe}" (\n')
                        f.write(f'    move /y "{current_exe}" "{backup_exe}"\n')
                        f.write(")\n")
                        f.write(f'move /y "{temp_file}" "{current_exe}"\n')
                        f.write("echo Update completed!\n")
                        f.write(f'start "" "{current_exe}"\n')
                        f.write(f'del "{backup_exe}" >nul 2>&1\n')
                        f.write(f'del "%~f0"\n')

                    # 启动批处理脚本
                    subprocess.Popen(
                        ["cmd", "/c", batch_script],
                        creationflags=subprocess.CREATE_NO_WINDOW
                    )

                    # 退出当前程序
                    from PySide6.QtWidgets import QApplication
                    QApplication.quit()
        else:
            QMessageBox.warning(
                self,
                "下载失败",
                "更新下载失败，请稍后重试或手动下载。",
            )

