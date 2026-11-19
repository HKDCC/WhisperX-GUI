from PyQt6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QPushButton,
    QWidget,
    QApplication,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont
from core.config_manager import config_manager
from ui.styles import get_stylesheet


class ZZZCrashDialog(QDialog):
    """Straight, retro-futurist diagnostic & warning dialog."""

    def __init__(self, message, is_crash=True, title=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        self.message = message
        self.is_crash = is_crash
        self.custom_title = title
        self.drag_position = QPoint()

        self.resize(560, 410)
        self.init_ui()

    def init_ui(self):
        theme = config_manager.get("theme_mode")
        self.setStyleSheet(get_stylesheet(theme))

        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 12, 12, 12)

        accent = "#EF4444" if self.is_crash else "#FF5C1A"
        bg = "#111318" if theme == "dark" else "#F2EFE8"
        border = accent
        text_primary = "#F2F4F8" if theme == "dark" else "#141519"
        text_muted = "#949BA8" if theme == "dark" else "#565A65"
        console_bg = "#0A0B0E" if theme == "dark" else "#FFFFFF"
        console_fg = "#E2E6EE" if theme == "dark" else "#141519"
        console_border = "#2A2E3A" if theme == "dark" else "#18191E"

        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("crash_container")
        self.content_widget.setStyleSheet(f"""
            QWidget#crash_container {{
                background-color: {bg};
                border: 2px solid {border};
                border-radius: 3px;
            }}
        """)
        layout.addWidget(self.content_widget)

        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(22, 20, 22, 20)
        content_layout.setSpacing(12)

        # Header strip
        header_row = QHBoxLayout()
        header_row.setSpacing(10)

        tag_label = QLabel("ERR // CRITICAL" if self.is_crash else "SYS // NOTICE", self.content_widget)
        tag_label.setFont(QFont("Consolas", 9, QFont.Weight.Bold))
        tag_label.setStyleSheet(f"""
            background-color: {accent};
            color: #FFFFFF;
            padding: 3px 8px;
            border-radius: 2px;
        """)
        header_row.addWidget(tag_label)

        title_text = self.custom_title or ("CRITICAL SYSTEM CRASH" if self.is_crash else "STARTUP WARNING")
        self.title_label = QLabel(title_text, self.content_widget)
        self.title_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        self.title_label.setStyleSheet(f"color: {text_primary}; background: transparent;")
        header_row.addWidget(self.title_label)
        header_row.addStretch(1)
        content_layout.addLayout(header_row)

        sub_label = QLabel("DIAGNOSTIC TELEMETRY / 系统诊断报告", self.content_widget)
        sub_label.setFont(QFont("Consolas", 9))
        sub_label.setStyleSheet(f"color: {text_muted}; background: transparent;")
        content_layout.addWidget(sub_label)

        self.text_edit = QTextEdit(self.content_widget)
        self.text_edit.setReadOnly(True)
        self.text_edit.setPlainText(self.message)
        self.text_edit.setFont(QFont("Consolas", 9))
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {console_bg};
                color: {console_fg};
                border: 1.5px solid {console_border};
                border-radius: 2px;
                padding: 10px;
            }}
        """)
        content_layout.addWidget(self.text_edit)

        btn_layout = QHBoxLayout()
        btn_layout.setSpacing(10)

        self.copy_btn = QPushButton("COPY LOG / 复制日志", self.content_widget)
        self.copy_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.copy_btn.setMinimumHeight(34)
        self.copy_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {"#161920" if theme == "dark" else "#FFFFFF"};
                color: {text_primary};
                border: 1.5px solid {console_border};
                border-radius: 2px;
                padding: 0 14px;
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                font-weight: 600;
                font-size: 12px;
            }}
            QPushButton:hover {{
                border-color: {accent};
                color: {accent};
            }}
        """)
        self.copy_btn.clicked.connect(self.copy_log)
        btn_layout.addWidget(self.copy_btn)

        btn_layout.addStretch(1)

        btn_text = "TERMINATE / 确定" if self.is_crash else "CONTINUE / 继续"
        self.close_btn = QPushButton(btn_text, self.content_widget)
        self.close_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.close_btn.setMinimumSize(150, 34)
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {accent};
                color: #FFFFFF;
                border: 1.5px solid {accent};
                border-radius: 2px;
                padding: 0 16px;
                font-family: "Segoe UI", "Microsoft YaHei UI", sans-serif;
                font-weight: 700;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {"#F87171" if self.is_crash else "#FF7338"};
            }}
        """)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)

        content_layout.addLayout(btn_layout)

    def copy_log(self):
        cb = QApplication.clipboard()
        if cb:
            cb.setText(self.message)
        self.copy_btn.setText("COPIED / 已复制")

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
