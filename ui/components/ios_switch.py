from PyQt6.QtWidgets import QAbstractButton
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QTransform
from PyQt6.QtCore import Qt, QSize, pyqtSignal, QPropertyAnimation, pyqtProperty, QPointF, QEasingCurve
from core.config_manager import config_manager

class IOSSwitch(QAbstractButton):
    checkedChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setCheckable(True)
        self.setFixedSize(54, 26)
        
        # Lever sliding thumb animation (ratio from 0.0 to 1.0)
        self._thumb_position = 0.0
        
        # Hover animation parameters
        self._scale = 1.0
        self._shear = 0.0
        self.hover_anim = None
        self.hover_anim_shear = None
        self.anim = None
        
        self.clicked.connect(self.on_clicked)
        self.setMouseTracking(True)
        
    def on_clicked(self):
        self.checkedChanged.emit(self.isChecked())
        self.animate_thumb()

    def setChecked(self, checked):
        super().setChecked(checked)
        self._thumb_position = 1.0 if checked else 0.0
        self.update()

    def animate_thumb(self):
        target = 1.0 if self.isChecked() else 0.0
        if self.anim:
            self.anim.stop()
            self.anim.deleteLater()
            self.anim = None
        self.anim = QPropertyAnimation(self, b"thumb_position")
        self.anim.setDuration(150)
        self.anim.setEndValue(target)
        self.anim.start()

    @pyqtProperty(float)
    def thumb_position(self):
        return self._thumb_position

    @thumb_position.setter
    def thumb_position(self, pos):
        self._thumb_position = pos
        self.update()

    @pyqtProperty(float)
    def scale_factor(self):
        return self._scale

    @scale_factor.setter
    def scale_factor(self, s):
        self._scale = s
        self.update()

    @pyqtProperty(float)
    def shear_factor(self):
        return self._shear

    @shear_factor.setter
    def shear_factor(self, s):
        self._shear = s
        self.update()

    def enterEvent(self, event):
        self.animate_hover(1.08, 0.05)
        super().enterEvent(event)

    def leaveEvent(self, event):
        self.animate_hover(1.0, 0.0)
        super().leaveEvent(event)

    def animate_hover(self, target_scale, target_shear):
        if self.hover_anim:
            self.hover_anim.stop()
            self.hover_anim.deleteLater()
            self.hover_anim = None
        if self.hover_anim_shear:
            self.hover_anim_shear.stop()
            self.hover_anim_shear.deleteLater()
            self.hover_anim_shear = None
            
        self.hover_anim = QPropertyAnimation(self, b"scale_factor")
        self.hover_anim.setDuration(250)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(target_scale)
        self.hover_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.hover_anim_shear = QPropertyAnimation(self, b"shear_factor")
        self.hover_anim_shear.setDuration(250)
        self.hover_anim_shear.setStartValue(self._shear)
        self.hover_anim_shear.setEndValue(target_shear)
        self.hover_anim_shear.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.hover_anim.start()
        self.hover_anim_shear.start()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = h / 2.0
        theme = config_manager.get("theme_mode")
        
        # Apply elastic hover transformation
        transform = QTransform()
        transform.translate(cx, cy)
        transform.scale(self._scale, self._scale)
        transform.shear(self._shear, 0.0)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)
        
        # Draw mechanical slot housing (dark steel charcoal or light gray concrete)
        bg_color = QColor("#D8D8DF") if theme == "light" else QColor("#121216")
        painter.setBrush(QBrush(bg_color))
        
        # Border color changes depending on checked state (Neon Yellow/Neon Pink)
        if theme == "light":
            border_color = QColor("#0088FF") if self.isChecked() else QColor("#FF0055")
        else:
            border_color = QColor("#00F0FF") if self.isChecked() else QColor("#FF0055")
        painter.setPen(QPen(border_color, 2))
        
        # Skewed outer slot polygon
        poly = QPolygonF([
            QPointF(4.0, 2.0),
            QPointF(float(w) - 2.0, 2.0),
            QPointF(float(w) - 4.0, float(h) - 2.0),
            QPointF(2.0, float(h) - 2.0)
        ])
        painter.drawPolygon(poly)
        
        # Draw small neon indicator lights
        slot_y = h / 2.0
        
        # Off light: Glows neon pink when unchecked
        painter.setPen(Qt.PenStyle.NoPen)
        if not self.isChecked():
            painter.setBrush(QBrush(QColor("#FF0055")))
        else:
            painter.setBrush(QBrush(QColor("#E6E6EB") if theme == "light" else QColor("#400010")))
        painter.drawEllipse(QPointF(10.0, slot_y), 3.5, 3.5)
        
        # On light: Glows neon yellow when checked
        if self.isChecked():
            painter.setBrush(QBrush(QColor("#F3FF00")))
        else:
            painter.setBrush(QBrush(QColor("#E6E6EB") if theme == "light" else QColor("#404000")))
        painter.drawEllipse(QPointF(float(w) - 10.0, slot_y), 3.5, 3.5)
        
        # Draw physical lever handle
        margin = 3
        lever_w = 18.0
        lever_h = float(h - (margin * 2))
        
        start_x = float(margin + 2)
        end_x = float(w) - lever_w - float(margin + 2)
        x_pos = start_x + (end_x - start_x) * self._thumb_position
        
        # Draw lever base
        if theme == "light":
            lever_bg = QColor("#FFFFFF")
            lever_border = QColor("#0F0F12")
        else:
            lever_bg = QColor("#2C2C38") if not self.isChecked() else QColor("#4A4A5E")
            lever_border = QColor("#FFFFFF") if not self.isChecked() else QColor("#F3FF00")
            
        painter.setBrush(QBrush(lever_bg))
        painter.setPen(QPen(lever_border, 1.5))
        
        lever_poly = QPolygonF([
            QPointF(x_pos + 2.0, float(margin)),
            QPointF(x_pos + lever_w, float(margin)),
            QPointF(x_pos + lever_w - 2.0, float(margin) + lever_h),
            QPointF(x_pos, float(margin) + lever_h)
        ])
        painter.drawPolygon(lever_poly)
        
        # Center neon pin accent line on the lever
        if theme == "light":
            pin_color = QColor("#0088FF") if self.isChecked() else QColor("#FF0055")
        else:
            pin_color = QColor("#F3FF00") if self.isChecked() else QColor("#FF0055")
            
        painter.setPen(QPen(pin_color, 2))
        painter.drawLine(
            QPointF(x_pos + lever_w / 2.0, float(margin) + 3.0),
            QPointF(x_pos + lever_w / 2.0, float(margin) + lever_h - 3.0)
        )
        
        painter.end()

    def sizeHint(self):
        return QSize(54, 26)
