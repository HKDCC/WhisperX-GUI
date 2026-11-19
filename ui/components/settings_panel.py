import os
from PyQt6.QtWidgets import (
    QFrame,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QComboBox,
    QPushButton,
    QFileDialog,
)
from PyQt6.QtCore import pyqtSignal, Qt, QPointF
from PyQt6.QtGui import QPainter, QColor, QBrush
from core.config_manager import config_manager
from core.translator import translator
from ui.components.ios_switch import IOSSwitch
from ui.components.segmented_control import SegmentedControl


class SettingLabel(QLabel):
    """Straight, flush-left aligned setting row label."""

    def __init__(self, parent=None, fixed_width=92):
        super().__init__(parent)
        self.setObjectName("setting_label")
        self.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        if fixed_width:
            self.setFixedWidth(fixed_width)


class SettingsPanel(QFrame):
    language_changed = pyqtSignal(str)
    theme_changed = pyqtSignal(str)
    install_cuda_requested = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("settings_panel")
        self.setFixedWidth(348)

        self.v_layout = QVBoxLayout(self)
        self.v_layout.setContentsMargins(18, 16, 18, 16)
        self.v_layout.setSpacing(8)

        # Straight Hardware Panel Title Bar
        self.title_label = QLabel(self)
        self.title_label.setObjectName("panel_title")
        self.title_label.setFixedHeight(34)
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        self.v_layout.addWidget(self.title_label)

        # ----------------------------------------------------
        # 01 // GENERAL SETTINGS
        # ----------------------------------------------------
        self.general_title = QLabel(self)
        self.general_title.setObjectName("section_title")
        self.v_layout.addWidget(self.general_title)

        # UI Language
        self.lang_layout = QHBoxLayout()
        self.lang_layout.setSpacing(10)
        self.lang_label = SettingLabel(self)
        self.lang_cb = QComboBox(self)
        self.lang_cb.addItems(["简体中文", "English"])
        self.lang_cb.setCurrentText("English" if config_manager.get("ui_language") == "en" else "简体中文")
        self.lang_cb.currentTextChanged.connect(self.on_lang_changed)
        self.lang_layout.addWidget(self.lang_label)
        self.lang_layout.addWidget(self.lang_cb, 1)
        self.v_layout.addLayout(self.lang_layout)

        # Theme Mode
        self.theme_layout = QHBoxLayout()
        self.theme_layout.setSpacing(10)
        self.theme_label = SettingLabel(self)
        self.theme_seg = SegmentedControl(self)
        self.theme_seg.addItem("light", "Light")
        self.theme_seg.addItem("dark", "Dark")
        self.theme_seg.setCurrentItem(config_manager.get("theme_mode") or "light")
        self.theme_seg.currentItemChanged.connect(self.on_theme_changed)
        self.theme_layout.addWidget(self.theme_label)
        self.theme_layout.addWidget(self.theme_seg, 1)
        self.v_layout.addLayout(self.theme_layout)

        # Divider 1
        self.divider1 = QFrame(self)
        self.divider1.setFrameShape(QFrame.Shape.HLine)
        self.divider1.setFixedHeight(1)
        self.v_layout.addWidget(self.divider1)

        # ----------------------------------------------------
        # 02 // ENGINE & MODEL SETTINGS
        # ----------------------------------------------------
        self.advanced_title = QLabel(self)
        self.advanced_title.setObjectName("section_title")
        self.v_layout.addWidget(self.advanced_title)

        # WhisperX CLI Path
        self.path_layout = QHBoxLayout()
        self.path_layout.setSpacing(6)
        self.path_label = SettingLabel(self)
        self.path_input = QLineEdit(self)
        self.path_input.setText(config_manager.get("whisperx_path") or "whisperx")
        self.path_input.textChanged.connect(lambda t: config_manager.set("whisperx_path", t))
        self.path_btn = QPushButton("...", self)
        self.path_btn.setFixedSize(32, 30)
        self.path_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.path_btn.clicked.connect(self.browse_whisperx_path)
        self.path_layout.addWidget(self.path_label)
        self.path_layout.addWidget(self.path_input, 1)
        self.path_layout.addWidget(self.path_btn)
        self.v_layout.addLayout(self.path_layout)

        # Whisper Model Selection
        self.model_layout = QHBoxLayout()
        self.model_layout.setSpacing(10)
        self.model_label = SettingLabel(self)
        self.model_cb = QComboBox(self)
        self.model_cb.setObjectName("model_cb")
        self.update_models_list()
        self.model_cb.currentIndexChanged.connect(self.on_model_changed)
        self.model_layout.addWidget(self.model_label)
        self.model_layout.addWidget(self.model_cb, 1)
        self.v_layout.addLayout(self.model_layout)

        # Whisper Language
        self.whisper_lang_layout = QHBoxLayout()
        self.whisper_lang_layout.setSpacing(10)
        self.whisper_lang_label = SettingLabel(self)
        self.whisper_lang_cb = QComboBox(self)
        self.whisper_lang_cb.setObjectName("whisper_lang_cb")
        self.update_whisper_languages()
        self.whisper_lang_cb.currentIndexChanged.connect(self.on_whisper_lang_changed)
        self.whisper_lang_layout.addWidget(self.whisper_lang_label)
        self.whisper_lang_layout.addWidget(self.whisper_lang_cb, 1)
        self.v_layout.addLayout(self.whisper_lang_layout)

        # Device
        self.device_layout = QHBoxLayout()
        self.device_layout.setSpacing(10)
        self.device_label = SettingLabel(self)
        self.device_seg = SegmentedControl(self)
        self.device_seg.addItem("cuda", "CUDA")
        self.device_seg.addItem("cpu", "CPU")
        self.device_seg.setCurrentItem(config_manager.get("device") or "cpu")
        self.device_seg.currentItemChanged.connect(self.on_device_changed)
        self.device_layout.addWidget(self.device_label)
        self.device_layout.addWidget(self.device_seg, 1)
        self.v_layout.addLayout(self.device_layout)
        self.device_seg.setItemEnabled("cuda", config_manager.cuda_available)

        # CUDA Hardware Alert Banner (visible when NVIDIA GPU exists without CUDA PyTorch)
        self.cuda_warning_card = QFrame(self)
        self.cuda_warning_card.setObjectName("cuda_warning_card")
        cuda_card_layout = QVBoxLayout(self.cuda_warning_card)
        cuda_card_layout.setContentsMargins(10, 7, 10, 7)
        cuda_card_layout.setSpacing(6)

        self.cuda_warning_label = QLabel(self.cuda_warning_card)
        self.cuda_warning_label.setWordWrap(True)
        self.cuda_warning_label.setObjectName("cuda_warning_label")
        cuda_card_layout.addWidget(self.cuda_warning_label)

        cuda_btn_row = QHBoxLayout()
        cuda_btn_row.setContentsMargins(0, 0, 0, 0)
        cuda_btn_row.addStretch(1)
        self.install_cuda_btn = QPushButton(self.cuda_warning_card)
        self.install_cuda_btn.setObjectName("install_cuda_btn")
        self.install_cuda_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.install_cuda_btn.setFixedHeight(24)
        self.install_cuda_btn.clicked.connect(self.install_cuda_requested.emit)
        cuda_btn_row.addWidget(self.install_cuda_btn)
        cuda_card_layout.addLayout(cuda_btn_row)

        self.v_layout.addWidget(self.cuda_warning_card)
        self.cuda_warning_card.setVisible(bool(config_manager.needs_cuda_install))

        # Compute Type
        self.compute_layout = QHBoxLayout()
        self.compute_layout.setSpacing(10)
        self.compute_label = SettingLabel(self)
        self.compute_seg = SegmentedControl(self)
        self.compute_seg.addItem("float16", "float16")
        self.compute_seg.addItem("int8", "int8")
        self.compute_seg.setCurrentItem(config_manager.get("compute_type") or "int8")
        self.compute_seg.currentItemChanged.connect(lambda t: config_manager.set("compute_type", t))
        self.compute_layout.addWidget(self.compute_label)
        self.compute_layout.addWidget(self.compute_seg, 1)
        self.v_layout.addLayout(self.compute_layout)

        # Divider 2
        self.divider2 = QFrame(self)
        self.divider2.setFrameShape(QFrame.Shape.HLine)
        self.divider2.setFixedHeight(1)
        self.v_layout.addWidget(self.divider2)

        # ----------------------------------------------------
        # 03 // PIPELINE SWITCHES
        # ----------------------------------------------------
        self.pipeline_title = QLabel(self)
        self.pipeline_title.setObjectName("section_title")
        self.v_layout.addWidget(self.pipeline_title)

        # VAD Toggle
        self.vad_layout = QHBoxLayout()
        self.vad_label = SettingLabel(self, fixed_width=None)
        self.vad_switch = IOSSwitch(self)
        self.vad_switch.setChecked(bool(config_manager.get("vad_filter")))
        self.vad_switch.checkedChanged.connect(lambda s: config_manager.set("vad_filter", s))
        self.vad_layout.addWidget(self.vad_label)
        self.vad_layout.addStretch(1)
        self.vad_layout.addWidget(self.vad_switch)
        self.v_layout.addLayout(self.vad_layout)

        # Alignment Toggle
        self.align_layout = QHBoxLayout()
        self.align_label = SettingLabel(self, fixed_width=None)
        self.align_switch = IOSSwitch(self)
        self.align_switch.setChecked(bool(config_manager.get("align")))
        self.align_switch.checkedChanged.connect(lambda s: config_manager.set("align", s))
        self.align_layout.addWidget(self.align_label)
        self.align_layout.addStretch(1)
        self.align_layout.addWidget(self.align_switch)
        self.v_layout.addLayout(self.align_layout)

        # Diarization Toggle
        self.diarize_layout = QHBoxLayout()
        self.diarize_label = SettingLabel(self, fixed_width=None)
        self.diarize_switch = IOSSwitch(self)
        self.diarize_switch.setChecked(bool(config_manager.get("diarize")))
        self.diarize_switch.checkedChanged.connect(self.toggle_hf_token)
        self.diarize_switch.checkedChanged.connect(lambda s: config_manager.set("diarize", s))
        self.diarize_layout.addWidget(self.diarize_label)
        self.diarize_layout.addStretch(1)
        self.diarize_layout.addWidget(self.diarize_switch)
        self.v_layout.addLayout(self.diarize_layout)

        # HF Token Row
        self.hf_token_row = QFrame(self)
        self.hf_token_row.setObjectName("hf_token_row")
        self.hf_token_row.setStyleSheet("QFrame#hf_token_row { background: transparent; border: none; }")
        hf_layout = QHBoxLayout(self.hf_token_row)
        hf_layout.setContentsMargins(0, 0, 0, 0)
        hf_layout.setSpacing(6)

        self.hf_token_label = SettingLabel(self.hf_token_row)
        self.hf_token_label.setText("HF Token")
        hf_layout.addWidget(self.hf_token_label)

        self.hf_token_input = QLineEdit(self.hf_token_row)
        self.hf_token_input.setEchoMode(QLineEdit.EchoMode.Password)
        token = config_manager.get_hf_token()
        if token:
            self.hf_token_input.setText(token)
        self.hf_token_input.textChanged.connect(lambda t: config_manager.set_hf_token(t))
        hf_layout.addWidget(self.hf_token_input, 1)

        self.hf_toggle_btn = QPushButton(self.hf_token_row)
        self.hf_toggle_btn.setCheckable(True)
        self.hf_toggle_btn.setFixedSize(46, 30)
        self.hf_toggle_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        self.hf_toggle_btn.toggled.connect(self.on_hf_visibility_toggled)
        hf_layout.addWidget(self.hf_toggle_btn)

        self.v_layout.addWidget(self.hf_token_row)

        # HF Mirror Toggle
        self.mirror_layout = QHBoxLayout()
        self.mirror_label = SettingLabel(self, fixed_width=None)
        self.mirror_switch = IOSSwitch(self)
        self.mirror_switch.setChecked(bool(config_manager.get("use_hf_mirror")))
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
        self.title_label.setText(translator.t("settings"))
        self.general_title.setText(translator.t("general_settings"))
        self.lang_label.setText(translator.t("ui_language"))
        self.theme_label.setText(translator.t("theme_mode"))
        self.advanced_title.setText(translator.t("engine_settings"))
        self.pipeline_title.setText(translator.t("pipeline_settings"))
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
        self.hf_toggle_btn.setText(
            translator.t("hide_token") if self.hf_toggle_btn.isChecked() else translator.t("show_token")
        )
        self.mirror_label.setText(translator.t("use_hf_mirror"))
        self.cuda_warning_label.setText(translator.t("cuda_install_tip"))
        self.install_cuda_btn.setText(translator.t("install_cuda_btn"))

        self.theme_seg.setItemText("light", translator.t("theme_light"))
        self.theme_seg.setItemText("dark", translator.t("theme_dark"))

    def update_style(self):
        theme = config_manager.get("theme_mode")

        div_color = "#C7C2B6" if theme == "light" else "#232732"
        self.divider1.setStyleSheet(f"background-color: {div_color}; border: none;")
        self.divider2.setStyleSheet(f"background-color: {div_color}; border: none;")

        if theme == "light":
            small_btn_css = """
                QPushButton {
                    background-color: #FFFFFF;
                    color: #141519;
                    border: 1.5px solid #B5B0A4;
                    border-radius: 2px;
                    font-family: "Segoe UI";
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    border-color: #FF5C1A;
                    color: #FF5C1A;
                }
            """
            self.cuda_warning_label.setStyleSheet(
                "font-family: 'Segoe UI'; color: #B43B0B; font-size: 11px; font-weight: 600; background: transparent;"
            )
        else:
            small_btn_css = """
                QPushButton {
                    background-color: #161920;
                    color: #E6E9F0;
                    border: 1.5px solid #2A2E3A;
                    border-radius: 2px;
                    font-family: "Segoe UI";
                    font-size: 11px;
                    font-weight: 700;
                }
                QPushButton:hover {
                    border-color: #FF5C1A;
                    color: #FF5C1A;
                }
            """
            self.cuda_warning_label.setStyleSheet(
                "font-family: 'Segoe UI'; color: #FF9466; font-size: 11px; font-weight: 600; background: transparent;"
            )

        self.path_btn.setStyleSheet(small_btn_css)
        self.hf_toggle_btn.setStyleSheet(small_btn_css)
        self.install_cuda_btn.setStyleSheet("""
            QPushButton {
                background-color: #FF5C1A;
                color: #FFFFFF;
                border: 1px solid #FF5C1A;
                border-radius: 2px;
                padding: 0 12px;
                font-family: "Segoe UI";
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover {
                background-color: #FF7338;
            }
        """)

        self.theme_seg.update_style()
        self.device_seg.update_style()
        self.compute_seg.update_style()
        self.vad_switch.update()
        self.align_switch.update()
        self.diarize_switch.update()
        self.mirror_switch.update()
        self.update()

    def on_hf_visibility_toggled(self, checked):
        self.hf_token_input.setEchoMode(
            QLineEdit.EchoMode.Normal if checked else QLineEdit.EchoMode.Password
        )
        self.hf_toggle_btn.setText(
            translator.t("hide_token") if checked else translator.t("show_token")
        )

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
        self.hf_token_row.setVisible(bool(checked))

    def browse_whisperx_path(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            translator.t("browse_whisperx_title"),
            "",
            "Executable Files (*.exe *.bat *.cmd);;All Files (*)",
        )
        if file_path:
            file_path = file_path.replace("/", "\\")
            self.path_input.setText(file_path)

    def scan_local_models(self):
        cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
        local_models = []
        if os.path.exists(cache_dir):
            try:
                for item in os.listdir(cache_dir):
                    item_path = os.path.join(cache_dir, item)
                    if os.path.isdir(item_path):
                        if item.lower().startswith("models--") and "faster-whisper-" in item.lower():
                            snapshots_dir = os.path.join(item_path, "snapshots")
                            if os.path.isdir(snapshots_dir):
                                has_model_bin = False
                                for snap in os.listdir(snapshots_dir):
                                    snap_path = os.path.join(snapshots_dir, snap)
                                    if os.path.isdir(snap_path) and os.path.exists(
                                        os.path.join(snap_path, "model.bin")
                                    ):
                                        has_model_bin = True
                                        break
                                if not has_model_bin:
                                    continue
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

        all_possible_models = list(standard_models)
        for m in local_list:
            if m not in all_possible_models:
                all_possible_models.append(m)
        if saved_model not in all_possible_models:
            all_possible_models.append(saved_model)

        for model in all_possible_models:
            is_local = model in local_list
            suffix = translator.t("local_cached") if is_local else translator.t("auto_download")
            display_text = f"{model}{suffix}"
            self.model_cb.addItem(display_text, model)
            if model == saved_model:
                self.model_cb.setCurrentIndex(self.model_cb.count() - 1)

        self.model_cb.blockSignals(False)

    def on_model_changed(self, idx):
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
            ("es", "Spanish", "西班牙语"),
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
        painter.setRenderHint(QPainter.RenderHint.Antialiasing, False)

        w, h = self.width(), self.height()
        theme = config_manager.get("theme_mode")

        # 1. Clean architectural matte canvas
        bg_color = QColor("#E8E5DC") if theme == "light" else QColor("#0D0E12")
        painter.fillRect(self.rect(), bg_color)

        # 2. Ultra-subtle straight blueprint dot matrix
        dot_color = QColor("#D5D0C4") if theme == "light" else QColor("#1A1D26")
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(dot_color))
        for x in range(12, w, 18):
            for y in range(12, h, 18):
                painter.drawRect(x, y, 1, 1)

        # 3. Straight 1.5px structural divider line on left edge
        sep_color = QColor("#18191E") if theme == "light" else QColor("#2A2E3A")
        painter.fillRect(0, 0, 2, h, sep_color)

        painter.end()
