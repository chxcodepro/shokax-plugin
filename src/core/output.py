"""文本输出处理"""
import time
import pyperclip
import pyautogui


def output_text(text: str, cursor_left_offset: int = 0):
    """
    输出文本并定位光标

    Args:
        text: 要输出的文本
        cursor_left_offset: 光标需要左移的字符数
    """
    # 保存原剪贴板内容
    try:
        original_clipboard = pyperclip.paste()
    except Exception:
        original_clipboard = ""

    # 检测是否有选中文字（通过 Ctrl+C 获取）
    pyautogui.hotkey("ctrl", "c")
    time.sleep(0.05)

    try:
        selected_text = pyperclip.paste()
    except Exception:
        selected_text = ""

    # 判断是否有选中内容（与原剪贴板不同且非空）
    has_selection = selected_text and selected_text != original_clipboard

    if has_selection:
        # 包裹模式：将选中文字插入到模板中光标位置
        # 计算插入位置（从末尾往前数 cursor_left_offset 个字符）
        if cursor_left_offset > 0:
            insert_pos = len(text) - cursor_left_offset
            wrapped_text = text[:insert_pos] + selected_text + text[insert_pos:]
        else:
            # 如果没有偏移量，直接追加
            wrapped_text = text + selected_text

        # 写入包裹后的文本到剪贴板
        pyperclip.copy(wrapped_text)
        time.sleep(0.05)

        # 粘贴
        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.05)

        # 光标定位：定位到选中文字后面（即原来的 cursor_left_offset 位置）
        if cursor_left_offset > 0:
            for _ in range(cursor_left_offset):
                pyautogui.press("left")
                time.sleep(0.01)
    else:
        # 原有逻辑：无选中文字时直接输出模板
        pyperclip.copy(text)
        time.sleep(0.05)

        pyautogui.hotkey("ctrl", "v")
        time.sleep(0.05)

        if cursor_left_offset > 0:
            for _ in range(cursor_left_offset):
                pyautogui.press("left")
                time.sleep(0.01)

    # 恢复原剪贴板内容
    try:
        pyperclip.copy(original_clipboard)
    except Exception:
        pass
