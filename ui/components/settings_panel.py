from PyQt6.QtWidgets import QFrame, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox, QPushButton
from PyQt6.QtCore import pyqtSignal, Qt, QPointF, QSize, QRectF
from PyQt6.QtGui import QPainter, QColor, QBrush, QPen, QPolygonF, QFont
from core.config_manager import config_manager
from core.translator import translator
from ui.components.ios_switch import IOSSwitch
from ui.components.segmented_control import SegmentedControl

class TapeLabel(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setContentsMargins(12, 6, 12, 6)
        
    def sizeHint(self):
        fm = self.fontMetrics()
        text_w = fm.horizontalAdvance(self.text())
        text_h = fm.height()
        return QSize(int(text_w + 32), int(text_h + 12))
        
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w = float(self.width())
        h = float(self.height())
        
        painter.save()
        
        # Pivot around center
        cx = w / 2.0
        cy = h / 2.0
        painter.translate(cx, cy)
        
        # Stable rotation based on label text so it doesn't jitter
        text_hash = hash(self.text() or "")
        angle = -2.5 if text_hash % 2 == 0 else 2.5
        painter.rotate(angle)
        painter.translate(-cx, -cy)
        
        # Draw the tape background
        margin_x = 4.0
        margin_y = 2.0
        tape_rect = QRectF(margin_x, margin_y, w - 2.0 * margin_x, h - 2.0 * margin_y)
        
        # Masking tape colors
        tape_color = QColor("#FDF9E2") # off-white / light yellow textured
        painter.setBrush(QBrush(tape_color))
        painter.setPen(QPen(QColor("#D6D0BC"), 1))
        painter.drawRect(tape_rect)
        
        # Subtle torn lines at edges
        painter.setPen(QPen(QColor("#C4BEAA"), 1.5))
        painter.drawLine(QPointF(margin_x + 1.0, margin_y + 2.0), QPointF(margin_x + 1.0, margin_y + h - 4.0))
        painter.drawLine(QPointF(w - margin_x - 1.0, margin_y + 2.0), QPointF(w - margin_x - 1.0, margin_y + h - 4.0))
        
        # Font styling for handwritten marker text
        font = QFont("Comic Sans MS" if "Comic Sans MS" in QFont().family() else "Consolas", 8, QFont.Weight.Bold)
        painter.setFont(font)
        painter.setPen(QColor("#0F0F12")) # always dark handwritten ink
        
        painter.drawText(tape_rect, Qt.AlignmentFlag.AlignCenter, self.text())
        
        painter.restore()
        painter.end()


class SettingsPanel(QFrame):
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_panel")
        self.setFixedWidth(330)

        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(20, 20, 20, 20)
        self.v_layout.setSpacing(12)

        # Panel Title
        self.title_label = QLabel(self)
        self.title_label.setObjectName("panel_title")
        self.title_label.setFixedHeight(35)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.v_layout.addWidget(self.title_label)

        # ----------------------------------------------------
        # GENERAL SETTINGS
        # ----------------------------------------------------
        self.general_title = QLabel(self)
        self.general_title.setObjectName("section_title")
        self.v_layout.addWidget(self.general_title)

        # UI Language
        self.lang_layout = QHBoxLayout()
        self.lang_label = TapeLabel(self)
        self.lang_cb = QComboBox(self)
        self.lang_cb.addItems(["简体中文", "English"])
        self.lang_cb.setCurrentText("English" if config_manager.get("ui_language") == "en" else "简体中文")
        self.lang_cb.currentTextChanged.connect(self.on_lang_changed)
        self.lang_layout.addWidget(self.lang_label)
        self.lang_layout.addStretch(1)
        self.lang_layout.addWidget(self.lang_cb)
        self.v_layout.addLayout(self.lang_layout)

        # Theme Mode
        self.theme_layout = QHBoxLayout()
        self.theme_label = TapeLabel(self)
        self.theme_seg = SegmentedControl(self)
        self.theme_seg.addItem("light", "Light")
        self.theme_seg.addItem("dark", "Dark")
        self.theme_seg.setCurrentItem(config_manager.get("theme_mode"))
        self.theme_seg.currentItemChanged.connect(self.on_theme_changed)
        self.theme_layout.addWidget(self.theme_label)
        self.theme_layout.addStretch(1)
        self.theme_layout.addWidget(self.theme_seg)
        self.v_layout.addLayout(self.theme_layout)

        # Divider
        self.divider1 = QFrame(self)
        self.divider1.setFrameShape(QFrame.Shape.HLine)
        self.v_layout.addWidget(self.divider1)

        # ----------------------------------------------------
        # ADVANCED (WHISPER) SETTINGS
        # ----------------------------------------------------
        self.advanced_title = QLabel(self)
        self.advanced_title.setObjectName("section_title")
        self.v_layout.addWidget(self.advanced_title)

        # WhisperX Path Setting
        self.path_layout = QHBoxLayout()
        self.path_label = TapeLabel(self)
        self.path_input = QLineEdit(self)
        self.path_input.setText(config_manager.get("whisperx_path"))
        self.path_input.textChanged.connect(lambda t: config_manager.set("whisperx_path", t))
        self.path_btn = QPushButton("...", self)
        self.path_btn.setFixedWidth(30)
        self.path_btn.clicked.connect(self.browse_whisperx_path)
        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_input)
        self.path_layout.addWidget(self.path_btn)
        self.v_layout.addLayout(self.path_layout)

        # Whisper Model Selection
        self.model_layout = QHBoxLayout()
        self.model_label = TapeLabel(self)
        self.model_cb = QComboBox(self)
        self.model_cb.setObjectName("model_cb")
        self.update_models_list()
        self.model_cb.currentTextChanged.connect(self.on_model_changed)
        
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addStretch(1)
        self.model_layout.addWidget(self.model_cb)
        self.v_layout.addLayout(self.model_layout)

        # Whisper Language
        self.whisper_lang_layout = QHBoxLayout()
        self.whisper_lang_label = TapeLabel(self)
        self.whisper_lang_cb = QComboBox(self)
        self.whisper_lang_cb.setObjectName("whisper_lang_cb")
        self.update_whisper_languages()
        self.whisper_lang_cb.currentIndexChanged.connect(self.on_whisper_lang_changed)
        self.whisper_lang_layout.addWidget(self.whisper_lang_label)
        self.whisper_lang_layout.addStretch(1)
        self.whisper_lang_layout.addWidget(self.whisper_lang_cb)
        self.v_layout.addLayout(self.whisper_lang_layout)

        # Device
        self.device_layout = QHBoxLayout()
        self.device_label = TapeLabel(self)
        self.device_seg = SegmentedControl(self)
        self.device_seg.addItem("cuda", "CUDA")
        self.device_seg.addItem("cpu", "CPU")
        self.device_seg.setCurrentItem(config_manager.get("device"))
        self.device_seg.currentItemChanged.connect(self.on_device_changed)
        self.device_layout.addWidget(self.device_label)
        self.device_layout.addStretch(1)
        self.device_layout.addWidget(self.device_seg)
        self.v_layout.addLayout(self.device_layout)
        self.device_seg.setItemEnabled("cuda", config_manager.cuda_available)

        # CUDA warning label
        self.cuda_warning_label = QLabel(self)
        self.cuda_warning_label.setWordWrap(True)
        self.cuda_warning_label.setStyleSheet("color: #FF5500; font-size: 10px; font-family: 'Consolas', 'Microsoft YaHei'; margin-top: 2px; margin-bottom: 5px;")
        self.cuda_warning_label.setObjectName("cuda_warning_label")
        self.v_layout.addWidget(self.cuda_warning_label)
        self.cuda_warning_label.setVisible(not config_manager.cuda_available and config_manager.has_nvidia_gpu)

        # Compute Type
        self.compute_layout = QHBoxLayout()
        self.compute_label = TapeLabel(self)
        self.compute_seg = SegmentedControl(self)
        self.compute_seg.addItem("float16", "float16")
        self.compute_seg.addItem("int8", "int8")
        self.compute_seg.setCurrentItem(config_manager.get("compute_type"))
        self.compute_seg.currentItemChanged.connect(lambda t: config_manager.set("compute_type", t))
        self.compute_layout.addWidget(self.compute_label)
        self.compute_layout.addStretch(1)
        self.compute_layout.addWidget(self.compute_seg)
        self.v_layout.addLayout(self.compute_layout)

        # Divider
        self.divider2 = QFrame(self)
        self.divider2.setFrameShape(QFrame.Shape.HLine)
        self.v_layout.addWidget(self.divider2)

        # VAD Toggle
        self.vad_layout = QHBoxLayout()
        self.vad_label = TapeLabel(self)
        self.vad_switch = IOSSwitch(self)
        self.vad_switch.setChecked(config_manager.get("vad_filter"))
        self.vad_switch.checkedChanged.connect(lambda s: config_manager.set("vad_filter", s))
        self.vad_layout.addWidget(self.vad_label)
        self.vad_layout.addStretch(1)
        self.vad_layout.addWidget(self.vad_switch)
        self.v_layout.addLayout(self.vad_layout)

        # Alignment Toggle
        self.align_layout = QHBoxLayout()
        self.align_label = TapeLabel(self)
        self.align_switch = IOSSwitch(self)
        self.align_switch.setChecked(config_manager.get("align"))
        self.align_switch.checkedChanged.connect(lambda s: config_manager.set("align", s))
        self.align_layout.addWidget(self.align_label)
        self.align_layout.addStretch(1)
        self.align_layout.addWidget(self.align_switch)
        self.v_layout.addLayout(self.align_layout)

        # Diarization Toggle
        self.diarize_layout = QHBoxLayout()
        self.diarize_label = TapeLabel(self)
        self.diarize_switch = IOSSwitch(self)
        self.diarize_switch.setChecked(config_manager.get("diarize"))
        self.diarize_switch.checkedChanged.connect(self.toggle_hf_token)
        self.diarize_switch.checkedChanged.connect(lambda s: config_manager.set("diarize", s))
        self.diarize_layout.addWidget(self.diarize_label)
        self.diarize_layout.addStretch(1)
        self.diarize_layout.addWidget(self.diarize_switch)
        self.v_layout.addLayout(self.diarize_layout)

        # HF Token Input
        self.hf_token_input = QLineEdit(self)
        self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token = config_manager.get_hf_token()
        if token:
            self.hf_token_input.setText(token)
        self.hf_token_input.textChanged.connect(lambda t: config_manager.set_hf_token(t))
        self.v_layout.addWidget(self.hf_token_input)

        # HF Mirror Toggle
        self.mirror_layout = QHBoxLayout()
        self.mirror_label = TapeLabel(self)
        self.mirror_switch = IOSSwitch(self)
        self.mirror_switch.setChecked(config_manager.get("use_hf_mirror"))
        self.mirror_switch.checkedChanged.connect(lambda s: config_manager.set("use_hf_mirror", s))
        self.mirror_layout.addWidget(self.mirror_label)
        self.mirror_layout.addStretch(1)
        self.mirror_layout.addWidget(self.mirror_switch)
        self.v_layout.addLayout(self.mirror_layout)

        self.v_layout.addStretch(1)

        self.update_content()
        self.update_style()
        self.toggle_hf_token(self.diarize_switch.isChecked())
        self.on_device_changed(config_manager.get("device"))

    def update_content(self):
        # Update text for all elements
        self.title_label.setText(translator.t("settings"))
        self.general_title.setText(translator.t("general_settings"))
        self.lang_label.setText(translator.t("ui_language"))
        self.theme_label.setText(translator.t("theme_mode"))
        self.advanced_title.setText(translator.t("advanced_settings"))
        self.path_label.setText(translator.t("whisperx_path"))
        self.model_label.setText(translator.t("model_name"))
        self.whisper_lang_label.setText(translator.t("whisper_language"))
        self.update_whisper_languages()
        self.update_models_list()
        self.device_label.setText(translator.t("device"))
        self.compute_label.setText(translator.t("compute_type"))
        self.vad_label.setText(translator.t("vad_filter"))
        self.align_label.setText(translator.t("align"))
        self.diarize_label.setText(translator.t("diarize"))
        self.hf_token_input.setPlaceholderText(translator.t("hf_token_placeholder"))
        self.mirror_label.setText(translator.t("use_hf_mirror"))
        self.cuda_warning_label.setText(translator.t("cuda_install_tip"))

        # Update text inside segmented controls
        theme = config_manager.get("theme_mode")
        self.theme_seg.items[0] = ("light", translator.t("theme_light"), self.theme_seg.items[0][2])
        self.theme_seg.items[0][2].setText(translator.t("theme_light"))
        self.theme_seg.items[1] = ("dark", translator.t("theme_dark"), self.theme_seg.items[1][2])
        self.theme_seg.items[1][2].setText(translator.t("theme_dark"))

    def update_style(self):
        theme = config_manager.get("theme_mode")
        
        # Style dividers with tech look
        div_color = "#A1A1A8" if theme == "light" else "#3A3A4A"
        div_style = f"background-color: {div_color}; border: none; height: 2px; margin-top: 5px; margin-bottom: 5px;"
        self.divider1.setStyleSheet(div_style)
        self.divider2.setStyleSheet(div_style)

        if theme == "light":
            self.path_btn.setStyleSheet("background-color: #FFFFFF; color: #0F0F12; border: 1px solid #A1A1A8; font-weight: bold;")
            self.path_input.setStyleSheet("background-color: #FFFFFF; color: #0F0F12; border: 1px solid #A1A1A8;")
        else:
            self.path_btn.setStyleSheet("background-color: #1C1C24; color: #FFFFFF; border: 1px solid #3A3A4A; font-weight: bold;")
            self.path_input.setStyleSheet("background-color: #1C1C24; color: #FFFFFF; border: 1px solid #3A3A4A;")
        
        # Update child custom controls
        self.theme_seg.update_style()
        self.device_seg.update_style()
        self.compute_seg.update_style()
        self.vad_switch.update()
        self.align_switch.update()
        self.diarize_switch.update()
        self.mirror_switch.update()
        self.update() # triggers paintEvent to refresh background grid

    def on_lang_changed(self, text):
        lang = "zh" if text == "简体中文" else "en"
        translator.set_lang(lang)
        self.update_content()
        self.language_changed.emit(lang)

    def on_theme_changed(self, theme):
        config_manager.set("theme_mode", theme)
        self.update_style()
        self.theme_changed.emit(theme)

    def on_device_changed(self, device):
        config_manager.set("device", device)
        if device == "cpu":
            self.compute_seg.setItemEnabled("float16", False)
            self.compute_seg.setCurrentItem("int8")
            config_manager.set("compute_type", "int8")
        else:
            self.compute_seg.setItemEnabled("float16", True)

    def toggle_hf_token(self, checked):
        self.hf_token_input.setVisible(checked)

    def browse_whisperx_path(self):
        from PyQt6.QtWidgets import QFileDialog
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select WhisperX Executable",
            "",
            "Executable Files (*.exe);;All Files (*)"
        )
        if file_path:
            file_path = file_path.replace("/", "\\")
            self.path_input.setText(file_path)

    def scan_local_models(self):
        import os
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        local_models = []
        if os.path.exists(cache_dir):
            try:
                for item in os.listdir(cache_dir):
                    item_path = os.path.join(cache_dir, item)
                    if os.path.isdir(item_path):
                        if item.lower().startswith("models--") and "faster-whisper-" in item.lower():
                            # Check if model.bin exists in any snapshot directory
                            snapshots_dir = os.path.join(item_path, "snapshots")
                            if os.path.isdir(snapshots_dir):
                                has_model_bin = False
                                for snap in os.listdir(snapshots_dir):
                                    snap_path = os.path.join(snapshots_dir, snap)
                                    if os.path.isdir(snap_path):
                                        if os.path.exists(os.path.join(snap_path, "model.bin")):
                                            has_model_bin = True
                                            break
                                if not has_model_bin:
                                    continue # Skip this model since the actual model weights are missing!
                            else:
                                continue
                                
                            parts = item.split("--")
                            if len(parts) >= 3:
                                model_suffix = parts[-1].replace("faster-whisper-", "")
                                if model_suffix not in local_models:
                                    local_models.append(model_suffix)
            except Exception as e:
                print(f"Error scanning local models: {e}")
        return local_models

    def update_models_list(self):
        self.model_cb.blockSignals(True)
        self.model_cb.clear()
        
        local_list = self.scan_local_models()
        saved_model = config_manager.get("model_name") or "large-v3"
        
        standard_models = ["large-v3", "large-v2", "medium", "small", "base", "tiny"]
        
        # Ensure standard models + any extra local models detected are in the list
        all_possible_models = list(standard_models)
        for m in local_list:
            if m not in all_possible_models:
                all_possible_models.append(m)
                
        for model in all_possible_models:
            is_local = model in local_list
            suffix = translator.t("local_cached") if is_local else translator.t("auto_download")
            display_text = f"{model}{suffix}"
            self.model_cb.addItem(display_text, model)
            
            # If this is the saved model, select it
            if model == saved_model:
                self.model_cb.setCurrentText(display_text)
                
        self.model_cb.blockSignals(False)

    def on_model_changed(self, text):
        idx = self.model_cb.currentIndex()
        if idx >= 0:
            model_name = self.model_cb.itemData(idx)
            if model_name:
                config_manager.set("model_name", model_name)

    def update_whisper_languages(self):
        self.whisper_lang_cb.blockSignals(True)
        self.whisper_lang_cb.clear()
        
        lang = translator.get_lang()
        saved_lang = config_manager.get("language") or "auto"
        
        languages_data = [
            ("auto", "Auto Detect", "自动检测"),
            ("en", "English", "英语"),
            ("zh", "Chinese", "中文"),
            ("ja", "Japanese", "日语"),
            ("fr", "French", "法语"),
            ("de", "German", "德语"),
            ("es", "Spanish", "西班牙语")
        ]
        
        for code, en_name, zh_name in languages_data:
            display_name = zh_name if lang == "zh" else en_name
            self.whisper_lang_cb.addItem(display_name, code)
            if code == saved_lang:
                self.whisper_lang_cb.setCurrentIndex(self.whisper_lang_cb.count() - 1)
                
        self.whisper_lang_cb.blockSignals(False)

    def on_whisper_lang_changed(self):
        idx = self.whisper_lang_cb.currentIndex()
        if idx >= 0:
            code = self.whisper_lang_cb.itemData(idx)
            if code:
                config_manager.set("language", code)

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        w, h = self.width(), self.height()
        theme = config_manager.get("theme_mode")
        
        # 1. Background fill
        bg_color = QColor("#E6E6EB") if theme == "light" else QColor("#0F0F12")
        painter.fillRect(self.rect(), bg_color)
        
        # 2. Draw halftone dot grid
        dot_color = QColor("#D8D8DF") if theme == "light" else QColor("#1B1B22")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(dot_color))
        dot_spacing = 16
        dot_size = 1.5
        for x in range(0, w, dot_spacing):
            for y in range(0, h, dot_spacing):
                painter.drawEllipse(QPointF(float(x), float(y)), dot_size, dot_size)
                
        # 3. Draw skewed title card behind self.title_label (starts at y=20, h=35)
        card_y = 18.0
        card_h = 37.0
        card_x1 = 20.0
        card_x2 = float(w) - 20.0
        
        poly = QPolygonF([
            QPointF(card_x1 + 10.0, card_y),
            QPointF(card_x2, card_y),
            QPointF(card_x2 - 10.0, card_y + card_h),
            QPointF(card_x1, card_y + card_h)
        ])
        
        # Neon Yellow Card Body
        painter.setBrush(QBrush(QColor("#F3FF00")))
        painter.setPen(QPen(QColor("#0F0F12"), 2))
        painter.drawPolygon(poly)
        
        # Neon Pink Accent notch inside the title card
        painter.setBrush(QBrush(QColor("#FF0055")))
        painter.setPen(Qt.PenStyle.NoPen)
        accent_poly = QPolygonF([
            QPointF(card_x1 + 4.0, card_y + 4.0),
            QPointF(card_x1 + 12.0, card_y + 4.0),
            QPointF(card_x1 + 8.0, card_y + card_h - 4.0),
            QPointF(card_x1, card_y + card_h - 4.0)
        ])
        painter.drawPolygon(accent_poly)
        
        # 4. Draw vertical neon separation line on the left border (x = 0)
        sep_color = QColor("#0088FF") if theme == "light" else QColor("#00F0FF")
        painter.setPen(QPen(sep_color, 3))
        painter.drawLine(0, 0, 0, h)
        
        painter.end()
