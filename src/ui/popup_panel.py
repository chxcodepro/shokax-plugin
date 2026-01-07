"""仿输入法弹出选择面板"""
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal, QPoint
from PySide6.QtGui import QCursor, QPainter, QColor, QFont, QPen, QPainterPath

from src.core.menu_config import MENU_ITEMS, SUB_MENU_ITEMS, get_output


# 指示器颜色
INDICATOR_COLORS = {
    "primary": "#9333ea",
    "info": "#0ea5e9",
    "warning": "#eab308",
    "success": "#22c55e",
    "danger": "#ef4444",
}


class CircleIndicator(QWidget):
    """圆形指示器（用于提醒）"""

    def __init__(self, color: str, icon: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._icon = icon
        self.setFixedSize(14, 14)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        painter.setBrush(QColor(self._color))
        painter.setPen(Qt.NoPen)
        painter.drawEllipse(1, 1, 12, 12)

        painter.setPen(QColor("#ffffff"))
        font = QFont()
        font.setPixelSize(8)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(self.rect(), Qt.AlignCenter, self._icon)


class ArrowIndicator(QWidget):
    """箭头指示器（用于折叠）"""

    def __init__(self, color: str, parent=None):
        super().__init__(parent)
        self._color = color
        self.setFixedSize(14, 14)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(self._color))
        pen.setWidth(2)
        pen.setCapStyle(Qt.RoundCap)
        pen.setJoinStyle(Qt.RoundJoin)
        painter.setPen(pen)

        path = QPainterPath()
        path.moveTo(4, 3)
        path.lineTo(10, 7)
        path.lineTo(4, 11)
        painter.drawPath(path)


class BorderIndicator(QWidget):
    """边框指示器（用于方块）"""

    def __init__(self, color: str, text: str, parent=None):
        super().__init__(parent)
        self._color = color
        self._text = text
        font = QFont()
        font.setPixelSize(9)
        self._font = font
        self.setFixedSize(max(36, len(text) * 6 + 10), 16)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)

        pen = QPen(QColor(self._color))
        pen.setWidth(1)
        painter.setPen(pen)
        painter.setBrush(Qt.NoBrush)
        painter.drawRoundedRect(1, 1, self.width() - 2, self.height() - 2, 3, 3)

        painter.setPen(QColor(self._color))
        painter.setFont(self._font)
        painter.drawText(self.rect(), Qt.AlignCenter, self._text)


class MenuItemWidget(QWidget):
    """菜单项组件"""

    clicked = Signal()

    def __init__(
        self,
        index: int,
        text: str,
        indicator: QWidget | None = None,
        parent=None,
    ):
        super().__init__(parent)
        self._selected = False
        self._index = index

        layout = QHBoxLayout(self)
        layout.setContentsMargins(6, 3, 8, 3)
        layout.setSpacing(5)

        # 序号
        self._index_label = QLabel(str(index))
        self._index_label.setStyleSheet(
            "color: #a1a1aa; font-size: 10px; min-width: 10px;"
        )
        layout.addWidget(self._index_label)

        # 指示器（子菜单项才有）
        if indicator:
            layout.addWidget(indicator)

        # 文本
        self._text_label = QLabel(text)
        self._text_label.setStyleSheet("color: #3f3f46; font-size: 12px;")
        layout.addWidget(self._text_label)
        layout.addStretch()

        self.setFixedHeight(26)
        self.setCursor(Qt.PointingHandCursor)

    def set_selected(self, selected: bool):
        """设置选中状态"""
        self._selected = selected
        if selected:
            self.setStyleSheet(
                "background-color: #6366f1; border-radius: 4px;"
            )
            self._index_label.setStyleSheet(
                "color: rgba(255,255,255,0.6); font-size: 10px; min-width: 10px;"
            )
            self._text_label.setStyleSheet("color: #ffffff; font-size: 12px;")
        else:
            self.setStyleSheet("background-color: transparent;")
            self._index_label.setStyleSheet(
                "color: #a1a1aa; font-size: 10px; min-width: 10px;"
            )
            self._text_label.setStyleSheet("color: #3f3f46; font-size: 12px;")
        self.update()

    def enterEvent(self, event):
        if not self._selected:
            self.setStyleSheet("background-color: #f4f4f5; border-radius: 4px;")
        super().enterEvent(event)

    def leaveEvent(self, event):
        if not self._selected:
            self.setStyleSheet("background-color: transparent;")
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)


class PopupPanel(QWidget):
    """弹出选择面板"""

    output_selected = Signal(str, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self._current_level = 0
        self._selected_index = 0
        self._current_menu_key = ""
        self._menu_items: list[MenuItemWidget] = []

        self._init_ui()

    def _init_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint
            | Qt.WindowStaysOnTopHint
            | Qt.Tool
            | Qt.Popup
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedWidth(140)

        self._container = QWidget(self)
        self._container.setObjectName("popup_panel")
        self._container.setStyleSheet(
            """
            QWidget#popup_panel {
                background-color: #ffffff;
                border: 1px solid #e4e4e7;
                border-radius: 8px;
            }
            """
        )

        self._layout = QVBoxLayout(self._container)
        self._layout.setContentsMargins(4, 4, 4, 4)
        self._layout.setSpacing(2)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.addWidget(self._container)

    def show_at_cursor(self):
        """在光标位置显示"""
        self._show_main_menu()
        pos = QCursor.pos()
        self.move(pos + QPoint(10, 10))
        self.show()
        self.activateWindow()
        self.setFocus()

    def _clear_menu(self):
        """清空菜单"""
        for item in self._menu_items:
            item.deleteLater()
        self._menu_items.clear()

    def _show_main_menu(self):
        """显示主菜单"""
        self._clear_menu()
        self._current_level = 0
        self._selected_index = 0

        for i, menu_item in enumerate(MENU_ITEMS):
            widget = MenuItemWidget(i + 1, menu_item.label)
            widget.clicked.connect(lambda idx=i: self._on_item_clicked(idx))
            self._layout.addWidget(widget)
            self._menu_items.append(widget)

        self._update_selection()
        self.adjustSize()

    def _show_sub_menu(self, menu_key: str):
        """显示子菜单"""
        self._clear_menu()
        self._current_level = 1
        self._current_menu_key = menu_key
        self._selected_index = 0

        # 子菜单指示器图标
        icons = {
            "primary": "+",
            "info": "i",
            "warning": "!",
            "success": "✓",
            "danger": "-",
        }

        for i, sub_item in enumerate(SUB_MENU_ITEMS):
            color = INDICATOR_COLORS.get(sub_item.key, "#666666")

            # 根据父菜单类型选择指示器样式
            if menu_key == "fold":
                indicator = ArrowIndicator(color)
            elif menu_key == "block":
                indicator = BorderIndicator(color, sub_item.label)
            else:
                # reminder 和其他使用圆形
                indicator = CircleIndicator(color, icons.get(sub_item.key, ""))

            # block 类型不需要额外文本（已在指示器中显示）
            text = "" if menu_key == "block" else sub_item.label
            widget = MenuItemWidget(i + 1, text, indicator)
            widget.clicked.connect(lambda idx=i: self._on_sub_item_clicked(idx))
            self._layout.addWidget(widget)
            self._menu_items.append(widget)

        self._update_selection()
        self.adjustSize()

    def _update_selection(self):
        """更新选中状态"""
        for i, item in enumerate(self._menu_items):
            item.set_selected(i == self._selected_index)

    def _on_item_clicked(self, index: int):
        """主菜单项点击"""
        self._select_item(index)

    def _on_sub_item_clicked(self, index: int):
        """子菜单项点击"""
        self._select_sub_item(index)

    def _select_item(self, index: int):
        """选择主菜单项"""
        if index < 0 or index >= len(MENU_ITEMS):
            return

        menu_item = MENU_ITEMS[index]
        if menu_item.has_submenu:
            self._show_sub_menu(menu_item.key)
        else:
            text, offset = get_output(menu_item.key)
            self.hide()
            self.output_selected.emit(text, offset)

    def _select_sub_item(self, index: int):
        """选择子菜单项"""
        if index < 0 or index >= len(SUB_MENU_ITEMS):
            return

        sub_item = SUB_MENU_ITEMS[index]
        text, offset = get_output(self._current_menu_key, sub_item.key)
        self.hide()
        self.output_selected.emit(text, offset)

    def keyPressEvent(self, event):
        key = event.key()

        # 数字键选择
        if Qt.Key_1 <= key <= Qt.Key_9:
            index = key - Qt.Key_1
            if self._current_level == 0:
                self._select_item(index)
            else:
                self._select_sub_item(index)
            return

        # 上下键导航
        if key == Qt.Key_Up:
            self._selected_index = max(0, self._selected_index - 1)
            self._update_selection()
        elif key == Qt.Key_Down:
            self._selected_index = min(len(self._menu_items) - 1, self._selected_index + 1)
            self._update_selection()

        # 回车确认
        elif key == Qt.Key_Return or key == Qt.Key_Enter:
            if self._current_level == 0:
                self._select_item(self._selected_index)
            else:
                self._select_sub_item(self._selected_index)

        # ESC 直接关闭
        elif key == Qt.Key_Escape:
            self.hide()

        # Backspace返回上级
        elif key == Qt.Key_Backspace:
            if self._current_level == 1:
                self._show_main_menu()

        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        """失去焦点时隐藏"""
        self.hide()
        super().focusOutEvent(event)
