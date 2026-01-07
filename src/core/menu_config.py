"""菜单配置数据"""
from dataclasses import dataclass
from typing import Callable


@dataclass
class SubMenuItem:
    """子菜单项"""
    key: str
    label: str
    icon: str
    color: str


@dataclass
class MenuItem:
    """菜单项"""
    key: str
    label: str
    has_submenu: bool
    template: str | Callable[[str], str] = ""
    cursor_offset: int | Callable[[str], int] = 0


# 子菜单选项（用于提醒、折叠、方块）
SUB_MENU_ITEMS = [
    SubMenuItem("primary", "primary", "+", "#9333ea"),
    SubMenuItem("info", "info", "i", "#0ea5e9"),
    SubMenuItem("warning", "warning", "!", "#eab308"),
    SubMenuItem("success", "success", "✓", "#22c55e"),
    SubMenuItem("danger", "danger", "-", "#ef4444"),
]


def _reminder_template(sub_key: str) -> str:
    return f":::{sub_key}\n\n:::"


def _reminder_offset(sub_key: str) -> int:
    # 光标需要定位到两个:::之间的空行
    # 模板: ":::{sub_key}\n\n:::" 从末尾往前数4个字符（\n:::）
    return 4


def _fold_template(sub_key: str) -> str:
    return f"+++{sub_key}\n\n+++"


def _fold_offset(sub_key: str) -> int:
    return 4


def _block_template(sub_key: str) -> str:
    return f"[]{{.label .{sub_key}}}"


def _block_offset(sub_key: str) -> int:
    # 光标定位到[]内，从末尾往前数到[之后
    # 模板: "[]{.label .xxx}" 需要定位到[]内
    return len(f"{{.label .{sub_key}}}") + 1


# 主菜单配置
MENU_ITEMS = [
    MenuItem(
        key="rainbow",
        label="彩虹",
        has_submenu=False,
        template="[]{.rainbow}",
        cursor_offset=11,  # 从末尾往前数11个字符到[]中间
    ),
    MenuItem(
        key="reminder",
        label="提醒",
        has_submenu=True,
        template=_reminder_template,
        cursor_offset=_reminder_offset,
    ),
    MenuItem(
        key="fold",
        label="折叠",
        has_submenu=True,
        template=_fold_template,
        cursor_offset=_fold_offset,
    ),
    MenuItem(
        key="block",
        label="方块",
        has_submenu=True,
        template=_block_template,
        cursor_offset=_block_offset,
    ),
    MenuItem(
        key="card",
        label="卡片",
        has_submenu=False,
        template=";;;[id] []\n\n;;;",
        cursor_offset=4,  # 从末尾往前数4个字符到空行位置
    ),
]


def get_output(menu_key: str, sub_key: str | None = None) -> tuple[str, int]:
    """
    获取输出文本和光标偏移量

    Args:
        menu_key: 主菜单key
        sub_key: 子菜单key（如果有）

    Returns:
        (输出文本, 光标左移偏移量)
    """
    for item in MENU_ITEMS:
        if item.key == menu_key:
            if item.has_submenu and sub_key:
                text = item.template(sub_key) if callable(item.template) else item.template
                offset = item.cursor_offset(sub_key) if callable(item.cursor_offset) else item.cursor_offset
            else:
                text = item.template if isinstance(item.template, str) else ""
                offset = item.cursor_offset if isinstance(item.cursor_offset, int) else 0
            return text, offset
    return "", 0
