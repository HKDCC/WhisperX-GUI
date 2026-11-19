from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, pyqtProperty, QEasingCurve, QRectF, QPointF
from core.config_manager import config_manager


class IOSSwitch(QAbstractButton):
    """Straight, tactile cassette-hardware toggle switch."""

    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(46, 22)
        self.setCursor(Qt.CursorShape.PointingHandCursor)

        self._thumb_position = 0.0
        self.anim = None

        self.clicked.connect(self.on_clicked)
        self.setMouseTracking(True)

    def on_clicked(self):
        self.checkedChanged.emit(self.isChecked())
        self.animate_thumb()

    def setChecked(self, checked):
        super().setChecked(bool(checked))
        self._thumb_position = 1.0 if checked else 0.0
        self.update()

    def animate_thumb(self):
        target = 1.0 if self.isChecked() else 0.0
        if self.anim:
            self.anim.stop()
            self.anim.deleteLater()
            self.anim = None
        self.anim = QPropertyAnimation(self, b"thumb_position")
        self.anim.setDuration(120)
        self.anim.setStartValue(self._thumb_position)
        self.anim.setEndValue(target)
        self.anim.setEasingCurve(QEasingCurve.Type.OutCubic)
        self.anim.start()

    @pyqtProperty(float)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    def enterEvent(self, event):
        self.update()
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.update()
        super().leaveEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        theme = config_manager.get("theme_mode")
        checked = self.isChecked()
        hovered = self.underMouse()
        enabled = self.isEnabled()

        if not enabled:
            track_bg = QColor("#E2DFD5" if theme == "light" else "#161920")
            track_border = QColor("#C2BDB0" if theme == "light" else "#2A2E3A")
            thumb_bg = QColor("#ACA79B" if theme == "light" else "#3A404E")
            thumb_border = track_border
        elif checked:
            track_bg = QColor("#FF5C1A")
            track_border = QColor("#141519" if theme == "light" else "#FF8552")
            thumb_bg = QColor("#FFFFFF")
            thumb_border = QColor("#141519" if theme == "light" else "#FFFFFF")
        else:
            if theme == "light":
                track_bg = QColor("#DEDAD0" if not hovered else "#D4CFC3")
                track_border = QColor("#141519" if hovered else "#8D887B")
                thumb_bg = QColor("#FFFFFF")
                thumb_border = QColor("#141519")
            else:
                track_bg = QColor("#14171E" if not hovered else "#1E222B")
                track_border = QColor("#565E73" if hovered else "#323846")
                thumb_bg = QColor("#949BA8" if not hovered else "#E2E6EE")
                thumb_border = QColor("#949BA8" if not hovered else "#E2E6EE")

        # Outer straight housing
        outer_rect = QRectF(1.0, 1.0, w - 2.0, h - 2.0)
        painter.setBrush(QBrush(track_bg))
        painter.setPen(QPen(track_border, 1.5))
        painter.drawRoundedRect(outer_rect, 2.5, 2.5)

        # Subtle hardware status dot inside track
        painter.setPen(Qt.PenStyle.NoPen)
        if checked and enabled:
            painter.setBrush(QBrush(QColor("#E5FF2E")))
            painter.drawEllipse(QPointF(10.0, h / 2.0), 2.0, 2.0)
        elif not checked and enabled:
            painter.setBrush(QBrush(QColor("#8D887B" if theme == "light" else "#484F63")))
            painter.drawEllipse(QPointF(w - 10.0, h / 2.0), 2.0, 2.0)

        # Sliding rectangular rocker thumb
        margin = 3.5
        thumb_w = 18.0
        thumb_h = h - margin * 2.0
        start_x = margin
        end_x = w - thumb_w - margin
        x_pos = start_x + (end_x - start_x) * self._thumb_position

        thumb_rect = QRectF(x_pos, margin, thumb_w, thumb_h)
        painter.setBrush(QBrush(thumb_bg))
        painter.setPen(QPen(thumb_border, 1.0))
        painter.drawRoundedRect(thumb_rect, 1.5, 1.5)

        # Vertical tactile grip notch on thumb
        grip_color = QColor("#FF5C1A" if checked else ("#8D887B" if theme == "light" else "#14171E"))
        if not enabled:
            grip_color = QColor("#7A7E8A")
        painter.setPen(QPen(grip_color, 1.5))
        cx = x_pos + thumb_w / 2.0
        painter.drawLine(QPointF(cx, margin + 3.5), QPointF(cx, margin + thumb_h - 3.5))

        painter.end()

    def sizeHint(self):
        return QSize(46, 22)
