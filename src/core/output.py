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

    # 写入剪贴板并粘贴
    pyperclip.copy(text)
    time.sleep(0.05)  # 短暂延迟确保剪贴板更新

    # 模拟 Ctrl+V 粘贴
    pyautogui.hotkey("ctrl", "v")
    time.sleep(0.05)

    # 光标定位：左移指定字符数
    if cursor_left_offset > 0:
        for _ in range(cursor_left_offset):
            pyautogui.press("left")
            time.sleep(0.01)

    # 恢复原剪贴板内容
    try:
        pyperclip.copy(original_clipboard)
    except Exception:
        pass
