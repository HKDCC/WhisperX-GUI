import math
import os
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QFileDialog
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QFont
from core.config_manager import config_manager
from core.translator import translator

SUPPORTED_EXTENSIONS = {".mp3", ".wav", ".m4a", ".mp4", ".mkv", ".avi", ".flac", ".ogg", ".webm", ".mov", ".aac"}


class DropZone(QWidget):
    files_selected = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setFixedHeight(156)
        self.setObjectName("dropzone")
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self.vBoxLayout = QVBoxLayout(self)
        self.vBoxLayout.setContentsMargins(20, 96, 20, 14)
        self.vBoxLayout.setSpacing(3)

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
        theme = config_manager.get("theme_mode")
        if theme == "light":
            self.title_label.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #141519; background: transparent;"
            )
            self.sub_label.setStyleSheet(
                "font-size: 11px; color: #565A65; background: transparent;"
            )
        else:
            self.title_label.setStyleSheet(
                "font-size: 13px; font-weight: 700; color: #F2F4F8; background: transparent;"
            )
            self.sub_label.setStyleSheet(
                "font-size: 11px; color: #949BA8; background: transparent;"
            )
        self.setStyleSheet("QWidget#dropzone { background-color: transparent; }")
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        is_hovered = self.underMouse() and self.isEnabled()
        theme = config_manager.get("theme_mode")

        # 1. Outer straight deck housing
        if theme == "light":
            bg_color = QColor("#FAF8F3" if not is_hovered else "#FFFFFF")
            border_color = QColor("#FF5C1A" if is_hovered else "#18191E")
            subtle_color = QColor("#D5D0C5")
            text_meta = QColor("#6E727D")
        else:
            bg_color = QColor("#151820" if not is_hovered else "#191D27")
            border_color = QColor("#FF5C1A" if is_hovered else "#2A2E3A")
            subtle_color = QColor("#232733")
            text_meta = QColor("#687080")

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.0))
        painter.drawRoundedRect(QRectF(0.5, 0.5, w - 1.0, h - 1.0), 3.0, 3.0)

        # 2. Clean 3px top hardware accent bar
        top_bar_color = QColor("#FF5C1A") if is_hovered else (QColor("#18191E") if theme == "light" else QColor("#2E3444"))
        painter.setBrush(QBrush(top_bar_color))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(1.0, 1.0, w - 2.0, 3.0))

        # 3. Subtle corner registration ticks & telemetry micro-tags
        font_meta = QFont("Consolas", 8, QFont.Weight.Bold)
        painter.setFont(font_meta)
        painter.setPen(QPen(QColor("#FF5C1A") if is_hovered else text_meta))
        painter.drawText(QPointF(14.0, 22.0), "DECK // 01")
        painter.setPen(QPen(text_meta))
        painter.drawText(QRectF(w - 190.0, 11.0, 176.0, 16.0), Qt.AlignmentFlag.AlignRight, "MEDIA DROP BAY")

        # Subtle horizontal divider line below telemetry strip
        painter.setPen(QPen(subtle_color, 1.0))
        painter.drawLine(QPointF(12.0, 29.0), QPointF(w - 12.0, 29.0))

        # 4. Crisp architectural Cassette Icon centered at y=60
        cx = w / 2.0
        cy = 60.0
        tw, th = 112.0, 50.0
        tx = cx - tw / 2.0
        ty = cy - th / 2.0
        chamfer = 4.0

        tape_bg = QColor("#EFECE4") if theme == "light" else QColor("#101218")
        tape_border = QColor("#FF5C1A") if is_hovered else (QColor("#18191E") if theme == "light" else QColor("#40475A"))

        tape_poly = QPolygonF([
            QPointF(tx + chamfer, ty),
            QPointF(tx + tw - chamfer, ty),
            QPointF(tx + tw, ty + chamfer),
            QPointF(tx + tw, ty + th - chamfer),
            QPointF(tx + tw - chamfer, ty + th),
            QPointF(tx + chamfer, ty + th),
            QPointF(tx, ty + th - chamfer),
            QPointF(tx, ty + chamfer),
        ])
        painter.setBrush(QBrush(tape_bg))
        painter.setPen(QPen(tape_border, 1.5))
        painter.drawPolygon(tape_poly)

        # Cassette recessed tape window
        wx, wy, ww, wh = tx + 16.0, ty + 13.0, tw - 32.0, th - 26.0
        win_bg = QColor("#FFFFFF") if theme == "light" else QColor("#0B0C10")
        win_border = QColor("#18191E") if theme == "light" else QColor("#2D3342")
        painter.setBrush(QBrush(win_bg))
        painter.setPen(QPen(win_border, 1.0))
        painter.drawRect(QRectF(wx, wy, ww, wh))

        # Left & right tape spools
        r = 7.5
        sp1_x = wx + ww * 0.27
        sp2_x = wx + ww * 0.73
        sp_y = wy + wh / 2.0

        spool_fill = QColor("#E2DFD5") if theme == "light" else QColor("#1E222D")
        spool_edge = QColor("#141519") if theme == "light" else QColor("#949BA8")
        painter.setBrush(QBrush(spool_fill))
        painter.setPen(QPen(spool_edge, 1.2))
        painter.drawEllipse(QPointF(sp1_x, sp_y), r, r)
        painter.drawEllipse(QPointF(sp2_x, sp_y), r, r)

        # Spool teeth
        spoke_color = QColor("#FF5C1A") if is_hovered else (QColor("#141519") if theme == "light" else QColor("#E5FF2E"))
        painter.setPen(QPen(spoke_color, 1.2))
        for angle in (0, 120, 240):
            rad = math.radians(angle)
            dx = math.cos(rad) * (r - 2.2)
            dy = math.sin(rad) * (r - 2.2)
            painter.drawLine(QPointF(sp1_x, sp_y), QPointF(sp1_x + dx, sp_y + dy))
            painter.drawLine(QPointF(sp2_x, sp_y), QPointF(sp2_x + dx, sp_y + dy))

        # Cassette micro-label & REC LED
        painter.setFont(QFont("Consolas", 6, QFont.Weight.Bold))
        painter.setPen(QPen(text_meta))
        painter.drawText(QPointF(tx + 8.0, ty + 10.0), "TAPE-90")

        rec_dot = QColor("#FF5C1A") if is_hovered else QColor("#8D887B" if theme == "light" else "#3A404E")
        painter.setBrush(QBrush(rec_dot))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawEllipse(QPointF(tx + tw - 11.0, ty + 7.5), 2.5, 2.5)

        painter.end()

    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                local_path = url.toLocalFile()
                if os.path.isdir(local_path):
                    for root, _dirs, filenames in os.walk(local_path):
                        for fn in sorted(filenames):
                            if os.path.splitext(fn)[1].lower() in SUPPORTED_EXTENSIONS:
                                files.append(os.path.join(root, fn))
                elif os.path.isfile(local_path):
                    files.append(local_path)
        if files:
            self.files_selected.emit(files)

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton and self.isEnabled():
            files, _ = QFileDialog.getOpenFileNames(
                self,
                translator.t("dropzone_title"),
                "",
                "Media Files (*.mp3 *.wav *.m4a *.mp4 *.mkv *.avi *.flac *.ogg *.webm *.mov *.aac);;All Files (*.*)",
            )
            if files:
                self.files_selected.emit(files)
