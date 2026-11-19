import os


def _asset_url(filename):
    base_dir = os.path.dirname(os.path.abspath(__file__))
    path = os.path.join(base_dir, "assets", filename).replace("\\", "/")
    return path


def get_stylesheet(theme="light"):
    checkmark_path = _asset_url("checkmark.png")
    arrow_light_path = _asset_url("down_arrow_light.png")
    arrow_dark_path = _asset_url("down_arrow_dark.png")

    if theme == "light":
        return f"""
        /* Cassette-Futurism Precision Hardware Console - Light Mode */
        QMainWindow, QWidget#main_widget {{
            background-color: #E8E5DC;
            color: #141519;
            font-family: "Segoe UI";
            font-size: 13px;
        }}

        QDialog, QMessageBox {{
            background-color: #F2EFE8;
            color: #141519;
            border: 1.5px solid #18191E;
        }}

        QDialog QLabel, QMessageBox QLabel {{
            color: #141519;
            background-color: transparent;
            font-family: "Segoe UI";
        }}

        QDialog QPushButton, QMessageBox QPushButton {{
            background-color: #FFFFFF;
            color: #141519;
            border: 1.5px solid #18191E;
            border-radius: 2px;
            padding: 5px 14px;
            font-weight: 600;
            font-family: "Segoe UI";
        }}

        QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
            background-color: #FF5C1A;
            border-color: #FF5C1A;
            color: #FFFFFF;
        }}

        QWidget#left_pane {{
            background-color: #F2EFE8;
        }}

        QFrame#settings_panel {{
            background-color: transparent;
            border: none;
        }}

        QLabel {{
            color: #141519;
            font-family: "Segoe UI";
        }}

        QLabel#header_title {{
            font-size: 16px;
            font-weight: 800;
            color: #141519;
            letter-spacing: 0.8px;
        }}

        QLabel#header_subtitle {{
            font-size: 10.5px;
            font-weight: 600;
            color: #565A65;
            font-family: "Segoe UI";
            letter-spacing: 0.4px;
        }}

        QLabel#panel_title {{
            font-size: 13px;
            font-weight: 800;
            color: #E5FF2E;
            background-color: #141519;
            border-left: 4px solid #FF5C1A;
            border-radius: 2px;
            padding: 0 12px;
            letter-spacing: 0.6px;
        }}

        QLabel#section_title {{
            font-size: 11px;
            font-weight: 700;
            color: #141519;
            background-color: #E5E1D7;
            border-left: 3px solid #FF5C1A;
            padding: 4px 8px;
            font-family: "Consolas";
            letter-spacing: 0.4px;
        }}

        QLabel#setting_label {{
            font-size: 12px;
            font-weight: 600;
            color: #2B2E36;
        }}

        QLabel#section_header_label {{
            font-size: 12px;
            font-weight: 700;
            color: #141519;
            font-family: "Segoe UI";
        }}

        QFrame#surface_card {{
            background-color: #FAF8F3;
            border: 1px solid #18191E;
            border-radius: 3px;
        }}

        QFrame#cuda_warning_card {{
            background-color: #FFF4EE;
            border: 1.5px solid #FF5C1A;
            border-radius: 3px;
        }}

        QLineEdit, QComboBox {{
            background-color: #FFFFFF;
            color: #141519;
            border: 1.5px solid #B5B0A4;
            border-radius: 2px;
            padding: 4px 8px;
            min-height: 20px;
            font-family: "Segoe UI";
            font-size: 12px;
        }}

        QLineEdit:hover, QComboBox:hover {{
            border-color: #18191E;
        }}

        QLineEdit:focus, QComboBox:focus {{
            border: 1.5px solid #FF5C1A;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #D5D0C5;
        }}

        QComboBox::down-arrow {{
            image: url("{arrow_light_path}");
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #FFFFFF;
            border: 1.5px solid #18191E;
            selection-background-color: #141519;
            selection-color: #E5FF2E;
            outline: 0;
            padding: 3px;
            color: #141519;
        }}

        QCheckBox {{
            spacing: 6px;
            font-weight: 700;
            font-size: 11px;
            font-family: "Consolas";
            color: #141519;
            padding: 2px 4px;
        }}

        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 1.5px solid #18191E;
            border-radius: 2px;
            background-color: #FFFFFF;
        }}

        QCheckBox::indicator:unchecked:hover {{
            border-color: #FF5C1A;
        }}

        QCheckBox::indicator:checked {{
            border-color: #FF5C1A;
            background-color: #FF5C1A;
            image: url("{checkmark_path}");
        }}

        QListWidget {{
            background-color: #FFFFFF;
            border: 1px solid #18191E;
            border-radius: 3px;
            padding: 4px;
            outline: 0;
            font-family: "Consolas";
            font-size: 12px;
        }}

        QListWidget::item {{
            padding: 6px 10px;
            color: #141519;
            border-bottom: 1px solid #EFECE4;
        }}

        QListWidget::item:hover {{
            background-color: #F2EFE8;
        }}

        QListWidget::item:selected {{
            background-color: #141519;
            color: #E5FF2E;
            font-weight: 700;
        }}

        QTextEdit#console_output {{
            background-color: #FAF8F3;
            color: #1E2128;
            font-family: "Consolas";
            font-size: 11.5px;
            border: 1px solid #18191E;
            border-radius: 3px;
            padding: 8px;
        }}

        QProgressBar {{
            background-color: #E2DFD5;
            border: 1px solid #18191E;
            border-radius: 2px;
            text-align: center;
            color: #141519;
            font-family: "Consolas";
            font-size: 11px;
            font-weight: 700;
            min-height: 22px;
        }}

        QProgressBar::chunk {{
            background-color: #FF5C1A;
        }}

        QScrollBar:vertical {{
            border: none;
            background: #EAE6DC;
            width: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: #ACA79B;
            min-height: 20px;
            border-radius: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: #FF5C1A;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: #EAE6DC;
            height: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: #ACA79B;
            min-width: 20px;
            border-radius: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: #FF5C1A;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
    else:
        return f"""
        /* Cassette-Futurism Precision Hardware Console - Dark Mode */
        QMainWindow, QWidget#main_widget {{
            background-color: #0D0E12;
            color: #F2F4F8;
            font-family: "Segoe UI";
            font-size: 13px;
        }}

        QDialog, QMessageBox {{
            background-color: #111318;
            color: #F2F4F8;
            border: 1.5px solid #2A2E3A;
        }}

        QDialog QLabel, QMessageBox QLabel {{
            color: #F2F4F8;
            background-color: transparent;
            font-family: "Segoe UI";
        }}

        QDialog QPushButton, QMessageBox QPushButton {{
            background-color: #161920;
            color: #F2F4F8;
            border: 1.5px solid #2A2E3A;
            border-radius: 2px;
            padding: 5px 14px;
            font-weight: 600;
            font-family: "Segoe UI";
        }}

        QDialog QPushButton:hover, QMessageBox QPushButton:hover {{
            background-color: #FF5C1A;
            border-color: #FF5C1A;
            color: #FFFFFF;
        }}

        QWidget#left_pane {{
            background-color: #111318;
        }}

        QFrame#settings_panel {{
            background-color: transparent;
            border: none;
        }}

        QLabel {{
            color: #F2F4F8;
            font-family: "Segoe UI";
        }}

        QLabel#header_title {{
            font-size: 16px;
            font-weight: 800;
            color: #F2F4F8;
            letter-spacing: 0.8px;
        }}

        QLabel#header_subtitle {{
            font-size: 10.5px;
            font-weight: 600;
            color: #8A93A4;
            font-family: "Segoe UI";
            letter-spacing: 0.4px;
        }}

        QLabel#panel_title {{
            font-size: 13px;
            font-weight: 800;
            color: #F2F4F8;
            background-color: #161920;
            border: 1px solid #2A2E3A;
            border-left: 4px solid #E5FF2E;
            border-radius: 2px;
            padding: 0 12px;
            letter-spacing: 0.6px;
        }}

        QLabel#section_title {{
            font-size: 11px;
            font-weight: 700;
            color: #E5FF2E;
            background-color: #161920;
            border-left: 3px solid #FF5C1A;
            padding: 4px 8px;
            font-family: "Consolas";
            letter-spacing: 0.4px;
        }}

        QLabel#setting_label {{
            font-size: 12px;
            font-weight: 600;
            color: #C2C8D4;
        }}

        QLabel#section_header_label {{
            font-size: 12px;
            font-weight: 700;
            color: #E6E9F0;
            font-family: "Segoe UI";
        }}

        QFrame#surface_card {{
            background-color: #151820;
            border: 1.5px solid #2A2E3A;
            border-radius: 3px;
        }}

        QFrame#cuda_warning_card {{
            background-color: #211512;
            border: 1.5px solid #FF5C1A;
            border-radius: 3px;
        }}

        QLineEdit, QComboBox {{
            background-color: #161920;
            color: #F2F4F8;
            border: 1.5px solid #2A2E3A;
            border-radius: 2px;
            padding: 4px 8px;
            min-height: 20px;
            font-family: "Segoe UI";
            font-size: 12px;
        }}

        QLineEdit:hover, QComboBox:hover {{
            border-color: #484F63;
        }}

        QLineEdit:focus, QComboBox:focus {{
            border: 1.5px solid #FF5C1A;
        }}

        QComboBox::drop-down {{
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 24px;
            border-left: 1px solid #2A2E3A;
        }}

        QComboBox::down-arrow {{
            image: url("{arrow_dark_path}");
            width: 10px;
            height: 10px;
        }}

        QComboBox QAbstractItemView {{
            background-color: #161920;
            border: 1.5px solid #FF5C1A;
            selection-background-color: #E5FF2E;
            selection-color: #111318;
            outline: 0;
            padding: 3px;
            color: #F2F4F8;
        }}

        QCheckBox {{
            spacing: 6px;
            font-weight: 700;
            font-size: 11px;
            font-family: "Consolas";
            color: #E6E9F0;
            padding: 2px 4px;
        }}

        QCheckBox::indicator {{
            width: 15px;
            height: 15px;
            border: 1.5px solid #3A4050;
            border-radius: 2px;
            background-color: #161920;
        }}

        QCheckBox::indicator:unchecked:hover {{
            border-color: #FF5C1A;
        }}

        QCheckBox::indicator:checked {{
            border-color: #FF5C1A;
            background-color: #FF5C1A;
            image: url("{checkmark_path}");
        }}

        QListWidget {{
            background-color: #0E1015;
            border: 1.5px solid #2A2E3A;
            border-radius: 3px;
            padding: 4px;
            outline: 0;
            font-family: "Consolas";
            font-size: 12px;
        }}

        QListWidget::item {{
            padding: 6px 10px;
            color: #E6E9F0;
            border-bottom: 1px solid #1A1E27;
        }}

        QListWidget::item:hover {{
            background-color: #1A1E27;
        }}

        QListWidget::item:selected {{
            background-color: #E5FF2E;
            color: #111318;
            font-weight: 700;
        }}

        QTextEdit#console_output {{
            background-color: #0A0B0E;
            color: #D2D8E4;
            font-family: "Consolas";
            font-size: 11.5px;
            border: 1.5px solid #2A2E3A;
            border-radius: 3px;
            padding: 8px;
        }}

        QProgressBar {{
            background-color: #161920;
            border: 1.5px solid #2A2E3A;
            border-radius: 2px;
            text-align: center;
            color: #F2F4F8;
            font-family: "Consolas";
            font-size: 11px;
            font-weight: 700;
            min-height: 22px;
        }}

        QProgressBar::chunk {{
            background-color: #FF5C1A;
        }}

        QScrollBar:vertical {{
            border: none;
            background: #111318;
            width: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:vertical {{
            background: #2E3444;
            min-height: 20px;
            border-radius: 2px;
        }}

        QScrollBar::handle:vertical:hover {{
            background: #FF5C1A;
        }}

        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0px;
        }}

        QScrollBar:horizontal {{
            border: none;
            background: #111318;
            height: 8px;
            margin: 0px;
        }}

        QScrollBar::handle:horizontal {{
            background: #2E3444;
            min-width: 20px;
            border-radius: 2px;
        }}

        QScrollBar::handle:horizontal:hover {{
            background: #FF5C1A;
        }}

        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{
            width: 0px;
        }}
        """
