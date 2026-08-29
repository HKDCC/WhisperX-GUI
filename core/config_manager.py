import os
import json
import base64

APP_NAME = "WhisperX_GUI"
CONFIG_FILE = "config.json"

class ConfigManager:
    def __init__(self):
        import platform
        if platform.system() == "Windows":
            local_appdata = os.getenv("LOCALAPPDATA")
            if local_appdata:
                config_dir = os.path.join(local_appdata, APP_NAME)
            else:
                config_dir = os.path.join(os.path.expanduser("~"), f".{APP_NAME.lower()}")
        else:
            config_dir = os.path.join(os.path.expanduser("~"), f".{APP_NAME.lower()}")
            
        os.makedirs(config_dir, exist_ok=True)
        self.config_path = os.path.join(config_dir, CONFIG_FILE)
        
        self.cuda_available = self.check_cuda_available()
        self.has_nvidia_gpu = self.check_nvidia_gpu()
        
        self.default_config = {
            "model_name": "base",
            "device": "cuda" if self.cuda_available else "cpu",
            "compute_type": "float16" if self.cuda_available else "int8",
            "output_formats": ["srt", "txt"],
            "vad_filter": True,
            "align": True,
            "diarize": True,
            "language": "auto",
            "ui_language": "zh",
            "theme_mode": "light",
            "use_hf_mirror": True,
            "whisperx_path": "whisperx",
        }
        self.config = self.load_config()

    def check_cuda_available(self):
        # 1. Check local PyTorch environment
        try:
            import torch
            if torch.cuda.is_available():
                return True
        except ImportError:
            pass
        # 2. Check if there is physically an NVIDIA GPU.
        # This enables the option in case they use a custom GPU-enabled whisperx executable.
        return self.check_nvidia_gpu()

    def check_nvidia_gpu(self):
        import shutil
        if shutil.which("nvidia-smi") is not None:
            return True
        common_paths = [
            r"C:\Program Files\NVIDIA Corporation\NVSMI\nvidia-smi.exe",
            r"C:\Windows\System32\nvidia-smi.exe"
        ]
        for path in common_paths:
            if os.path.exists(path):
                return True
        return False

    def load_config(self):
        config = self.default_config.copy()
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # merge with default
                    config.update(data)
            except Exception as e:
                print(f"Failed to load config: {e}")
        
        # CPU / float16 Config Incompatibility Check
        if config.get("device") == "cpu" and config.get("compute_type") == "float16":
            config["compute_type"] = "int8"
            
        return config

    def save_config(self):
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Failed to save config: {e}")

    def get(self, key):
        return self.config.get(key, self.default_config.get(key))

    def set(self, key, value):
        self.config[key] = value
        # CPU / float16 Config Incompatibility Check
        if self.config.get("device") == "cpu" and self.config.get("compute_type") == "float16":
            self.config["compute_type"] = "int8"
        self.save_config()

    def get_hf_token(self):
        encoded = self.config.get("hf_token", "")
        if encoded:
            try:
                token = base64.b64decode(encoded.encode()).decode()
                return token.strip() if token else None
            except:
                return None
        return None

    def set_hf_token(self, token):
        if token:
            token_stripped = token.strip()
            if token_stripped:
                encoded = base64.b64encode(token_stripped.encode()).decode()
                self.config["hf_token"] = encoded
            else:
                self.config.pop("hf_token", None)
        else:
            self.config.pop("hf_token", None)
        self.save_config()

config_manager = ConfigManager()
