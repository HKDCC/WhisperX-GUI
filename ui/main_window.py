import os
import shutil
import subprocess
import sys
import threading
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QFileDialog,
    QListWidget,
    QListWidgetItem,
    QProgressBar,
    QLabel,
    QPushButton,
    QCheckBox,
    QTextEdit,
    QMessageBox,
    QFrame,
    QAbstractItemView,
    QApplication,
)
from PyQt6.QtCore import (
    Qt,
    QPoint,
    QRect,
    QRectF,
    QSize,
    QUrl,
    pyqtSlot,
    QThread,
    pyqtSignal,
)
from PyQt6.QtGui import (
    QIcon,
    QPainter,
    QColor,
    QBrush,
    QPen,
    QFont,
    QFontMetrics,
    QCursor,
    QDesktopServices,
    QGuiApplication,
)
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

    def __init__(self):
        super().__init__()
        self._is_running = True
        self.process = None
        self.lock = threading.Lock()

    def stop(self):
        with self.lock:
            self._is_running = False
            if self.process and self.process.poll() is None:
                if os.name == "nt":
                    try:
                        subprocess.call(
                            ["taskkill", "/F", "/T", "/PID", str(self.process.pid)],
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                        )
                    except Exception:
                        pass
                else:
                    try:
                        self.process.terminate()
                    except Exception:
                        pass

    def run(self):
        whisperx_exe = config_manager.get("whisperx_path") or "whisperx"
        resolved_exe = (
            shutil.which(whisperx_exe) if not os.path.exists(whisperx_exe) else whisperx_exe
        )

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
        cmd = [
            target_python,
            "-m",
            "pip",
            "install",
            "torch",
            "torchvision",
            "torchaudio",
            "--index-url",
            "https://download.pytorch.org/whl/cu121",
            "--upgrade",
        ]
        self.log_updated.emit("Command: " + " ".join(cmd) + "\n")

        try:
            with self.lock:
                if not self._is_running:
                    self.installer_finished.emit(False, "Stopped by user.")
                    return
                self.process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                )

            while self._is_running:
                line = self.process.stdout.readline()
                if not line and self.process.poll() is not None:
                    break
                if line:
                    self.log_updated.emit(line)

            self.process.communicate()
            rc = self.process.returncode
            with self.lock:
                self.process = None

            if not self._is_running:
                self.installer_finished.emit(False, "Stopped by user.")
            elif rc == 0:
                self.installer_finished.emit(True, "Installation completed successfully.")
            else:
                self.installer_finished.emit(
                    False, f"Installation failed with exit status: {rc}"
                )
        except Exception as e:
            self.installer_finished.emit(False, str(e))


class TactileButton(QPushButton):
    """Straight, crisp rectangular hardware button without wobble or skew."""

    def __init__(self, parent=None, variant="secondary"):
        super().__init__(parent)
        self.variant = variant  # "primary", "secondary", "ghost"
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMouseTracking(True)

    def set_variant(self, variant):
        self.variant = variant
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w = float(self.width())
        h = float(self.height())
        rect = QRectF(0.75, 0.75, w - 1.5, h - 1.5)

        is_hovered = self.underMouse()
        is_pressed = self.isDown()
        is_enabled = self.isEnabled()
        is_running = bool(self.property("running"))
        theme = config_manager.get("theme_mode")

        if not is_enabled:
            bg = QColor("#E4E1D7" if theme == "light" else "#161920")
            border = QColor("#C7C2B6" if theme == "light" else "#242834")
            fg = QColor("#9C978B" if theme == "light" else "#4C5366")
        elif self.variant == "primary" or self.objectName() == "run_btn":
            if is_running:
                bg = QColor("#DC2626" if is_pressed else ("#F87171" if is_hovered else "#EF4444"))
                border = QColor("#991B1B" if theme == "light" else "#FCA5A5")
                fg = QColor("#FFFFFF")
            else:
                bg = QColor("#D9480F" if is_pressed else ("#FF7338" if is_hovered else "#FF5C1A"))
                border = QColor("#141519" if theme == "light" else "#FF8B5E")
                fg = QColor("#FFFFFF")
        elif self.variant == "ghost":
            if theme == "light":
                bg = QColor("#E2DFD5" if is_pressed else ("#EAE6DC" if is_hovered else "transparent"))
                border = QColor("#141519" if is_hovered else "#C7C2B6")
                fg = QColor("#FF5C1A" if is_hovered else "#2B2E36")
            else:
                bg = QColor("#222733" if is_pressed else ("#1C202B" if is_hovered else "transparent"))
                border = QColor("#FF5C1A" if is_hovered else "#2A2E3A")
                fg = QColor("#E5FF2E" if is_hovered else "#A8B0BF")
        else:
            if theme == "light":
                bg = QColor("#E2DFD5" if is_pressed else ("#FAF8F3" if is_hovered else "#FFFFFF"))
                border = QColor("#FF5C1A" if is_hovered else "#18191E")
                fg = QColor("#FF5C1A" if is_hovered else "#141519")
            else:
                bg = QColor("#222733" if is_pressed else ("#1E2330" if is_hovered else "#161920"))
                border = QColor("#E5FF2E" if is_hovered else "#323846")
                fg = QColor("#E5FF2E" if is_hovered else "#F2F4F8")

        painter.setBrush(QBrush(bg))
        painter.setPen(QPen(border, 1.5))
        painter.drawRoundedRect(rect, 2.5, 2.5)

        font_size = 10 if (self.variant == "primary" or self.objectName() == "run_btn") else 9
        font_weight = QFont.Weight.Bold if (self.variant == "primary" or self.objectName() == "run_btn") else QFont.Weight.DemiBold
        font = QFont("Segoe UI", font_size, font_weight)
        painter.setFont(font)
        painter.setPen(fg)
        painter.drawText(self.rect(), Qt.AlignmentFlag.AlignCenter, self.text())
        painter.end()


class HardwareTooltip(QWidget):
    """Straight, clean architectural hover tooltip."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowFlags(Qt.WindowType.ToolTip | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_ShowWithoutActivating)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.w = 270
        self.h = 56
        self.setFixedSize(self.w, self.h)
        self.text = ""
        self.hide()

    def show_tooltip(self, text):
        self.text = text
        font_main = QFont("Segoe UI", 9)
        fm = QFontMetrics(font_main)
        self.w = 276
        text_w = self.w - 28
        bound_rect = fm.boundingRect(
            QRect(0, 0, text_w, 1000),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignLeft,
            text,
        )
        self.h = max(44, int(bound_rect.height() + 22))
        self.setFixedSize(self.w, self.h)
        self.update()
        self.show()

    def hide_tooltip(self):
        self.hide()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        w, h = float(self.width()), float(self.height())
        theme = config_manager.get("theme_mode")

        bg_color = QColor("#FFFFFF") if theme == "light" else QColor("#161920")
        border_color = QColor("#18191E") if theme == "light" else QColor("#3A4050")
        text_color = QColor("#141519") if theme == "light" else QColor("#F2F4F8")

        painter.setBrush(QBrush(bg_color))
        painter.setPen(QPen(border_color, 1.5))
        painter.drawRoundedRect(QRectF(0.75, 0.75, w - 1.5, h - 1.5), 2.5, 2.5)

        # Crisp 3px Signal Orange left accent strip
        painter.setBrush(QBrush(QColor("#FF5C1A")))
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(QRectF(1.5, 1.5, 3.0, h - 3.0))

        painter.setFont(QFont("Segoe UI", 9))
        painter.setPen(text_color)
        painter.drawText(
            QRect(14, 10, int(w) - 24, int(h) - 20),
            Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignVCenter | Qt.AlignmentFlag.AlignLeft,
            self.text,
        )
        painter.end()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        app = QApplication.instance()
        if app:
            app.setFont(QFont("Segoe UI", 10))
        self.setFont(QFont("Segoe UI", 10))
        self.resize(1100, 740)
        self.setMinimumSize(940, 660)

        icon_png_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "icon.png"
        )
        icon_ico_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "assets", "icon.ico"
        )
        if os.path.exists(icon_png_path):
            self.setWindowIcon(QIcon(icon_png_path))
        elif os.path.exists(icon_ico_path):
            self.setWindowIcon(QIcon(icon_ico_path))

        self.files = []
        self.output_dir = ""
        self._custom_output_dir = False
        self.runner = None
        self.installer = None
        self._console_expanded = True
        self._status_state = "ready"

        self.init_ui()
        self.apply_theme()
        self.update_content()
        self.update_queue_controls()
        self.install_tooltips()

        if not config_manager.cuda_available:
            self.append_console(
                "SYSTEM INFO: No NVIDIA GPU / CUDA detected. Running in CPU mode."
            )
        elif config_manager.needs_cuda_install:
            self.append_console(
                "SYSTEM INFO: NVIDIA GPU detected, but local PyTorch lacks CUDA support."
            )

    def init_ui(self):
        self.main_widget = QWidget()
        self.main_widget.setObjectName("main_widget")
        self.setCentralWidget(self.main_widget)

        main_layout = QHBoxLayout(self.main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # ----------------------------------------------------
        # LEFT PANE (Primary Workspace)
        # ----------------------------------------------------
        left_pane = QWidget()
        left_pane.setObjectName("left_pane")
        left_layout = QVBoxLayout(left_pane)
        left_layout.setContentsMargins(24, 18, 24, 18)
        left_layout.setSpacing(12)

        # 1. Top Hardware Header Strip
        header_layout = QHBoxLayout()
        header_layout.setSpacing(12)

        title_col = QVBoxLayout()
        title_col.setSpacing(2)
        self.header_title = QLabel("WHISPERX STUDIO", self)
        self.header_title.setObjectName("header_title")
        self.header_subtitle = QLabel(self)
        self.header_subtitle.setObjectName("header_subtitle")
        title_col.addWidget(self.header_title)
        title_col.addWidget(self.header_subtitle)
        header_layout.addLayout(title_col)
        header_layout.addStretch(1)

        self.gpu_badge = QLabel(self)
        self.gpu_badge.setObjectName("telemetry_badge")
        self.ffmpeg_badge = QLabel(self)
        self.ffmpeg_badge.setObjectName("telemetry_badge")
        header_layout.addWidget(self.gpu_badge)
        header_layout.addWidget(self.ffmpeg_badge)
        left_layout.addLayout(header_layout)

        # 2. Cassette Dropzone
        self.dropzone = DropZone(self)
        self.dropzone.files_selected.connect(self.add_files)
        left_layout.addWidget(self.dropzone)

        # 3. Queue Section Header + Action Buttons + Queue List
        queue_header = QHBoxLayout()
        queue_header.setSpacing(8)
        self.file_list_label = QLabel(self)
        self.file_list_label.setObjectName("section_header_label")
        queue_header.addWidget(self.file_list_label)
        queue_header.addStretch(1)

        self.add_files_btn = TactileButton(self, variant="ghost")
        self.add_files_btn.setFixedHeight(26)
        self.add_files_btn.setMinimumWidth(64)
        self.add_files_btn.clicked.connect(self.browse_add_files)

        self.remove_file_btn = TactileButton(self, variant="ghost")
        self.remove_file_btn.setFixedHeight(26)
        self.remove_file_btn.setMinimumWidth(62)
        self.remove_file_btn.clicked.connect(self.remove_selected_files)

        self.clear_files_btn = TactileButton(self, variant="ghost")
        self.clear_files_btn.setFixedHeight(26)
        self.clear_files_btn.setMinimumWidth(60)
        self.clear_files_btn.clicked.connect(self.clear_files)

        queue_header.addWidget(self.add_files_btn)
        queue_header.addWidget(self.remove_file_btn)
        queue_header.addWidget(self.clear_files_btn)
        left_layout.addLayout(queue_header)

        self.file_list = QListWidget(self)
        self.file_list.setFont(QFont("Consolas", 10))
        self.file_list.setSelectionMode(QAbstractItemView.SelectionMode.ExtendedSelection)
        self.file_list.setMinimumHeight(96)
        self.file_list.itemSelectionChanged.connect(self.update_queue_controls)
        left_layout.addWidget(self.file_list, 1)

        # 4. Output Configuration Card
        self.output_card = QFrame(self)
        self.output_card.setObjectName("surface_card")
        output_card_layout = QVBoxLayout(self.output_card)
        output_card_layout.setContentsMargins(14, 10, 14, 10)
        output_card_layout.setSpacing(8)

        # Row A: Output Directory
        dir_layout = QHBoxLayout()
        dir_layout.setSpacing(8)
        self.dir_label = QLabel(self.output_card)
        self.dir_label.setFixedWidth(86)
        self.dir_path_label = QLabel(self.output_card)
        self.dir_path_label.setMinimumWidth(140)

        self.dir_btn = TactileButton(self.output_card, variant="secondary")
        self.dir_btn.setFixedSize(68, 28)
        self.dir_btn.clicked.connect(self.change_dir)

        self.open_dir_btn = TactileButton(self.output_card, variant="secondary")
        self.open_dir_btn.setFixedSize(68, 28)
        self.open_dir_btn.clicked.connect(self.open_output_dir)

        dir_layout.addWidget(self.dir_label)
        dir_layout.addWidget(self.dir_path_label, 1)
        dir_layout.addWidget(self.dir_btn)
        dir_layout.addWidget(self.open_dir_btn)
        output_card_layout.addLayout(dir_layout)

        # Row B: Export Formats
        formats_layout = QHBoxLayout()
        formats_layout.setSpacing(10)
        self.formats_label = QLabel(self.output_card)
        self.formats_label.setFixedWidth(86)
        formats_layout.addWidget(self.formats_label)

        self.format_checkboxes = {}
        saved_formats = config_manager.get("output_formats") or ["srt"]
        for fmt in ["srt", "txt", "vtt", "tsv", "json"]:
            cb = QCheckBox(fmt.upper(), self.output_card)
            cb.setCursor(Qt.CursorShape.PointingHandCursor)
            cb.setChecked(fmt in saved_formats)
            cb.toggled.connect(lambda checked, f=fmt: self.on_format_toggled(f, checked))
            formats_layout.addWidget(cb)
            self.format_checkboxes[fmt] = cb
        formats_layout.addStretch(1)
        output_card_layout.addLayout(formats_layout)
        left_layout.addWidget(self.output_card)

        # 5. Execution & Telemetry Bar
        run_layout = QHBoxLayout()
        run_layout.setSpacing(10)

        self.status_badge = QLabel(self)
        self.status_badge.setObjectName("status_badge")
        self.status_badge.setFixedHeight(36)
        self.status_badge.setMinimumWidth(92)
        self.status_badge.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.progress_bar = QProgressBar(self)
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setFixedHeight(36)
        self.progress_bar.setFormat("IDLE // 0%")

        self.run_btn = TactileButton(self, variant="primary")
        self.run_btn.setObjectName("run_btn")
        self.run_btn.setFixedSize(184, 36)
        self.run_btn.clicked.connect(self.toggle_run)

        run_layout.addWidget(self.status_badge)
        run_layout.addWidget(self.progress_bar, 1)
        run_layout.addWidget(self.run_btn)
        left_layout.addLayout(run_layout)

        # 6. Console Telemetry Drawer
        console_header = QHBoxLayout()
        console_header.setSpacing(8)
        self.console_label = QLabel(self)
        self.console_label.setObjectName("section_header_label")
        console_header.addWidget(self.console_label)
        console_header.addStretch(1)

        self.console_clear_btn = TactileButton(self, variant="ghost")
        self.console_clear_btn.setFixedHeight(24)
        self.console_clear_btn.setMinimumWidth(68)
        self.console_clear_btn.clicked.connect(self.clear_console)

        self.console_toggle_btn = TactileButton(self, variant="ghost")
        self.console_toggle_btn.setFixedHeight(24)
        self.console_toggle_btn.setMinimumWidth(72)
        self.console_toggle_btn.clicked.connect(self.toggle_console)

        console_header.addWidget(self.console_clear_btn)
        console_header.addWidget(self.console_toggle_btn)
        left_layout.addLayout(console_header)

        self.console = QTextEdit(self)
        self.console.setObjectName("console_output")
        self.console.setFont(QFont("Consolas", 9))
        self.console.setReadOnly(True)
        self.console.setFixedHeight(112)
        left_layout.addWidget(self.console)

        # ----------------------------------------------------
        # RIGHT PANE (Parameters Sidebar)
        # ----------------------------------------------------
        self.settings_panel = SettingsPanel(self)
        self.settings_panel.language_changed.connect(self.on_language_changed)
        self.settings_panel.theme_changed.connect(self.on_theme_changed)
        self.settings_panel.install_cuda_requested.connect(self.install_pytorch_cuda)

        main_layout.addWidget(left_pane, 1)
        main_layout.addWidget(self.settings_panel)

        self.tooltip_widget = HardwareTooltip()

    def keyPressEvent(self, event):
        if event.key() in (Qt.Key.Key_Delete, Qt.Key.Key_Backspace) and self.file_list.hasFocus():
            self.remove_selected_files()
            return
        super().keyPressEvent(event)

    def install_tooltips(self):
        self.widget_descs = [
            self.dropzone,
            self.file_list,
            self.add_files_btn,
            self.remove_file_btn,
            self.clear_files_btn,
            self.dir_btn,
            self.open_dir_btn,
            self.run_btn,
            self.console_toggle_btn,
            self.console_clear_btn,
            self.settings_panel.lang_cb,
            self.settings_panel.model_cb,
            self.settings_panel.whisper_lang_cb,
            self.settings_panel.vad_switch,
            self.settings_panel.align_switch,
            self.settings_panel.diarize_switch,
            self.settings_panel.hf_token_input,
            self.settings_panel.hf_toggle_btn,
            self.settings_panel.mirror_switch,
            self.settings_panel.path_input,
            self.settings_panel.path_btn,
            self.settings_panel.install_cuda_btn,
        ]

        for cb in self.format_checkboxes.values():
            self.widget_descs.append(cb)

        for seg in (
            self.settings_panel.theme_seg,
            self.settings_panel.device_seg,
            self.settings_panel.compute_seg,
        ):
            self.widget_descs.append(seg)
            for item in seg.items:
                self.widget_descs.append(item[2])

        for w in self.widget_descs:
            w.installEventFilter(self)
            w.setMouseTracking(True)

    def get_widget_description(self, widget):
        key = None
        if widget == self.dropzone:
            key = "desc_dropzone"
        elif widget == self.file_list:
            key = "desc_file_list"
        elif widget == self.add_files_btn:
            key = "desc_add_files_btn"
        elif widget == self.remove_file_btn:
            key = "desc_remove_file_btn"
        elif widget == self.clear_files_btn:
            key = "desc_clear_files_btn"
        elif widget == self.dir_btn:
            key = "desc_dir_btn"
        elif widget == self.open_dir_btn:
            key = "desc_open_dir_btn"
        elif widget == self.run_btn:
            key = "desc_run_btn"
        elif widget == self.console_toggle_btn:
            key = "desc_console_toggle_btn"
        elif widget == self.console_clear_btn:
            key = "desc_console_clear_btn"
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
        elif widget == self.settings_panel.hf_toggle_btn:
            key = "desc_hf_toggle_btn"
        elif widget == self.settings_panel.mirror_switch:
            key = "desc_mirror_switch"
        elif widget in (self.settings_panel.path_input, self.settings_panel.path_btn):
            key = "desc_whisperx_path"
        elif widget == self.settings_panel.install_cuda_btn:
            key = "desc_install_cuda_btn"
        elif widget == self.settings_panel.model_cb:
            idx = self.settings_panel.model_cb.currentIndex()
            model_name = (
                self.settings_panel.model_cb.itemData(idx) if idx >= 0 else "large-v3"
            ) or "large-v3"
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
            for seg in (
                self.settings_panel.theme_seg,
                self.settings_panel.device_seg,
                self.settings_panel.compute_seg,
            ):
                for item in seg.items:
                    if item[2] == widget:
                        return translator.t("desc_set_value").format(val=item[1])

        return translator.t(key) if key else ""

    def eventFilter(self, watched, event):
        if event.type() == event.Type.Enter:
            desc = self.get_widget_description(watched)
            if desc:
                self.tooltip_widget.show_tooltip(desc)
                self.move_tooltip(QCursor.pos())
        elif event.type() == event.Type.MouseMove:
            if self.tooltip_widget.isVisible():
                self.move_tooltip(QCursor.pos())
        elif event.type() == event.Type.Leave:
            self.tooltip_widget.hide_tooltip()

        return super().eventFilter(watched, event)

    def move_tooltip(self, global_pos):
        offset_pos = global_pos + QPoint(14, 14)
        screen = QGuiApplication.primaryScreen()
        if screen:
            screen_geom = screen.availableGeometry()
            if offset_pos.x() + self.tooltip_widget.w > screen_geom.right():
                offset_pos.setX(global_pos.x() - self.tooltip_widget.w - 14)
            if offset_pos.y() + self.tooltip_widget.h > screen_geom.bottom():
                offset_pos.setY(global_pos.y() - self.tooltip_widget.h - 14)
            offset_pos.setX(max(screen_geom.left(), offset_pos.x()))
            offset_pos.setY(max(screen_geom.top(), offset_pos.y()))
        self.tooltip_widget.move(offset_pos)

    def closeEvent(self, event):
        for thread_attr in ("runner", "installer"):
            worker = getattr(self, thread_attr, None)
            if worker:
                for sig_name in (
                    "progress_updated",
                    "progress_percent",
                    "log_updated",
                    "transcription_finished",
                    "installer_finished",
                ):
                    sig = getattr(worker, sig_name, None)
                    if sig is not None:
                        try:
                            sig.disconnect()
                        except Exception:
                            pass
                if worker.isRunning():
                    worker.stop()
                    worker.wait(2000)
                setattr(self, thread_attr, None)
        if hasattr(self, "tooltip_widget"):
            self.tooltip_widget.hide_tooltip()
        event.accept()

    def set_ui_locked(self, locked):
        self.dropzone.setEnabled(not locked)
        self.add_files_btn.setEnabled(not locked)
        self.dir_btn.setEnabled(not locked)
        self.settings_panel.setEnabled(not locked)
        for cb in self.format_checkboxes.values():
            cb.setEnabled(not locked)
        if locked:
            self.remove_file_btn.setEnabled(False)
            self.clear_files_btn.setEnabled(False)
        else:
            self.update_queue_controls()

    def _update_status_badge_style(self):
        theme = config_manager.get("theme_mode")
        state = self._status_state
        if state in ("running", "installing"):
            bg, fg, border = "#FF5C1A", "#FFFFFF", "#FF5C1A"
        elif state == "done":
            bg, fg, border = "#16A34A", "#FFFFFF", "#16A34A"
        elif state == "error":
            bg, fg, border = "#EF4444", "#FFFFFF", "#EF4444"
        elif state == "stopped":
            bg = "#E2DFD5" if theme == "light" else "#262B36"
            fg = "#565A65" if theme == "light" else "#C2C8D4"
            border = "#8D887B" if theme == "light" else "#3A4050"
        else:
            bg = "#141519" if theme == "light" else "#1E222B"
            fg = "#E5FF2E"
            border = "#141519" if theme == "light" else "#323846"

        self.status_badge.setStyleSheet(f"""
            QLabel#status_badge {{
                background-color: {bg};
                color: {fg};
                border: 1.5px solid {border};
                border-radius: 2px;
                padding: 0 10px;
                font-family: "Consolas";
                font-size: 11px;
                font-weight: 700;
            }}
        """)

    def _update_telemetry_badges(self):
        theme = config_manager.get("theme_mode")
        base_bg = "#FAF8F3" if theme == "light" else "#161920"
        base_border = "#18191E" if theme == "light" else "#2A2E3A"
        ok_fg = "#141519" if theme == "light" else "#E5FF2E"
        warn_fg = "#C2410C" if theme == "light" else "#FF8552"

        if config_manager.torch_cuda_available:
            gpu_text = translator.t("badge_cuda_ready")
            gpu_fg = ok_fg
        elif config_manager.has_nvidia_gpu:
            gpu_text = translator.t("badge_cuda_missing")
            gpu_fg = warn_fg
        else:
            gpu_text = translator.t("badge_cpu_only")
            gpu_fg = "#565A65" if theme == "light" else "#949BA8"

        has_ffmpeg = shutil.which("ffmpeg") is not None
        ffmpeg_text = translator.t("badge_ffmpeg_ok" if has_ffmpeg else "badge_ffmpeg_missing")
        ffmpeg_fg = ok_fg if has_ffmpeg else warn_fg

        pill_tpl = (
            "background-color: {bg}; color: {fg}; border: 1px solid {bd}; "
            "border-radius: 2px; padding: 3px 8px; "
            "font-family: 'Consolas'; font-size: 10px; font-weight: 700;"
        )
        self.gpu_badge.setText(gpu_text)
        self.gpu_badge.setStyleSheet(pill_tpl.format(bg=base_bg, fg=gpu_fg, bd=base_border))
        self.ffmpeg_badge.setText(ffmpeg_text)
        self.ffmpeg_badge.setStyleSheet(pill_tpl.format(bg=base_bg, fg=ffmpeg_fg, bd=base_border))

    def apply_theme(self):
        theme = config_manager.get("theme_mode") or "light"
        app = QApplication.instance()
        if app:
            app.setStyleSheet(get_stylesheet(theme))
        self.setStyleSheet(get_stylesheet(theme))

        self.dropzone.update_style()
        self.settings_panel.update_style()

        if theme == "light":
            self.dir_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #2B2E36;")
            self.dir_path_label.setStyleSheet(
                "font-family: 'Consolas'; font-size: 11.5px; color: #141519;"
            )
            self.formats_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #2B2E36;")
        else:
            self.dir_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #949BA8;")
            self.dir_path_label.setStyleSheet(
                "font-family: 'Consolas'; font-size: 11.5px; color: #E5FF2E;"
            )
            self.formats_label.setStyleSheet("font-size: 12px; font-weight: 700; color: #949BA8;")

        self._update_status_badge_style()
        self._update_telemetry_badges()

        for btn in (
            self.add_files_btn,
            self.remove_file_btn,
            self.clear_files_btn,
            self.dir_btn,
            self.open_dir_btn,
            self.run_btn,
            self.console_clear_btn,
            self.console_toggle_btn,
        ):
            btn.update()

    def update_content(self):
        self.setWindowTitle(translator.t("title"))
        self.header_subtitle.setText(translator.t("header_subtitle"))
        self.dropzone.update_content()

        self.file_list_label.setText(
            translator.t("queue_count_fmt").format(count=len(self.files))
        )
        self.add_files_btn.setText(translator.t("add_files_btn"))
        self.remove_file_btn.setText(translator.t("remove_selected_btn"))
        self.clear_files_btn.setText(translator.t("clear_queue_btn"))

        self.dir_label.setText(translator.t("output_dir") + ":")
        self.formats_label.setText(translator.t("formats") + ":")
        self.dir_btn.setText(translator.t("change_btn"))
        self.open_dir_btn.setText(translator.t("open_dir_btn"))
        self.dir_path_label.setText(
            self.output_dir if self.output_dir else translator.t("same_as_source")
        )

        self.console_label.setText(translator.t("console_title"))
        self.console_clear_btn.setText(translator.t("clear_log_btn"))
        self.console_toggle_btn.setText(
            translator.t("toggle_console_hide" if self._console_expanded else "toggle_console_show")
        )
        self.console.setPlaceholderText(translator.t("console_placeholder"))

        self.status_badge.setText(translator.t(f"status_{self._status_state}"))
        self._update_telemetry_badges()

        is_busy = bool(
            (self.runner and self.runner.isRunning())
            or (self.installer and self.installer.isRunning())
        )
        self.run_btn.setText(translator.t("stop_btn" if is_busy else "run_btn"))

    def update_queue_controls(self):
        has_files = len(self.files) > 0
        has_selection = len(self.file_list.selectedItems()) > 0
        is_busy = bool(
            (self.runner and self.runner.isRunning())
            or (self.installer and self.installer.isRunning())
        )

        self.file_list_label.setText(
            translator.t("queue_count_fmt").format(count=len(self.files))
        )
        self.remove_file_btn.setEnabled(has_selection and not is_busy)
        self.clear_files_btn.setEnabled(has_files and not is_busy)
        self.open_dir_btn.setEnabled(bool(self.output_dir or has_files))

    def browse_add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self,
            translator.t("dropzone_title"),
            "",
            "Media Files (*.mp3 *.wav *.m4a *.mp4 *.mkv *.avi *.flac *.ogg *.webm *.mov *.aac);;All Files (*.*)",
        )
        if files:
            self.add_files(files)

    def add_files(self, files):
        for f in files:
            norm = os.path.normpath(f)
            if norm not in self.files:
                self.files.append(norm)
                parent_dir = os.path.basename(os.path.dirname(norm))
                display = f"{os.path.basename(norm)}   [{parent_dir}]" if parent_dir else os.path.basename(norm)
                item = QListWidgetItem(display)
                item.setData(Qt.ItemDataRole.UserRole, norm)
                item.setToolTip(norm)
                self.file_list.addItem(item)

        if self.files and not self._custom_output_dir and not self.output_dir:
            self.output_dir = os.path.dirname(self.files[0])
            self.dir_path_label.setText(self.output_dir)

        self.update_queue_controls()

    def remove_selected_files(self):
        selected_rows = sorted(
            {self.file_list.row(item) for item in self.file_list.selectedItems()},
            reverse=True,
        )
        if not selected_rows:
            return
        for row in selected_rows:
            item = self.file_list.takeItem(row)
            if item:
                path = item.data(Qt.ItemDataRole.UserRole)
                if path in self.files:
                    self.files.remove(path)

        if not self.files and not self._custom_output_dir:
            self.output_dir = ""
            self.dir_path_label.setText(translator.t("same_as_source"))

        self.update_queue_controls()

    def clear_files(self):
        self.files.clear()
        self.file_list.clear()
        if not self._custom_output_dir:
            self.output_dir = ""
            self.dir_path_label.setText(translator.t("same_as_source"))
        self.update_queue_controls()

    def change_dir(self):
        start_dir = self.output_dir or (os.path.dirname(self.files[0]) if self.files else "")
        directory = QFileDialog.getExistingDirectory(self, translator.t("output_dir"), start_dir)
        if directory:
            self.output_dir = os.path.normpath(directory)
            self._custom_output_dir = True
            self.dir_path_label.setText(self.output_dir)
            self.update_queue_controls()

    def open_output_dir(self):
        target = self.output_dir or (os.path.dirname(self.files[0]) if self.files else "")
        if not target:
            return
        os.makedirs(target, exist_ok=True)
        if os.name == "nt":
            try:
                os.startfile(target)
                return
            except Exception:
                pass
        QDesktopServices.openUrl(QUrl.fromLocalFile(target))

    def on_format_toggled(self, fmt, checked):
        selected = [f for f, cb in self.format_checkboxes.items() if cb.isChecked()]
        if not selected:
            cb = self.format_checkboxes[fmt]
            cb.blockSignals(True)
            cb.setChecked(True)
            cb.blockSignals(False)
            return
        config_manager.set("output_formats", selected)

    def update_formats(self):
        formats = [fmt for fmt, cb in self.format_checkboxes.items() if cb.isChecked()]
        if not formats:
            formats = ["srt"]
            self.format_checkboxes["srt"].blockSignals(True)
            self.format_checkboxes["srt"].setChecked(True)
            self.format_checkboxes["srt"].blockSignals(False)
        config_manager.set("output_formats", formats)

    def toggle_console(self):
        self._console_expanded = not self._console_expanded
        self.console.setVisible(self._console_expanded)
        self.console_toggle_btn.setText(
            translator.t("toggle_console_hide" if self._console_expanded else "toggle_console_show")
        )

    def clear_console(self):
        self.console.clear()

    def append_console(self, text):
        self.console.append(text.rstrip())

    def set_status(self, state_key, progress_text=None):
        self._status_state = state_key
        self.status_badge.setText(translator.t(f"status_{state_key}"))
        self._update_status_badge_style()
        if progress_text is not None:
            self.progress_bar.setFormat(progress_text)

    def on_language_changed(self, lang):
        self.update_content()

    def on_theme_changed(self, theme):
        self.apply_theme()

    def toggle_run(self):
        if self.runner and self.runner.isRunning():
            self.runner.stop()
            return
        if self.installer and self.installer.isRunning():
            self.installer.stop()
            return

        if not self.files:
            QMessageBox.warning(
                self, translator.t("no_files_title"), translator.t("no_files_msg")
            )
            return

        if config_manager.get("diarize"):
            token = config_manager.get_hf_token()
            if not token or not token.strip():
                QMessageBox.warning(
                    self,
                    translator.t("hf_token_warning_title"),
                    translator.t("hf_token_warning_msg"),
                )
                return

        if config_manager.get("device") == "cuda" and not config_manager.torch_cuda_available:
            title_text = "安装 GPU 加速支持" if translator.get_lang() == "zh" else "Install GPU Support"
            question_text = (
                "检测到您的系统配置有 NVIDIA 显卡，但当前运行环境（PyTorch）尚未安装 GPU 加速库。\n\n"
                "是否允许程序自动为您下载并安装 GPU 加速依赖？\n(这可能需要几分钟，取决于您的网速)"
                if translator.get_lang() == "zh"
                else "NVIDIA GPU detected, but the current PyTorch environment lacks GPU acceleration support.\n\n"
                "Would you like the program to automatically download and install GPU dependencies for you?\n"
                "(This may take a few minutes depending on your network connection)"
            )
            reply = QMessageBox.question(
                self,
                title_text,
                question_text,
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes,
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.install_pytorch_cuda()
                return
            else:
                fallback_title = "CUDA 无法使用" if translator.get_lang() == "zh" else "CUDA Unavailable"
                fallback_text = (
                    "将以 CPU 模式运行（速度较慢）。"
                    if translator.get_lang() == "zh"
                    else "Will run in CPU mode (slower speed)."
                )
                QMessageBox.warning(self, fallback_title, fallback_text)
                config_manager.set("device", "cpu")
                self.settings_panel.device_seg.setCurrentItem("cpu")
                self.settings_panel.on_device_changed("cpu")

        if not self._console_expanded:
            self.toggle_console()
        self.console.clear()

        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.set_status("running", "INITIALIZING // %p%")

        self.run_btn.setText(translator.t("stop_btn"))
        self.run_btn.setProperty("running", True)
        self.run_btn.update()

        self.set_ui_locked(True)

        out_dir = self.output_dir if self.output_dir else os.path.dirname(self.files[0])

        self.runner = WhisperRunner(config_manager, self.files, out_dir)
        self.runner.progress_updated.connect(
            self.on_progress_updated, Qt.ConnectionType.QueuedConnection
        )
        self.runner.progress_percent.connect(
            self.on_progress_percent_updated, Qt.ConnectionType.QueuedConnection
        )
        self.runner.log_updated.connect(
            self.on_log_updated, Qt.ConnectionType.QueuedConnection
        )
        self.runner.transcription_finished.connect(
            self.on_finished, Qt.ConnectionType.QueuedConnection
        )
        self.runner.finished.connect(self.runner.deleteLater)
        self.runner.start()

    def install_pytorch_cuda(self):
        if self.installer and self.installer.isRunning():
            return
        if not self._console_expanded:
            self.toggle_console()
        self.console.clear()

        self.progress_bar.setRange(0, 0)
        self.set_status("installing", "INSTALLING CUDA...")

        self.run_btn.setText(translator.t("stop_btn"))
        self.run_btn.setProperty("running", True)
        self.run_btn.update()

        self.set_ui_locked(True)

        self.installer = PyTorchCUDAInstaller()
        self.installer.progress_updated.connect(
            self.on_progress_updated, Qt.ConnectionType.QueuedConnection
        )
        self.installer.log_updated.connect(
            self.on_log_updated, Qt.ConnectionType.QueuedConnection
        )
        self.installer.installer_finished.connect(
            self.on_installer_finished, Qt.ConnectionType.QueuedConnection
        )
        self.installer.finished.connect(self.installer.deleteLater)
        self.installer.start()

    @pyqtSlot(bool, str)
    def on_installer_finished(self, success, message):
        self.set_ui_locked(False)
        self.run_btn.setProperty("running", False)
        self.run_btn.setText(translator.t("run_btn"))
        self.run_btn.update()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)
        self.installer = None

        if success:
            self.set_status("done", "CUDA READY // 100%")
            ok_title = "安装成功" if translator.get_lang() == "zh" else "Installation Successful"
            ok_text = (
                "GPU 加速依赖环境安装成功！为了应用更改并启用显卡加速，应用程序将自动重启。\n\n点击确定以重启软件。"
                if translator.get_lang() == "zh"
                else "GPU acceleration environment installed successfully! The application will restart automatically to apply changes.\n\nClick OK to restart."
            )
            QMessageBox.information(self, ok_title, ok_text)

            config_manager.set("device", "cuda")
            if getattr(sys, "frozen", False):
                subprocess.Popen([sys.executable] + sys.argv[1:])
            else:
                subprocess.Popen([sys.executable] + sys.argv)
            QApplication.quit()
        elif message == "Stopped by user.":
            self.set_status("stopped", "STOPPED // 0%")
        else:
            self.set_status("error", "INSTALL FAILED")
            err_title = "安装失败" if translator.get_lang() == "zh" else "Installation Failed"
            err_text = (
                f"GPU 环境自动安装失败，错误信息：\n{message}\n\n建议您手动在终端运行相关 pip 命令尝试解决。"
                if translator.get_lang() == "zh"
                else f"Automatic GPU environment installation failed. Error:\n{message}\n\nWe recommend running the pip command manually in a terminal."
            )
            QMessageBox.critical(self, err_title, err_text)

    @pyqtSlot(str)
    def on_progress_updated(self, text):
        self.console.append(f"Progress: {text}")
        self.progress_bar.setFormat(f"{text} // %p%")

    @pyqtSlot(int)
    def on_progress_percent_updated(self, value):
        self.progress_bar.setValue(value)

    @pyqtSlot(str)
    def on_log_updated(self, text):
        self.console.append(text.strip())

    @pyqtSlot(bool, str)
    def on_finished(self, success, msg):
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(100 if success else 0)

        self.run_btn.setText(translator.t("run_btn"))
        self.run_btn.setProperty("running", False)
        self.run_btn.update()

        self.set_ui_locked(False)

        if self.runner:
            for sig_name in (
                "progress_updated",
                "progress_percent",
                "log_updated",
                "transcription_finished",
            ):
                sig = getattr(self.runner, sig_name, None)
                if sig is not None:
                    try:
                        sig.disconnect()
                    except Exception:
                        pass
            self.runner = None

        if success:
            self.set_status("done", "COMPLETED // 100%")
            QMessageBox.information(
                self, translator.t("success_title"), translator.t("success_msg")
            )
        else:
            if msg in ["Stopped by user.", translator.t("stopped_msg")]:
                self.set_status("stopped", "STOPPED // 0%")
            else:
                self.set_status("error", "ERROR")
                lower_msg = msg.lower()
                if "out of memory" in lower_msg or "vram" in lower_msg or "cuda" in lower_msg:
                    msg += "\n\n" + translator.t("vram_error_suggestion")
                if (
                    "localentrynotfound" in lower_msg
                    or "huggingface" in lower_msg
                    or "connection" in lower_msg
                    or "timeout" in lower_msg
                ):
                    msg += "\n\n" + translator.t("hf_error_suggestion")
                QMessageBox.critical(self, translator.t("error_title"), msg)
