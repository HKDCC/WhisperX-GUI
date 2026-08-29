import sys
import os
import traceback
import platform

if getattr(sys, 'frozen', False):
    # running in PyInstaller bundle
    exe_dir = os.path.dirname(sys.executable)
else:
    # running in normal python environment
    exe_dir = os.path.dirname(os.path.abspath(__file__))

os.environ["PATH"] = exe_dir + os.pathsep + os.environ.get("PATH", "")

os.chdir(os.path.dirname(os.path.abspath(__file__)))

def get_log_dir():
    if platform.system() == "Windows":
        local_appdata = os.getenv("LOCALAPPDATA")
        if local_appdata:
            return os.path.join(local_appdata, "WhisperX_GUI")
    return os.path.join(os.path.expanduser("~"), ".whisperx_gui")

log_dir = get_log_dir()
os.makedirs(log_dir, exist_ok=True)

class CrashLogger:
    def __init__(self, filename="crash.log", stream=None):
        self.logfile = open(filename, "w", encoding="utf-8", buffering=1)
        self.stream = stream
    def write(self, msg):
        self.logfile.write(msg)
        self.logfile.flush()
        if self.stream:
            try:
                self.stream.write(msg)
                self.stream.flush()
            except Exception:
                pass
    def flush(self):
        self.logfile.flush()
        if self.stream:
            try:
                self.stream.flush()
            except Exception:
                pass

sys.stdout = CrashLogger(os.path.join(log_dir, "stdout_crash.log"), sys.__stdout__)
sys.stderr = CrashLogger(os.path.join(log_dir, "stderr_crash.log"), sys.__stderr__)

def global_exception_handler(exc_type, exc_value, exc_traceback):
    tb_text = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
    try:
        sys.stderr.write(tb_text)
    except:
        pass
    
    try:
        from PyQt6.QtWidgets import QApplication
        app = QApplication.instance()
        if not app:
            app = QApplication(sys.argv)
        from ui.crash_dialog import ZZZCrashDialog
        dialog = ZZZCrashDialog(tb_text, is_crash=True)
        dialog.exec()
    except Exception as e:
        try:
            sys.stderr.write(f"Failed to display crash dialog: {e}\n")
        except:
            pass
    sys.exit(1)

sys.excepthook = global_exception_handler

# Set QT_API to force qfluentwidgets to use PyQt6 instead of PyQt5
os.environ["QT_API"] = "pyqt6"

from PyQt6.QtWidgets import QApplication

# Ensure correct working directory so modules can be imported
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow

def main():
    app = QApplication(sys.argv)
    
    # Load stylesheet on the application from the start
    from core.config_manager import config_manager
    from ui.styles import get_stylesheet
    theme = config_manager.get("theme_mode") or "light"
    app.setStyleSheet(get_stylesheet(theme))
    
    # Check whisperx CLI path
    import shutil
    whisperx_exe = config_manager.get("whisperx_path") or "whisperx"
    
    is_valid = False
    if os.path.exists(whisperx_exe):
        is_valid = True
    elif shutil.which(whisperx_exe):
        is_valid = True
        
    if not is_valid:
        from ui.crash_dialog import ZZZCrashDialog
        msg = (
            "WARNING: 'whisperx' executable was not found.\n\n"
            "Please ensure that WhisperX is installed correctly.\n"
            "If you are using a virtual environment (venv/conda), you can configure the "
            "exact executable path inside the settings panel of this application once launched.\n\n"
            "Current configured path: " + whisperx_exe
        )
        dialog = ZZZCrashDialog(msg, is_crash=False, title="CLI PATH WARNING")
        dialog.exec()
        
    # Check ffmpeg CLI path
    if not shutil.which("ffmpeg"):
        from ui.crash_dialog import ZZZCrashDialog
        msg = (
            "WARNING: 'ffmpeg' executable was not found in your system's PATH.\n\n"
            "WhisperX requires FFmpeg to process audio and video files.\n"
            "Please ensure FFmpeg is installed and added to your system's PATH,\n"
            "otherwise transcription will fail."
        )
        dialog = ZZZCrashDialog(msg, is_crash=False, title="FFMPEG PATH WARNING")
        dialog.exec()
        
    window = MainWindow()
    window.show()
    
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
