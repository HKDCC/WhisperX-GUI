import math
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QFont
from core.config_manager import config_manager
from core.translator import translator

class DropZone(QWidget):
    files_selected = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setMinimumHeight(190)
        self.setObjectName("dropzone")
        
        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(15, 110, 15, 15)  # Offset text so cassette deck fits in center
        self.vBoxLayout.setSpacing(4)
        
        self.title_label = QLabel(self)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setObjectName("dz_title")
        
        self.sub_label = QLabel(self)
        self.sub_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.sub_label.setObjectName("dz_sub")
        
        self.vBoxLayout.addWidget(self.title_label)
        self.vBoxLayout.addWidget(self.sub_label)
        
        self.update_content()
        self.update_style()

    def update_content(self):
        self.title_label.setText(translator.t("dropzone_title"))
        self.sub_label.setText(translator.t("dropzone_subtitle"))

    def update_style(self):
        # Handle background painting in paintEvent, keep widget container background transparent in CSS.
        theme = config_manager.get("theme_mode")
        if theme == "light":
            self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #0F0F12; background: transparent; text-transform: uppercase;")
            self.sub_label.setStyleSheet("font-size: 11px; color: #5C5C64; background: transparent;")
        else:
            self.title_label.setStyleSheet("font-size: 13px; font-weight: bold; color: #FFFFFF; background: transparent; text-transform: uppercase;")
            self.sub_label.setStyleSheet("font-size: 11px; color: #8E8E93; background: transparent;")
        self.setStyleSheet("""
            QWidget#dropzone {
                background-color: transparent;
            }
        """)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        is_hovered = self.underMouse()
        theme = config_manager.get("theme_mode")
        
        # 1. Main outer housing
        bg_color = QColor("#D8D8DF") if theme == "light" else QColor("#08080B")
        painter.setBrush(QBrush(bg_color))
        
        if theme == "light":
            border_color = QColor("#FF0055") if is_hovered else QColor("#0F0F12")
            border_width = 3
        else:
            border_color = QColor("#F3FF00") if is_hovered else QColor("#2A2A35")
            border_width = 3
            
        painter.setPen(QPen(border_color, border_width))
        painter.drawRect(1, 1, w - 2, h - 2)
        
        # 2. Diagonal hazard stripes band at the very top (draw black background strip first)
        stripe_h = 8
        painter.fillRect(2, 2, w - 4, stripe_h, QColor("#0F0F12"))
        
        painter.setPen(Qt.PenStyle.NoPen)
        for x in range(-20, w, 15):
            painter.setBrush(QBrush(QColor("#F3FF00")))
            poly = QPolygonF([
                QPointF(float(x), 2.0),
                QPointF(float(x) + 7.0, 2.0),
                QPointF(float(x) + 7.0 - float(stripe_h), 2.0 + float(stripe_h)),
                QPointF(float(x) - float(stripe_h), 2.0 + float(stripe_h))
            ])
            painter.drawPolygon(poly)
            
        # 3. Draw Retro Cassette Deck in the center
        cx = w / 2.0
        cy = h / 2.0 - 20.0
        
        tw, th = 140.0, 76.0
        tx = cx - tw / 2.0
        ty = cy - th / 2.0
        
        # Tape shell outer body (angled corners)
        tape_bg = QColor("#FFFFFF") if theme == "light" else QColor("#15151A")
        painter.setBrush(QBrush(tape_bg))
        
        tape_border = QColor("#FF0055") if is_hovered else (QColor("#0F0F12") if theme == "light" else QColor("#3E3E4E"))
        painter.setPen(QPen(tape_border, 3 if theme == "light" else 2))
        
        tape_poly = QPolygonF([
            QPointF(tx + 6.0, ty),
            QPointF(tx + tw - 6.0, ty),
            QPointF(tx + tw, ty + 6.0),
            QPointF(tx + tw, ty + th - 6.0),
            QPointF(tx + tw - 6.0, ty + th),
            QPointF(tx + 6.0, ty + th),
            QPointF(tx, ty + th - 6.0),
            QPointF(tx, ty + 6.0)
        ])
        painter.drawPolygon(tape_poly)
        
        # Cassette transparent window
        wx, wy, ww, wh = tx + 18.0, ty + 16.0, tw - 36.0, th - 40.0
        window_bg = QColor("#EDEDF2") if theme == "light" else QColor("#08080A")
        window_border = QColor("#0088FF") if theme == "light" else QColor("#00F0FF")
        painter.setBrush(QBrush(window_bg))
        painter.setPen(QPen(window_border, 2 if theme == "light" else 1))
        painter.drawRect(QRectF(wx, wy, ww, wh))
        
        # Spools
        r = 11.0
        sp1_x = wx + ww / 4.0
        sp2_x = wx + 3.0 * ww / 4.0
        sp_y = wy + wh / 2.0
        
        # Left Spool
        spool_bg = QColor("#D8D8DF") if theme == "light" else QColor("#24242E")
        spool_border = QColor("#0F0F12") if theme == "light" else QColor("#FFFFFF")
        painter.setBrush(QBrush(spool_bg))
        painter.setPen(QPen(spool_border, 2 if theme == "light" else 1))
        painter.drawEllipse(QPointF(sp1_x, sp_y), r, r)
        
        # Right Spool
        painter.drawEllipse(QPointF(sp2_x, sp_y), r, r)
        
        # Spool gears / spokes
        spool_spoke_color = QColor("#FF0055") if is_hovered else (QColor("#0088FF") if theme == "light" else QColor("#A1A1A8"))
        painter.setPen(QPen(spool_spoke_color, 2 if theme == "light" else 1.5))
        for angle in range(0, 360, 60):
            rad = math.radians(angle)
            dx = math.cos(rad) * (r - 2.0)
            dy = math.sin(rad) * (r - 2.0)
            painter.drawLine(QPointF(sp1_x, sp_y), QPointF(sp1_x + dx, sp_y + dy))
            painter.drawLine(QPointF(sp2_x, sp_y), QPointF(sp2_x + dx, sp_y + dy))
            
        # Tiny tape label details
        text_color = QColor("#0F0F12") if theme == "light" else QColor("#7A7A85")
        painter.setPen(QPen(text_color))
        font = QFont("Consolas", 7, QFont.Weight.Bold)
        painter.setFont(font)
        painter.drawText(QPointF(tx + 8.0, ty + 12.0), "ZZZ-90")
        painter.drawText(QPointF(tx + tw - 38.0, ty + 12.0), "SIDE A")
        
        # Retro Cassette Label
        label_color = QColor("#0088FF") if theme == "light" else QColor("#00F0FF")
        painter.setPen(QPen(label_color, 1))
        font_sm = QFont("Consolas", 6)
        painter.setFont(font_sm)
        painter.drawText(QPointF(tx + 28.0, ty + th - 10.0), "CASSETTE FUTURISM")
        
        # Neon REC light
        rec_color = QColor("#FF0055") if is_hovered else (QColor("#FF0055") if theme == "light" else QColor("#400010"))
        painter.setBrush(QBrush(rec_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(tx + tw - 15.0, ty + th - 15.0), 3.0, 3.0)
        
        painter.setPen(QPen(QColor("#FF0055") if is_hovered or theme == "light" else QColor("#7A7A85")))
        painter.drawText(QPointF(tx + tw - 34.0, ty + th - 10.0), "REC")
        
        painter.end()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        if files:
            self.files_selected.emit(files)

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            files, _ = QFileDialog.getOpenFileNames(
                self, 
                translator.t("dropzone_title"), 
                "", 
                "Media Files (*.mp3 *.wav *.m4a *.mp4 *.mkv *.avi *.flac);;All Files (*.*)"
            )
            if files:
                self.files_selected.emit(files)
