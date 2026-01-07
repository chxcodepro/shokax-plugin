"""样式定义"""

# 主窗口样式
MAIN_WINDOW_STYLE = """
QMainWindow {
    background-color: #f5f5f5;
}
QPushButton {
    background-color: #1a73e8;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 24px;
    font-size: 14px;
}
QPushButton:hover {
    background-color: #1557b0;
}
QPushButton:pressed {
    background-color: #104a9e;
}
QPushButton#stop_btn {
    background-color: #ea4335;
}
QPushButton#stop_btn:hover {
    background-color: #c5221f;
}
QLabel#title {
    font-size: 16px;
    font-weight: bold;
    color: #333333;
}
QLabel#status {
    font-size: 12px;
    color: #666666;
}
"""
