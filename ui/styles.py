def get_stylesheet(theme="light"):
    if theme == "light":
        return """
        /* ZZZ Light Mode (White Vinyl/Industrial Lab styling) */
        QMainWindow, QWidget#main_widget {
            background-color: #E6E6EB;
            color: #0F0F12;
            font-family: "Consolas", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        QDialog, QMessageBox {
            background-color: #EDEDF2;
            color: #0F0F12;
            border: 2px solid #0F0F12;
        }
        
        QDialog QLabel, QMessageBox QLabel {
            color: #0F0F12;
            background-color: transparent;
            font-family: "Consolas", sans-serif;
        }
        
        QDialog QPushButton, QMessageBox QPushButton {
            background-color: #FFFFFF;
            color: #0F0F12;
            border: 2px solid #0F0F12;
            padding: 5px 15px;
            font-weight: bold;
            font-family: "Consolas", sans-serif;
        }
        
        QDialog QPushButton:hover, QMessageBox QPushButton:hover {
            background-color: #F3FF00;
            color: #0F0F12;
        }
        
        QWidget#left_pane {
            background-color: #EDEDF2;
        }
        
        QFrame#settings_panel {
            background-color: transparent;
            border: none;
        }
        
        QLabel {
            color: #0F0F12;
            font-family: "Consolas", sans-serif;
        }
        
        QLabel#panel_title {
            font-size: 16px;
            font-weight: 900;
            color: #0F0F12;
            background: transparent;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }

        QLabel#section_title {
            font-size: 11px;
            font-weight: 800;
            color: #0088FF;
            background-color: #D8D8DF;
            border-left: 4px solid #FF0055;
            padding: 4px 8px;
            margin-top: 12px;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        QLineEdit, QComboBox {
            background-color: #FFFFFF;
            color: #0F0F12;
            border: 2px solid #A1A1A8;
            padding: 5px 8px;
            min-height: 20px;
            font-family: "Consolas", monospace;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #0088FF;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 2px solid #A1A1A8;
        }
        
        QComboBox::down-arrow {
            image: url(ui/assets/down_arrow_dark.png);
            width: 10px;
            height: 10px;
        }

        QComboBox QAbstractItemView {
            background-color: #FFFFFF;
            border: 2px solid #0088FF;
            selection-background-color: #F3FF00;
            selection-color: #0F0F12;
            outline: 0;
            padding: 4px;
            color: #0F0F12;
        }
        
        QCheckBox {
            spacing: 8px;
            font-weight: bold;
            color: #0F0F12;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #A1A1A8;
            background-color: #FFFFFF;
        }
        
        QCheckBox::indicator:unchecked:hover {
            border-color: #FF0055;
        }
        
        QCheckBox::indicator:checked {
            border-color: #F3FF00;
            background-color: #F3FF00;
            image: url(ui/assets/checkmark.png);
        }
        
        QListWidget {
            background-color: #EDEDF2;
            border: 2px solid #A1A1A8;
            padding: 5px;
            outline: 0;
        }
        
        QListWidget::item {
            padding: 8px 10px;
            color: #0F0F12;
            margin-bottom: 2px;
            font-family: "Consolas", monospace;
        }
        
        QListWidget::item:hover {
            background-color: #D8D8DF;
            color: #0088FF;
        }
        
        QListWidget::item:selected {
            background-color: #FF0055;
            color: #FFFFFF;
            font-weight: bold;
        }
        
        QTextEdit {
            background-color: #E6E6EB;
            color: #0F0F12;
            font-family: "Consolas", monospace;
            font-size: 12px;
            border: 2px solid #FF0055;
            padding: 10px;
        }
        
        QProgressBar {
            background-color: #D8D8DF;
            border: 2px solid #A1A1A8;
            text-align: center;
            color: transparent;
            height: 12px;
        }
        
        QProgressBar::chunk {
            background-color: #0088FF;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #E6E6EB;
            width: 8px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #A1A1A8;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #0088FF;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #E6E6EB;
            height: 8px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #A1A1A8;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #0088FF;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        """
    else:
        return """
        /* Zenless Zone Zero (ZZZ) Cyberpunk Cassette Futurism Theme - Dark Mode */
        QMainWindow, QWidget#main_widget {
            background-color: #0F0F12;
            color: #FFFFFF;
            font-family: "Consolas", "Segoe UI", sans-serif;
            font-size: 13px;
        }
        
        QDialog, QMessageBox {
            background-color: #121216;
            color: #FFFFFF;
            border: 2px solid #3A3A4A;
        }
        
        QDialog QLabel, QMessageBox QLabel {
            color: #FFFFFF;
            background-color: transparent;
            font-family: "Consolas", sans-serif;
        }
        
        QDialog QPushButton, QMessageBox QPushButton {
            background-color: #1C1C24;
            color: #FFFFFF;
            border: 1px solid #3A3A4A;
            padding: 5px 15px;
            font-weight: bold;
            font-family: "Consolas", sans-serif;
        }
        
        QDialog QPushButton:hover, QMessageBox QPushButton:hover {
            background-color: #FF0055;
            color: #FFFFFF;
            border-color: #FF0055;
        }
        
        QWidget#left_pane {
            background-color: #09090C;
        }
        
        QFrame#settings_panel {
            background-color: transparent;
            border: none;
        }
        
        QLabel {
            color: #FFFFFF;
            font-family: "Consolas", sans-serif;
        }
        
        QLabel#panel_title {
            font-size: 16px;
            font-weight: 900;
            color: #0F0F12;
            background: transparent;
            text-transform: uppercase;
            letter-spacing: 1.5px;
        }

        QLabel#section_title {
            font-size: 11px;
            font-weight: 800;
            color: #00F0FF;
            background-color: #15151A;
            border-left: 4px solid #FF0055;
            padding: 4px 8px;
            margin-top: 12px;
            margin-bottom: 4px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        
        QLineEdit, QComboBox {
            background-color: #15151A;
            color: #FFFFFF;
            border: 2px solid #3A3A4A;
            padding: 5px 8px;
            min-height: 20px;
            font-family: "Consolas", monospace;
        }
        
        QLineEdit:focus, QComboBox:focus {
            border: 2px solid #00F0FF;
        }
        
        QComboBox::drop-down {
            subcontrol-origin: padding;
            subcontrol-position: top right;
            width: 25px;
            border-left: 2px solid #3A3A4A;
        }
        
        QComboBox::down-arrow {
            image: url(ui/assets/down_arrow_light.png);
            width: 10px;
            height: 10px;
        }

        QComboBox QAbstractItemView {
            background-color: #15151A;
            border: 2px solid #00F0FF;
            selection-background-color: #F3FF00;
            selection-color: #0F0F12;
            outline: 0;
            padding: 4px;
            color: #FFFFFF;
        }
        
        QCheckBox {
            spacing: 8px;
            font-weight: bold;
            color: #FFFFFF;
        }
        
        QCheckBox::indicator {
            width: 16px;
            height: 16px;
            border: 2px solid #3A3A4A;
            background-color: #15151A;
        }
        
        QCheckBox::indicator:unchecked:hover {
            border-color: #FF0055;
        }
        
        QCheckBox::indicator:checked {
            border-color: #F3FF00;
            background-color: #F3FF00;
            image: url(ui/assets/checkmark.png);
        }
        
        QListWidget {
            background-color: #121216;
            border: 2px solid #3A3A4A;
            padding: 5px;
            outline: 0;
        }
        
        QListWidget::item {
            padding: 8px 10px;
            color: #FFFFFF;
            margin-bottom: 2px;
            font-family: "Consolas", monospace;
        }
        
        QListWidget::item:hover {
            background-color: #1C1C24;
            color: #00F0FF;
        }
        
        QListWidget::item:selected {
            background-color: #FF0055;
            color: #FFFFFF;
            font-weight: bold;
        }
        
        QTextEdit {
            background-color: #08080A;
            color: #00F0FF;
            font-family: "Consolas", monospace;
            font-size: 12px;
            border: 2px solid #FF0055;
            padding: 10px;
        }
        
        QProgressBar {
            background-color: #15151A;
            border: 2px solid #3A3A4A;
            text-align: center;
            color: transparent;
            height: 12px;
        }
        
        QProgressBar::chunk {
            background-color: #F3FF00;
        }
        
        QScrollBar:vertical {
            border: none;
            background: #0F0F12;
            width: 8px;
            margin: 0px;
        }
        
        QScrollBar::handle:vertical {
            background: #3A3A4A;
            min-height: 20px;
        }
        
        QScrollBar::handle:vertical:hover {
            background: #00F0FF;
        }
        
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
            height: 0px;
        }
        
        QScrollBar:horizontal {
            border: none;
            background: #0F0F12;
            height: 8px;
            margin: 0px;
        }
        
        QScrollBar::handle:horizontal {
            background: #3A3A4A;
            min-width: 20px;
        }
        
        QScrollBar::handle:horizontal:hover {
            background: #00F0FF;
        }
        
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
            width: 0px;
        }
        """
