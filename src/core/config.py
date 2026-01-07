"""配置管理"""
from pathlib import Path
import json

CONFIG_PATH = Path.home() / ".shoka-plugin" / "config.json"

DEFAULT_HOTKEY = {"modifiers": ["ctrl"], "key": "space"}


def load_config() -> dict:
    """加载配置"""
    if CONFIG_PATH.exists():
        try:
            data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
            if "hotkey" in data:
                return data
        except (json.JSONDecodeError, KeyError):
            pass
    return {"hotkey": DEFAULT_HOTKEY.copy()}


def save_config(config: dict):
    """保存配置"""
    CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
    CONFIG_PATH.write_text(json.dumps(config, indent=2, ensure_ascii=False), encoding="utf-8")


def get_hotkey_display(hotkey: dict) -> str:
    """获取快捷键显示文本"""
    parts = [m.capitalize() for m in hotkey.get("modifiers", ["ctrl"])]
    key = hotkey.get("key", "space")
    key_display = {"space": "空格", "grave": "`", "tab": "Tab"}.get(key, key.upper())
    parts.append(key_display)
    return "+".join(parts)
