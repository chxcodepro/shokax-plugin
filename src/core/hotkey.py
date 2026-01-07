"""全局热键管理"""
from pynput import keyboard
from PySide6.QtCore import QObject, Signal


# 修饰键映射
MODIFIER_MAP = {
    "ctrl": (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r),
    "alt": (keyboard.Key.alt_l, keyboard.Key.alt_r),
    "shift": (keyboard.Key.shift_l, keyboard.Key.shift_r),
}

# 特殊键映射
KEY_MAP = {
    "space": keyboard.Key.space,
    "tab": keyboard.Key.tab,
    "grave": "`",
}


class HotkeyManager(QObject):
    """热键管理器"""

    triggered = Signal()  # 热键触发信号

    def __init__(self):
        super().__init__()
        self._listener: keyboard.Listener | None = None
        self._enabled = False
        self._pressed_modifiers: set[str] = set()

        # 默认快捷键: Ctrl+空格
        self._modifiers = {"ctrl"}
        self._trigger_key = keyboard.Key.space

    def set_hotkey(self, modifiers: list[str], key: str):
        """设置快捷键"""
        self._modifiers = set(modifiers)
        self._trigger_key = KEY_MAP.get(key, key)

    def start(self):
        """启动热键监听"""
        if self._listener is not None:
            return
        self._enabled = True
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self._listener.start()

    def stop(self):
        """停止热键监听"""
        self._enabled = False
        if self._listener is not None:
            self._listener.stop()
            self._listener = None
        self._pressed_modifiers.clear()

    def _on_press(self, key):
        """按键按下事件"""
        if not self._enabled:
            return

        # 检查修饰键
        for mod_name, mod_keys in MODIFIER_MAP.items():
            if key in mod_keys:
                self._pressed_modifiers.add(mod_name)
                return

        # 检查触发键
        if self._pressed_modifiers == self._modifiers:
            if self._match_key(key):
                self.triggered.emit()

    def _on_release(self, key):
        """按键释放事件"""
        for mod_name, mod_keys in MODIFIER_MAP.items():
            if key in mod_keys:
                self._pressed_modifiers.discard(mod_name)
                return

    def _match_key(self, key) -> bool:
        """检查是否匹配触发键"""
        if self._trigger_key == key:
            return True
        # 处理字符键
        if hasattr(key, "char") and key.char == self._trigger_key:
            return True
        # 使用虚拟键码匹配（Ctrl+字母 时 char 为空，需要用 vk）
        if hasattr(key, "vk") and isinstance(self._trigger_key, str) and len(self._trigger_key) == 1:
            if key.vk == ord(self._trigger_key.upper()):
                return True
        return False

    @property
    def is_running(self) -> bool:
        """是否正在监听"""
        return self._listener is not None and self._enabled
