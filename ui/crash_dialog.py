import sys
import os
from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit, QPushButton, QWidget
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QCursor
from core.config_manager import config_manager
from ui.styles import get_stylesheet

class ZZZCrashDialog(QDialog):
    def __init__(self, message, is_crash=True, title=None, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.Dialog | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        self.message = message
        self.is_crash = is_crash
        self.custom_title = title
        
        self.drag_position = QPoint()
        
        self.resize(550, 400)
        self.init_ui()
        
    def init_ui(self):
        theme = config_manager.get("theme_mode")
        self.setStyleSheet(get_stylesheet(theme))
        
        # Main layout container
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Dialog central widget (with ZZZ background style)
        self.content_widget = QWidget(self)
        self.content_widget.setObjectName("main_widget")
        self.content_widget.setStyleSheet(f"""
            QWidget#main_widget {{
                background-color: {"#0F0F12" if theme == "dark" else "#E6E6EB"};
                border: 3px solid {"#FF0055"};
            }}
        """)
        layout.addWidget(self.content_widget)
        
        content_layout = QVBoxLayout(self.content_widget)
        content_layout.setContentsMargins(25, 25, 25, 25)
        content_layout.setSpacing(15)
        
        # Header title
        self.title_label = QLabel(self.content_widget)
        title_text = self.custom_title or ("CRITICAL SYSTEM CRASH" if self.is_crash else "STARTUP WARNING")
        self.title_label.setText(title_text)
        self.title_label.setFont(QFont("Consolas", 14, QFont.Weight.Bold))
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(f"color: {'#F3FF00' if theme == 'dark' else '#FF0055'}; text-transform: uppercase; letter-spacing: 1.5px;")
        content_layout.addWidget(self.title_label)
        
        # Subtitle
        sub_label = QLabel("DIAGNOSTIC REPORT / 诊断报告", self.content_widget)
        sub_label.setFont(QFont("Consolas", 8, QFont.Weight.Bold))
        sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        sub_label.setStyleSheet(f"color: {'#00F0FF' if theme == 'dark' else '#0088FF'};")
        content_layout.addWidget(sub_label)
        
        # Console text area
        self.text_edit = QTextEdit(self.content_widget)
        self.text_edit.setReadOnly(True)
        self.text_edit.setText(self.message)
        self.text_edit.setFont(QFont("Consolas", 9))
        self.text_edit.setStyleSheet(f"""
            QTextEdit {{
                background-color: {"#08080A" if theme == "dark" else "#FFFFFF"};
                color: {"#00F0FF" if theme == "dark" else "#0088FF"};
                border: 2px solid {"#3A3A4A" if theme == "dark" else "#A1A1A8"};
                padding: 10px;
            }}
        """)
        content_layout.addWidget(self.text_edit)
        
        # Bottom button row
        btn_layout = QHBoxLayout()
        btn_layout.addStretch(1)
        
        btn_text = "TERMINATE / 确定" if self.is_crash else "CONTINUE / 继续"
        self.close_btn = QPushButton(btn_text, self.content_widget)
        self.close_btn.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.close_btn.setMinimumSize(160, 36)
        
        # Style close button like bouncy button styling
        self.close_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: #F3FF00;
                color: #0F0F12;
                border: 2px solid #0F0F12;
                font-family: "Consolas", monospace;
                font-weight: bold;
                font-size: 11px;
                text-transform: uppercase;
            }}
            QPushButton:hover {{
                background-color: #FF0055;
                color: #FFFFFF;
                border-color: #FFFFFF;
            }}
            QPushButton:pressed {{
                background-color: #00F0FF;
                color: #0F0F12;
            }}
        """)
        self.close_btn.clicked.connect(self.accept)
        btn_layout.addWidget(self.close_btn)
        btn_layout.addStretch(1)
        
        content_layout.addLayout(btn_layout)
        
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_position = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_position)
            event.accept()
