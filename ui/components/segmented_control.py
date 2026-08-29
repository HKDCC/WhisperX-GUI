from PyQt6.QtWidgets import QWidget, QHBoxLayout, QPushButton
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QFont, QTransform
from PyQt6.QtCore import Qt, pyqtSignal, QPointF, QPropertyAnimation, pyqtProperty, QEasingCurve
from core.config_manager import config_manager

class SkewedTabButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setFixedHeight(26)
        
        # Elastic animations
        self._scale = 1.0
        self._shear = 0.0
        self.hover_anim = None
        self.hover_anim_shear = None
        
        self.setMouseTracking(True)
        
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
        self.animate_hover(1.05, 0.04)
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
        self.hover_anim.setDuration(200)
        self.hover_anim.setStartValue(self._scale)
        self.hover_anim.setEndValue(target_scale)
        self.hover_anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.hover_anim_shear = QPropertyAnimation(self, b"shear_factor")
        self.hover_anim_shear.setDuration(200)
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
        
        # Apply transformation
        transform = QTransform()
        transform.translate(cx, cy)
        transform.scale(self._scale, self._scale)
        transform.shear(self._shear, 0.0)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)
        
        skew = 6.0
        
        # Draw skewed parallelogram
        poly = QPolygonF([
            QPointF(skew + 2.0, 2.0),
            QPointF(float(w) - 2.0, 2.0),
            QPointF(float(w) - skew - 2.0, float(h) - 2.0),
            QPointF(2.0, float(h) - 2.0)
        ])
        
        is_checked = self.isChecked()
        is_hovered = self.underMouse()
        
        if not self.isEnabled():
            if theme == "light":
                bg_color = QColor("#E1E1E6")
                painter.setBrush(QBrush(bg_color))
                painter.setPen(QPen(QColor("#C1C1C8"), 1))
            else:
                bg_color = QColor("#16161B")
                painter.setBrush(QBrush(bg_color))
                painter.setPen(QPen(QColor("#252530"), 1))
        elif is_checked:
            bg_color = QColor("#F3FF00")  # Neon Yellow
            painter.setBrush(QBrush(bg_color))
            painter.setPen(QPen(QColor("#0F0F12"), 2))
        else:
            if theme == "light":
                if is_hovered:
                    bg_color = QColor("#D8D8DF")
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(QPen(QColor("#FF0055"), 1.5))  # Neon Pink
                else:
                    bg_color = QColor("#FFFFFF")
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(QPen(QColor("#A1A1A8"), 1))
            else:
                if is_hovered:
                    bg_color = QColor("#22222C")
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(QPen(QColor("#FF0055"), 1.5))  # Neon Pink
                else:
                    bg_color = QColor("#121216")
                    painter.setBrush(QBrush(bg_color))
                    painter.setPen(QPen(QColor("#3A3A4A"), 1))
                
        painter.drawPolygon(poly)
        
        # Draw small neon cyan accent notch inside active tab
        if is_checked and self.isEnabled():
            notch_color = QColor("#0088FF") if theme == "light" else QColor("#00F0FF")
            painter.setBrush(QBrush(notch_color))
            painter.setPen(Qt.PenStyle.NoPen)
            notch = QPolygonF([
                QPointF(2.0 + skew, 2.0),
                QPointF(10.0 + skew, 2.0),
                QPointF(7.0 + skew, 5.0),
                QPointF(2.0 + skew, 2.0)
            ])
            painter.drawPolygon(notch)
            
        # Draw button label
        font = QFont("Consolas", 9, QFont.Weight.Bold)
        painter.setFont(font)
        
        if not self.isEnabled():
            if theme == "light":
                painter.setPen(QColor("#A1A1A8"))
            else:
                painter.setPen(QColor("#4E4E5A"))
        elif is_checked:
            painter.setPen(QColor("#0F0F12"))
        else:
            if theme == "light":
                painter.setPen(QColor("#0F0F12") if not is_hovered else QColor("#FF0055"))
            else:
                painter.setPen(QColor("#FFFFFF") if not is_hovered else QColor("#FF0055"))
            
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class SegmentedControl(QWidget):
    currentItemChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QHBoxLayout(self)
        self.layout.setContentsMargins(4, 4, 4, 4)
        self.layout.setSpacing(4)
        self.items = []  # list of (key, text, button)
        self.current_key = None
        self.setObjectName("segmented_control")
        self.update_style()

    def addItem(self, key, text):
        btn = SkewedTabButton(text, self)
        btn.setObjectName("segment_btn")
        btn.clicked.connect(lambda: self.on_btn_clicked(key))
        self.layout.addWidget(btn)
        self.items.append((key, text, btn))
        if len(self.items) == 1:
            self.setCurrentItem(key)

    def on_btn_clicked(self, key):
        self.setCurrentItem(key)
        self.currentItemChanged.emit(key)

    def setCurrentItem(self, key):
        self.current_key = key
        for k, t, btn in self.items:
            btn.setChecked(k == key)
        self.update()

    def setItemEnabled(self, key, enabled):
        for k, t, btn in self.items:
            if k == key:
                btn.setEnabled(enabled)
                btn.update()
                break

    def update_style(self):
        # We handle button styling inside SkewedTabButton paintEvent.
        # Container style:
        theme = config_manager.get("theme_mode")
        if theme == "light":
            self.setStyleSheet("""
                QWidget#segmented_control {
                    background-color: #E6E6EB;
                    border: 2px solid #A1A1A8;
                }
            """)
        else:
            self.setStyleSheet("""
                QWidget#segmented_control {
                    background-color: #0F0F12;
                    border: 2px solid #2C2C35;
                }
            """)
