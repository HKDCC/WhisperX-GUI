import os
import random
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                             QFileDialog, QListWidget, QProgressBar, QLabel, 
                             QPushButton, QCheckBox, QTextEdit, QMessageBox)
from PyQt6.QtCore import Qt, QPoint, QPointF, QRectF, QPropertyAnimation, pyqtProperty, QEasingCurve, QTimer, pyqtSlot, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QPainter, QColor, QBrush, QPen, QPolygonF, QTransform, QFont, QCursor
from ui.components.dropzone import DropZone
from ui.components.settings_panel import SettingsPanel
from core.config_manager import config_manager
from core.whisper_runner import WhisperRunner
from core.translator import translator
from ui.styles import get_stylesheet

class PyTorchCUDAInstaller(QThread):
    progress_updated = pyqtSignal(str)
    log_updated = pyqtSignal(str)
    installer_finished = pyqtSignal(bool, str)

    def run(self):
        import subprocess
        import sys
        import shutil
        
        # Determine the target python interpreter to run pip
        whisperx_exe = config_manager.get("whisperx_path") or "whisperx"
        resolved_exe = shutil.which(whisperx_exe) if not os.path.exists(whisperx_exe) else whisperx_exe
        
        target_python = None
        if resolved_exe:
            dir_name = os.path.dirname(resolved_exe)
            parent_dir = os.path.dirname(dir_name)
            
            p1 = os.path.join(dir_name, "python.exe")
            p2 = os.path.join(parent_dir, "python.exe")
            
            if os.path.exists(p1):
                target_python = p1
            elif os.path.exists(p2):
                target_python = p2
                
        if not target_python:
            target_python = shutil.which("python") or sys.executable

        self.progress_updated.emit("Downloading CUDA environment...")
        self.log_updated.emit("Starting CUDA-enabled PyTorch environment installation...\n")
        self.log_updated.emit("Command: " + target_python + " -m pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121 --upgrade\n")
        
        cmd = [target_python, "-m", "pip", "install", "torch", "torchvision", "torchaudio", "--index-url", "https://download.pytorch.org/whl/cu121", "--upgrade"]
        
        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                encoding="utf-8",
                errors="replace",
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
            
            while True:
                line = process.stdout.readline()
                if not line and process.poll() is not None:
                    break
                if line:
                    self.log_updated.emit(line)
            
            process.communicate()
            if process.returncode == 0:
                self.installer_finished.emit(True, "Installation completed successfully.")
            else:
                self.installer_finished.emit(False, f"Installation failed with exit status: {process.returncode}")
        except Exception as e:
            self.installer_finished.emit(False, str(e))

class BouncyButton(QPushButton):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._scale = 1.0
        self._shear = 0.0
        self.anim = None
        self.anim_shear = None
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
        self.animate(1.06, 0.04)
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        self.animate(1.0, 0.0)
        super().leaveEvent(event)
        
    def animate(self, target_scale, target_shear):
        if self.anim:
            self.anim.stop()
            self.anim.deleteLater()
            self.anim = None
        if self.anim_shear:
            self.anim_shear.stop()
            self.anim_shear.deleteLater()
            self.anim_shear = None
            
        self.anim = QPropertyAnimation(self, b"scale_factor")
        self.anim.setDuration(250)
        self.anim.setStartValue(self._scale)
        self.anim.setEndValue(target_scale)
        self.anim.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.anim_shear = QPropertyAnimation(self, b"shear_factor")
        self.anim_shear.setDuration(250)
        self.anim_shear.setStartValue(self._shear)
        self.anim_shear.setEndValue(target_shear)
        self.anim_shear.setEasingCurve(QEasingCurve.Type.OutElastic)
        
        self.anim.start()
        self.anim_shear.start()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        cx = w / 2.0
        cy = h / 2.0
        
        transform = QTransform()
        transform.translate(cx, cy)
        transform.scale(self._scale, self._scale)
        transform.shear(self._shear, 0.0)
        transform.translate(-cx, -cy)
        painter.setTransform(transform)
        
        is_hovered = self.underMouse()
        is_pressed = self.isDown()
        
        is_run_btn = (self.objectName() == "run_btn")
        is_running = (self.property("running") == True)
        theme = config_manager.get("theme_mode")
        
        if not self.isEnabled():
            bg = QColor("#E0E0E5" if theme == "light" else "#1A1A22")
            border = QColor("#B0B0B5" if theme == "light" else "#4A4A5A")
            fg = QColor("#808085" if theme == "light" else "#6A6A78")
        elif is_run_btn:
            if is_running:
                bg = QColor("#FF0055")
                border = QColor("#0F0F12" if theme == "light" else "#FFFFFF")
                fg = QColor("#FFFFFF")
            else:
                if is_pressed:
                    bg = QColor("#FF0055")
                    border = QColor("#0F0F12" if theme == "light" else "#FFFFFF")
                    fg = QColor("#FFFFFF")
                elif is_hovered:
                    bg = QColor("#0088FF" if theme == "light" else "#00F0FF")
                    border = QColor("#0F0F12" if theme == "light" else "#FFFFFF")
                    fg = QColor("#FFFFFF" if theme == "light" else "#0F0F12")
                else:
                    bg = QColor("#F3FF00")
                    border = QColor("#0F0F12")
                    fg = QColor("#0F0F12")
        else:
            if theme == "light":
                if is_pressed:
                    bg = QColor("#F3FF00")
                    border = QColor("#0F0F12")
                    fg = QColor("#0F0F12")
                elif is_hovered:
                    bg = QColor("#D8D8DF")
                    border = QColor("#FF0055")
                    fg = QColor("#FF0055")
                else:
                    bg = QColor("#FFFFFF")
                    border = QColor("#0F0F12")
                    fg = QColor("#0F0F12")
            else:
                if is_pressed:
                    bg = QColor("#F3FF00")
                    border = QColor("#F3FF00")
                    fg = QColor("#0F0F12")
                elif is_hovered:
                    bg = QColor("#22222C")
                    border = QColor("#00F0FF")
                    fg = QColor("#00F0FF")
                else:
                    bg = QColor("#1C1C24")
                    border = QColor("#3A3A4A")
                    fg = QColor("#FFFFFF")
                
        skew = 5.0
        poly = QPolygonF([
            QPointF(skew + 2.0, 2.0),
            QPointF(float(w) - 2.0, 2.0),
            QPointF(float(w) - skew - 2.0, float(h) - 2.0),
            QPointF(2.0, float(h) - 2.0)
        ])
        
        painter.setBrush(QBrush(bg))
        border_pen = QPen(border, 3 if theme == "light" else 2)
        if not self.isEnabled():
            border_pen.setStyle(Qt.PenStyle.DashLine)
        painter.setPen(border_pen)
        painter.drawPolygon(poly)
        
        font = QFont("Consolas", 10, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(fg)
        
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class CRTOverlay(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground)
        
        # Position of the rolling tracking line (0.0 to 1.0)
        self.tracking_y = 0.0
        
        # Particles for cursor trail
        self.trail_particles = []
        self.last_pos = None
        
        # Timer for overlay animation
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.animate_overlay)
        self.timer.start(40) # ~25 FPS
        
    def animate_overlay(self):
        # Move tracking line down
        self.tracking_y += 0.004
        if self.tracking_y > 1.0:
            self.tracking_y = 0.0
            
        # Add a trail particle based on cursor position if it has moved
        global_pos = QCursor.pos()
        local_pos = self.mapFromGlobal(global_pos)
        if self.rect().contains(local_pos):
            if self.last_pos != local_pos:
                self.last_pos = local_pos
                theme = config_manager.get("theme_mode")
                color_str = "#0088FF" if theme == "light" else "#00F0FF"
                self.trail_particles.append({
                    "pos": local_pos,
                    "alpha": 255,
                    "size": random.randint(4, 7),
                    "color": QColor(color_str)
                })
            
        # Update and fade existing particles
        next_particles = []
        for p in self.trail_particles:
            p["alpha"] -= 25 # fade out over ~10 steps
            if p["alpha"] > 0:
                next_particles.append(p)
        self.trail_particles = next_particles
        
        self.update()
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)
        
        h = self.height()
        w = self.width()
        theme = config_manager.get("theme_mode")
        
        # 1. Subtle noise / flicker overlay
        flicker_alpha = random.randint(3, 7)
        if theme == "light":
            flicker_color = QColor(255, 255, 255, flicker_alpha)
        else:
            flicker_color = QColor(0, 240, 255, flicker_alpha)
        painter.fillRect(self.rect(), flicker_color)
        
        # 2. Draw CRT horizontal scan lines
        scan_alpha = 10 if theme == "light" else 16
        scanline_color = QColor(0, 0, 0, scan_alpha)
        painter.setPen(scanline_color)
        
        for y in range(0, h, 3):
            painter.drawLine(0, y, w, y)
            
        # 3. Rolling refresh tracking bar (loops top to bottom)
        bar_y = int(self.tracking_y * float(h))
        bar_height = 40
        
        # Draw translucent gradient bar
        if theme == "light":
            bar_color = QColor(0, 136, 255, 12)
        else:
            bar_color = QColor(0, 240, 255, 18)
        painter.fillRect(0, bar_y, w, bar_height, bar_color)
        
        # Center line of tracking bar
        if theme == "light":
            center_pen = QPen(QColor(0, 136, 255, 50), 2)
        else:
            center_pen = QPen(QColor(0, 240, 255, 70), 2)
        painter.setPen(center_pen)
        painter.drawLine(0, bar_y + bar_height // 2, w, bar_y + bar_height // 2)
        
        # 4. Draw fading cursor trail particles
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        painter.setPen(Qt.PenStyle.NoPen)
        for p in self.trail_particles:
            c = QColor(p["color"])
            c.setAlpha(p["alpha"])
            painter.setBrush(QBrush(c))
            sz = float(p["size"])
            px = float(p["pos"].x())
            py = float(p["pos"].y())
            # Main particle square
            painter.drawRect(QRectF(px - sz/2.0, py - sz/2.0, sz, sz))
            
            # Glow aura
            glow_c = QColor(p["color"])
            glow_c.setAlpha(int(float(p["alpha"]) * 0.25))
            painter.setBrush(QBrush(glow_c))
            painter.drawRect(QRectF(px - sz, py - sz, sz * 2.0, sz * 2.0))
            
        painter.end()


class GlitchTooltip(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.w = 260
        self.h = 80
        self.setFixedSize(self.w, self.h)
        self.text = ""
        self.subtext = "VHS MODE [PLAY]"
        self.hide()

    def show_tooltip(self, text, subtext="VHS MODE [PLAY]"):
        self.text = text
        self.subtext = subtext
        
        # Calculate dynamic size based on text metrics
        from PyQt6.QtGui import QFont, QFontMetrics
        from PyQt6.QtCore import QRect
        
        font_main = QFont("Consolas", 8, QFont.Weight.Bold)
        fm = QFontMetrics(font_main)
        
        # Bounding box width
        self.w = 260
        text_w = self.w - 30
        
        # Calculate bounding height for wrapped text
        bound_rect = fm.boundingRect(
            QRect(0, 0, text_w, 1000),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft,
            text
        )
        
        # dynamic height: subtext (20px) + spacing (10px) + text_height + bottom padding (18px)
        self.h = max(80, int(bound_rect.height() + 48))
        self.setFixedSize(self.w, self.h)
        
        self.update()
        self.show()

    def hide_tooltip(self):
        self.hide()

    def paintEvent(self, event):
        from PyQt6.QtCore import QPoint, QRect
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        theme = config_manager.get("theme_mode")
        
        # Draw skewed bubble background
        poly = QPolygonF([
            QPointF(10.0, 2.0),
            QPointF(float(w) - 2.0, 2.0),
            QPointF(float(w) - 10.0, float(h) - 2.0),
            QPointF(2.0, float(h) - 2.0)
        ])
        
        # Fill: Deep charcoal/black in dark mode, light grey/concrete in light mode
        bg_color = QColor("#FFFFFF") if theme == "light" else QColor("#0F0F12")
        painter.setBrush(QBrush(bg_color))
        
        # Border: Cyber Blue in light, Neon Pink in dark
        border_color = QColor("#0088FF") if theme == "light" else QColor("#FF0055")
        painter.setPen(QPen(border_color, 2))
        painter.drawPolygon(poly)
        
        # Draw accent line at the bottom
        accent_color = QColor("#FF0055") if theme == "light" else QColor("#00F0FF")
        painter.setPen(QPen(accent_color, 1.5))
        painter.drawLine(QPointF(15.0, float(h) - 6.0), QPointF(float(w) - 15.0, float(h) - 6.0))
        
        # Fonts
        font_main = QFont("Consolas", 8, QFont.Weight.Bold)
        font_sub = QFont("Consolas", 7)
        
        # Draw subtext
        painter.setFont(font_sub)
        subtext_color = QColor("#FF0055") if theme == "light" else QColor("#F3FF00")
        painter.setPen(subtext_color)
        painter.drawText(QPoint(15, 18), self.subtext)
        
        # Draw main text shadow (Glitch offset)
        painter.setFont(font_main)
        shadow_color = QColor("#FF0055") if theme == "light" else QColor("#00F0FF")
        painter.setPen(shadow_color)
        painter.drawText(QRect(17, 33, w - 30, h - 42), Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, self.text)
        
        # Draw main text (White / Black)
        text_color = QColor("#0F0F12") if theme == "light" else QColor("#FFFFFF")
        painter.setPen(text_color)
        painter.drawText(QRect(15, 32, w - 30, h - 42), Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft, self.text)
        
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.resize(1000, 700)
        
        # Load and set window icon (prefer PNG to bypass missing qico plugin in PyInstaller)
        icon_png_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.png')
        icon_ico_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'assets', 'icon.ico')
        if os.path.exists(icon_png_path):
            self.setWindowIcon(QIcon(icon_png_path))
        elif os.path.exists(icon_ico_path):
            self.setWindowIcon(QIcon(icon_ico_path))
        
        self.files = []
        self.output_dir = ""
        self.runner = None

        self.init_ui()
        self.apply_theme()
        self.update_content()
        self.install_glitch_tooltips()
        if not config_manager.cuda_available:
            self.console.setVisible(True)
            self.console.append("SYSTEM INFO: CUDA is not available on this system. Falling back to CPU mode.\n")

    def init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_widget")
        self.setCentralWidget(self.main_widget)
        
        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # LEFT PANE (Core operations)
        # ----------------------------------------------------
        left_pane = QWidget()
        left_pane.setObjectName("left_pane")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(30, 30, 30, 30)
        left_layout.setSpacing(18)

        # Dropzone
        self.dropzone = DropZone(self)
        self.dropzone.files_selected.connect(self.add_files)
        left_layout.addWidget(self.dropzone)

        # File List Section
        self.file_section_layout = QVBoxLayout()
        self.file_section_layout.setSpacing(6)
        self.file_list_label = QLabel(self)
        
        self.file_list = QListWidget(self)
        self.file_list.setMaximumHeight(110)
        self.file_section_layout.addWidget(self.file_list_label)
        self.file_section_layout.addWidget(self.file_list)
        left_layout.addLayout(self.file_section_layout)

        # Output Path Select
        dir_layout = QHBoxLayout()
        self.dir_label = QLabel(self)
        self.dir_path_label = QLabel(self)
        
        self.dir_btn = BouncyButton(self)
        self.dir_btn.clicked.connect(self.change_dir)
        
        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path_label)
        dir_layout.addStretch(1)
        dir_layout.addWidget(self.dir_btn)
        left_layout.addLayout(dir_layout)

        # Export Formats
        formats_layout = QHBoxLayout()
        self.formats_label = QLabel(self)
        formats_layout.addWidget(self.formats_label)
        
        self.format_checkboxes = {}
        for fmt in ["srt", "txt", "vtt", "tsv", "json"]:
            cb = QCheckBox(fmt, self)
            cb.setChecked(fmt in config_manager.get("output_formats"))
            cb.stateChanged.connect(self.update_formats)
            formats_layout.addWidget(cb)
            self.format_checkboxes[fmt] = cb
        formats_layout.addStretch(1)
        left_layout.addLayout(formats_layout)

        # Progress & Run Control
        run_layout = QHBoxLayout()
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setVisible(False)
        self.progress_bar.setRange(0, 0) # Indeterminate
        
        self.run_btn = BouncyButton(self)
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setMinimumHeight(40)
        self.run_btn.clicked.connect(self.toggle_run)
        
        run_layout.addWidget(self.progress_bar)
        run_layout.addWidget(self.run_btn)
        left_layout.addLayout(run_layout)

        # Real-time Console Log
        self.console = QTextEdit(self)
        self.console.setReadOnly(True)
        self.console.setVisible(False)
        self.console.setMaximumHeight(150)
        left_layout.addWidget(self.console)

        # ----------------------------------------------------
        # RIGHT PANE (Settings Sidebar)
        # ----------------------------------------------------
        self.settings_panel = SettingsPanel(self)
        self.settings_panel.language_changed.connect(self.on_language_changed)
        self.settings_panel.theme_changed.connect(self.on_theme_changed)

        # Combine Panes
        main_layout.addWidget(left_pane, 1)
        main_layout.addWidget(self.settings_panel)

        # CRT Scan Lines overlay widget
        self.crt_overlay = CRTOverlay(self)
        self.crt_overlay.setGeometry(0, 0, self.width(), self.height())
        
        # Glitch Tooltip widget
        self.glitch_tooltip = GlitchTooltip()

    def install_glitch_tooltips(self):
        # Dictionary of interactive controls and their respective hover tips
        # List of elements we want to watch with event filter
        self.widget_descs = [
            self.dropzone,
            self.file_list,
            self.dir_btn,
            self.run_btn,
            self.settings_panel.lang_cb,
            self.settings_panel.model_cb,
            self.settings_panel.whisper_lang_cb,
            self.settings_panel.vad_switch,
            self.settings_panel.align_switch,
            self.settings_panel.diarize_switch,
            self.settings_panel.hf_token_input,
            self.settings_panel.mirror_switch,
            self.settings_panel.path_input,
            self.settings_panel.path_btn,
        ]
        
        for fmt, cb in self.format_checkboxes.items():
            self.widget_descs.append(cb)
            
        for seg in [self.settings_panel.theme_seg, self.settings_panel.device_seg, self.settings_panel.compute_seg]:
            self.widget_descs.append(seg)
            for item in seg.items:
                self.widget_descs.append(item[2])

        for w in self.widget_descs:
            w.installEventFilter(self)
            w.setMouseTracking(True)

    def get_widget_description(self, widget):
        lang = translator.get_lang()
        # Determine the key for the widget
        key = None
        if widget == self.dropzone:
            key = "desc_dropzone"
        elif widget == self.file_list:
            key = "desc_file_list"
        elif widget == self.dir_btn:
            key = "desc_dir_btn"
        elif widget == self.run_btn:
            key = "desc_run_btn"
        elif widget == self.settings_panel.lang_cb:
            key = "desc_lang_cb"
        elif widget == self.settings_panel.whisper_lang_cb:
            key = "desc_whisper_lang_cb"
        elif widget == self.settings_panel.vad_switch:
            key = "desc_vad_switch"
        elif widget == self.settings_panel.align_switch:
            key = "desc_align_switch"
        elif widget == self.settings_panel.diarize_switch:
            key = "desc_diarize_switch"
        elif widget == self.settings_panel.hf_token_input:
            key = "desc_hf_token_input"
        elif widget == self.settings_panel.mirror_switch:
            key = "desc_mirror_switch"
        elif widget in [self.settings_panel.path_input, self.settings_panel.path_btn]:
            key = "desc_whisperx_path"
        elif widget == self.settings_panel.model_cb:
            idx = self.settings_panel.model_cb.currentIndex()
            if idx >= 0:
                model_name = self.settings_panel.model_cb.itemData(idx) or "large-v3"
            else:
                model_name = "large-v3"
            model_key = model_name.replace("-", "_")
            key_name = f"scenario_{model_key}"
            trans = translator.t(key_name)
            if trans == key_name:
                return translator.t("desc_custom_model").format(model_name=model_name)
            return trans
        elif widget == self.settings_panel.theme_seg:
            key = "desc_theme_seg"
        elif widget == self.settings_panel.device_seg:
            key = "desc_device_seg"
        elif widget == self.settings_panel.compute_seg:
            key = "desc_compute_seg"
        elif widget in self.format_checkboxes.values():
            for fmt, cb in self.format_checkboxes.items():
                if cb == widget:
                    return translator.t("desc_export_subtitle").format(fmt=fmt.upper())
        else:
            # Check segmented control buttons
            for seg in [self.settings_panel.theme_seg, self.settings_panel.device_seg, self.settings_panel.compute_seg]:
                for item in seg.items:
                    if item[2] == widget:
                        return translator.t("desc_set_value").format(val=item[1].upper())
                        
        if key:
            return translator.t(key)
        return ""

    def eventFilter(self, watched, event):
        if event.type() == event.Type.Enter:
            desc = self.get_widget_description(watched)
            if desc:
                self.glitch_tooltip.show_tooltip(desc)
                self.move_tooltip(QCursor.pos())
        elif event.type() == event.Type.MouseMove:
            if self.glitch_tooltip.isVisible():
                self.move_tooltip(QCursor.pos())
        elif event.type() == event.Type.Leave:
            self.glitch_tooltip.hide_tooltip()
            
        return super().eventFilter(watched, event)

    def move_tooltip(self, global_pos):
        offset_pos = global_pos + QPoint(15, 15)
        from PyQt6.QtGui import QGuiApplication
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            if offset_pos.x() + self.glitch_tooltip.w > screen_geom.right():
                offset_pos.setX(global_pos.x() - self.glitch_tooltip.w - 15)
            if offset_pos.y() + self.glitch_tooltip.h > screen_geom.bottom():
                offset_pos.setY(global_pos.y() - self.glitch_tooltip.h - 15)
            offset_pos.setX(max(screen_geom.left(), offset_pos.x()))
            offset_pos.setY(max(screen_geom.top(), offset_pos.y()))
        self.glitch_tooltip.move(offset_pos)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, 'crt_overlay'):
            self.crt_overlay.setGeometry(0, 0, self.width(), self.height())
            self.crt_overlay.raise_()

    def closeEvent(self, event):
        if self.runner:
            try:
                self.runner.progress_updated.disconnect()
            except Exception:
                pass
            try:
                self.runner.progress_percent.disconnect()
            except Exception:
                pass
            try:
                self.runner.log_updated.disconnect()
            except Exception:
                pass
            try:
                self.runner.transcription_finished.disconnect()
            except Exception:
                pass
            if self.runner.isRunning():
                self.runner.stop()
                self.runner.wait(2000)
            self.runner = None
        event.accept()

    def set_ui_locked(self, locked):
        self.dropzone.setEnabled(not locked)
        self.dir_btn.setEnabled(not locked)
        self.settings_panel.setEnabled(not locked)
        for cb in self.format_checkboxes.values():
            cb.setEnabled(not locked)

    def apply_theme(self):
        theme = config_manager.get("theme_mode")
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme))
        self.setStyleSheet(get_stylesheet(theme))
        
        self.dropzone.update_style()
        self.settings_panel.update_style()
        
        # Stylize file section and output directory label neon aesthetics
        if theme == "light":
            self.file_list_label.setStyleSheet("font-weight: 600; color: #0F0F12; font-family: 'Consolas', monospace; text-transform: uppercase;")
            self.dir_path_label.setStyleSheet("color: #0088FF; font-family: 'Consolas', monospace;")
            self.dir_label.setStyleSheet("color: #0F0F12; font-family: 'Consolas', monospace;")
        else:
            self.file_list_label.setStyleSheet("font-weight: 600; color: #FFFFFF; font-family: 'Consolas', monospace; text-transform: uppercase;")
            self.dir_path_label.setStyleSheet("color: #00F0FF; font-family: 'Consolas', monospace;")
            self.dir_label.setStyleSheet("color: #FFFFFF; font-family: 'Consolas', monospace;")

    def update_content(self):
        self.setWindowTitle(translator.t("title"))
        self.dropzone.update_content()
        self.file_list_label.setText(translator.t("files_to_process"))
        self.dir_label.setText(translator.t("output_dir") + ":")
        self.formats_label.setText(translator.t("formats") + ":")
        self.dir_btn.setText(translator.t("change_btn"))
        self.console.setPlaceholderText(translator.t("console_placeholder"))
        
        if not self.files:
            self.dir_path_label.setText(translator.t("same_as_source"))
        else:
            self.dir_path_label.setText(self.output_dir if self.output_dir else translator.t("same_as_source"))
            
        if self.runner and self.runner.isRunning():
            self.run_btn.setText(translator.t("stop_btn"))
        else:
            self.run_btn.setText(translator.t("run_btn"))

    def on_language_changed(self, lang):
        self.update_content()

    def on_theme_changed(self, theme):
        self.apply_theme()

    def add_files(self, files):
        for f in files:
            if f not in self.files:
                self.files.append(f)
                self.file_list.addItem(os.path.basename(f))
        
        if self.files and not self.output_dir:
            self.output_dir = os.path.dirname(self.files[0])
            self.dir_path_label.setText(self.output_dir)

    def change_dir(self):
        directory = QFileDialog.getExistingDirectory(self, translator.t("output_dir"))
        if directory:
            self.output_dir = directory
            self.dir_path_label.setText(directory)

    def update_formats(self):
        formats = [fmt for fmt, cb in self.format_checkboxes.items() if cb.isChecked()]
        config_manager.set("output_formats", formats)

    def toggle_run(self):
        if self.runner and self.runner.isRunning():
            self.runner.stop()
            return

        if not self.files:
            QMessageBox.warning(self, translator.t("no_files_title"), translator.t("no_files_msg"))
            return

        if config_manager.get("diarize"):
            token = config_manager.get_hf_token()
            if not token or not token.strip():
                QMessageBox.warning(
                    self,
                    translator.t("hf_token_warning_title"),
                    translator.t("hf_token_warning_msg")
                )
                return

        # Check if they selected CUDA, but PyTorch local environment doesn't support CUDA
        try:
            import torch
            local_cuda_ok = torch.cuda.is_available()
        except ImportError:
            local_cuda_ok = False
            
        if config_manager.get("device") == "cuda" and not local_cuda_ok:
            title_text = "安装 GPU 加速支持" if translator.get_lang() == "zh" else "Install GPU Support"
            question_text = (
                "检测到您的系统配置有 NVIDIA 显卡，但当前运行环境（PyTorch）尚未安装 GPU 加速库。\n\n"
                "是否允许程序自动为您下载并安装 GPU 加速依赖？\n(这可能需要几分钟，取决于您的网速)"
                if translator.get_lang() == "zh" else
                "NVIDIA GPU detected, but the current PyTorch environment lacks GPU acceleration support.\n\n"
                "Would you like the program to automatically download and install GPU dependencies for you?\n"
                "(This may take a few minutes depending on your network connection)"
            )
            reply = QMessageBox.question(
                self,
                title_text,
                question_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.install_pytorch_cuda()
                return
            else:
                fallback_title = "CUDA 无法使用" if translator.get_lang() == "zh" else "CUDA Unavailable"
                fallback_text = "将以 CPU 模式运行（速度较慢）。" if translator.get_lang() == "zh" else "Will run in CPU mode (slower speed)."
                QMessageBox.warning(self, fallback_title, fallback_text)
                config_manager.set("device", "cpu")
                self.settings_panel.device_seg.setCurrentItem("cpu")

        self.console.setVisible(True)
        self.console.clear()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        
        self.run_btn.setText(translator.t("stop_btn"))
        self.run_btn.setProperty("running", True)
        self.run_btn.style().unpolish(self.run_btn)
        self.run_btn.style().polish(self.run_btn)

        self.set_ui_locked(True)

        out_dir = self.output_dir if self.output_dir else os.path.dirname(self.files[0])

        self.runner = WhisperRunner(config_manager, self.files, out_dir)
        self.runner.progress_updated.connect(self.on_progress_updated, Qt.ConnectionType.QueuedConnection)
        self.runner.progress_percent.connect(self.on_progress_percent_updated, Qt.ConnectionType.QueuedConnection)
        self.runner.log_updated.connect(self.on_log_updated, Qt.ConnectionType.QueuedConnection)
        self.runner.transcription_finished.connect(self.on_finished, Qt.ConnectionType.QueuedConnection)
        self.runner.finished.connect(self.runner.deleteLater)
        self.runner.start()

    def install_pytorch_cuda(self):
        self.console.setVisible(True)
        self.console.clear()
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)
        self.progress_bar.setFormat("Installing GPU dependencies... %p%")
        
        self.run_btn.setText(translator.t("stop_btn"))
        self.run_btn.setProperty("running", True)
        self.run_btn.style().unpolish(self.run_btn)
        self.run_btn.style().polish(self.run_btn)
        
        self.set_ui_locked(True)
        
        self.installer = PyTorchCUDAInstaller()
        self.installer.progress_updated.connect(self.on_progress_updated, Qt.ConnectionType.QueuedConnection)
        self.installer.log_updated.connect(self.on_log_updated, Qt.ConnectionType.QueuedConnection)
        self.installer.installer_finished.connect(self.on_installer_finished, Qt.ConnectionType.QueuedConnection)
        self.installer.finished.connect(self.installer.deleteLater)
        self.installer.start()

    @pyqtSlot(bool, str)
    def on_installer_finished(self, success, message):
        self.set_ui_locked(False)
        self.run_btn.setProperty("running", False)
        self.run_btn.setText(translator.t("run_btn"))
        self.run_btn.style().unpolish(self.run_btn)
        self.run_btn.style().polish(self.run_btn)
        self.progress_bar.setVisible(False)
        
        if success:
            ok_title = "安装成功" if translator.get_lang() == "zh" else "Installation Successful"
            ok_text = (
                "GPU 加加速依赖环境安装成功！为了应用更改并启用显卡加速，应用程序将自动重启。\n\n点击确定以重启软件。"
                if translator.get_lang() == "zh" else
                "GPU acceleration environment installed successfully! To apply changes and enable GPU acceleration, the application will restart automatically.\n\nClick OK to restart."
            )
            QMessageBox.information(self, ok_title, ok_text)
            
            # Save setting so it loads CUDA on restart
            config_manager.set("device", "cuda")
            
            # Restart the application
            import subprocess
            import sys
            from PyQt6.QtWidgets import QApplication
            
            if getattr(sys, 'frozen', False):
                # Running as compiled binary
                subprocess.Popen([sys.executable] + sys.argv[1:])
            else:
                # Running as python script
                subprocess.Popen([sys.executable] + sys.argv)
            
            QApplication.quit()
        else:
            err_title = "安装失败" if translator.get_lang() == "zh" else "Installation Failed"
            err_text = (
                f"GPU 环境自动安装失败，错误信息：\n{message}\n\n建议您手动在终端运行相关 pip 命令尝试解决。"
                if translator.get_lang() == "zh" else
                f"Automatic GPU environment installation failed. Error:\n{message}\n\nWe recommend you run the pip command manually in terminal to solve it."
            )
            QMessageBox.critical(self, err_title, err_text)

    @pyqtSlot(str)
    def on_progress_updated(self, text):
        self.console.append(f"Progress: {text}")
        self.progress_bar.setFormat(f"{text} %p%")

    @pyqtSlot(int)
    def on_progress_percent_updated(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(str)
    def on_log_updated(self, text):
        self.console.append(text.strip())

    @pyqtSlot(bool, str)
    def on_finished(self, success, msg):
        self.progress_bar.setVisible(False)
        
        self.run_btn.setText(translator.t("run_btn"))
        self.run_btn.setProperty("running", False)
        self.run_btn.style().unpolish(self.run_btn)
        self.run_btn.style().polish(self.run_btn)
        
        self.set_ui_locked(False)
        
        if self.runner:
            try:
                self.runner.progress_updated.disconnect()
            except Exception:
                pass
            try:
                self.runner.progress_percent.disconnect()
            except Exception:
                pass
            try:
                self.runner.log_updated.disconnect()
            except Exception:
                pass
            try:
                self.runner.transcription_finished.disconnect()
            except Exception:
                pass
            self.runner = None
        
        if success:
            QMessageBox.information(self, translator.t("success_title"), translator.t("success_msg"))
        else:
            if msg not in ["Stopped by user.", translator.t("stopped_msg")]:
                lower_msg = msg.lower()
                if "out of memory" in lower_msg or "vram" in lower_msg or "cuda" in lower_msg:
                    msg += "\n\n" + translator.t("vram_error_suggestion")
                if "localentrynotfound" in lower_msg or "huggingface" in lower_msg or "connection" in lower_msg or "timeout" in lower_msg:
                    msg += "\n\n" + translator.t("hf_error_suggestion")
                QMessageBox.critical(self, translator.t("error_title"), msg)
