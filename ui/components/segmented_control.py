from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QFont
from PyQt6.QtCore import Qt, pyqtSignal, QRectF
from core.config_manager import config_manager


class SegmentButton(QPushButton):
    """Straight, flush-aligned tactile segment inside SegmentedControl."""

    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(24)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        theme = config_manager.get("theme_mode")
        is_checked = self.isChecked()
        is_hovered = self.underMouse()
        is_enabled = self.isEnabled()

        rect = QRectF(0.5, 0.5, w - 1.0, h - 1.0)

        if not is_enabled:
            bg = QColor("#E4E1D7" if theme == "light" else "#14171E")
            border = QColor("#CEC9BC" if theme == "light" else "#232732")
            fg = QColor("#A09B8F" if theme == "light" else "#4C5366")
        elif is_checked:
            if theme == "light":
                bg = QColor("#141519")
                border = QColor("#141519")
                fg = QColor("#E5FF2E")
            else:
                bg = QColor("#E5FF2E")
                border = QColor("#E5FF2E")
                fg = QColor("#111318")
        else:
            if theme == "light":
                bg = QColor("#E6E2D8" if is_hovered else "#F7F5F0")
                border = QColor("#141519" if is_hovered else "#CFCAC0")
                fg = QColor("#141519")
            else:
                bg = QColor("#222733" if is_hovered else "#161920")
                border = QColor("#525B70" if is_hovered else "#262B36")
                fg = QColor("#F2F4F8" if is_hovered else "#A8B0BF")

        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(border, 1.0))
        painter.drawRoundedRect(rect, 2.0, 2.0)

        font = QFont("Segoe UI", 9, QFont.Weight.DemiBold)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        painter.setFont(font)
        painter.setPen(fg)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


# Backwards-compatible alias
SkewedTabButton = SegmentButton


class SegmentedControl(QWidget):
    currentItemChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(3, 3, 3, 3)
        self.layout.setSpacing(3)
        self.items = []  # list of (key, text, button)
        self.current_key = None
        self.setObjectName("segmented_control")
        self.setFixedHeight(30)
        self.update_style()

    def addItem(self, key, text):
        btn = SegmentButton(text, self)
        btn.setObjectName("segment_btn")
        btn.clicked.connect(lambda _checked=False, k=key: self.on_btn_clicked(k))
        self.layout.addWidget(btn)
        self.items.append((key, text, btn))
        if len(self.items) == 1:
            self.setCurrentItem(key)

    def on_btn_clicked(self, key):
        self.setCurrentItem(key)
        self.currentItemChanged.emit(key)

    def setCurrentItem(self, key):
        self.current_key = key
        for k, _t, btn in self.items:
            btn.setChecked(k == key)
        self.update()

    def setItemEnabled(self, key, enabled):
        for k, _t, btn in self.items:
            if k == key:
                btn.setEnabled(enabled)
                btn.update()
                break

    def setItemText(self, key, text):
        for i, (k, _t, btn) in enumerate(self.items):
            if k == key:
                self.items[i] = (k, text, btn)
                btn.setText(text)
                btn.update()
                break

    def update_style(self):
        theme = config_manager.get("theme_mode")
        if theme == "light":
            self.setStyleSheet("""
                QWidget#segmented_control {
                    background-color: #E2DFD5;
                    border: 1px solid #18191E;
                    border-radius: 3px;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget#segmented_control {
                    background-color: #0D0E12;
                    border: 1px solid #2A2E3A;
                    border-radius: 3px;
                }
            """)
        for _k, _t, btn in self.items:
            btn.update()
