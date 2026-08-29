import os
import subprocess
import threading
from PyQt6.QtCore import QThread, pyqtSignal

def get_local_model_path(model_name):
    import os
    cache_dir = os.path.expanduser("~/.cache/huggingface/hub")
    if os.path.exists(cache_dir):
        try:
            for item in os.listdir(cache_dir):
                item_path = os.path.join(cache_dir, item)
                if os.path.isdir(item_path):
                    if item.lower().startswith("models--") and "faster-whisper-" in item.lower():
                        parts = item.split("--")
                        if len(parts) >= 3:
                            model_suffix = parts[-1].replace("faster-whisper-", "")
                            if model_suffix.lower() == model_name.lower():
                                snapshots_dir = os.path.join(item_path, "snapshots")
                                if os.path.isdir(snapshots_dir):
                                    for snap in os.listdir(snapshots_dir):
                                        snap_path = os.path.join(snapshots_dir, snap)
                                        if os.path.isdir(snap_path):
                                            if os.path.exists(os.path.join(snap_path, "model.bin")):
                                                return snap_path
        except Exception as e:
            print(f"Error resolving local model path: {e}")
    return None

class WhisperRunner(QThread):
    progress_updated = pyqtSignal(str)
    progress_percent = pyqtSignal(int)
    log_updated = pyqtSignal(str)
    transcription_finished = pyqtSignal(bool, str)

    def __init__(self, config, files, output_dir):
        super().__init__()
        self.config = config
        self.files = files
        self.output_dir = output_dir
        self._is_running = True
        self.process = None
        self.lock = threading.Lock()

    def stop(self):
        with self.lock:
            self._is_running = False
            if self.process:
                if os.name == 'nt':
                    try:
                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                    except Exception as e:
                        print(f"Failed to taskkill process: {e}")
                else:
                    try:
                        import signal
                        pgid = os.getpgid(self.process.pid)
                        os.killpg(pgid, signal.SIGTERM)
                    except Exception as e:
                        try:
                            self.process.terminate()
                        except Exception:
                            pass
                        print(f"Failed to terminate process group: {e}")

    def run(self):
        import re
        tqdm_regex = re.compile(r"(\d+)%\s*\|")
        
        try:
            for file in self.files:
                if not self._is_running:
                    self.log_updated.emit("Stopped by user.")
                    self.transcription_finished.emit(False, "Stopped by user.")
                    return

                self.progress_updated.emit(f"Processing: {os.path.basename(file)}")
                self.log_updated.emit(f"Starting {os.path.basename(file)}...\n")

                # Resolve directory path & create if not exists
                self.output_dir = os.path.abspath(self.output_dir)
                os.makedirs(self.output_dir, exist_ok=True)

                cmd = [self.config.get("whisperx_path") or "whisperx", file]
                
                model_name = self.config.get("model_name")
                local_path = get_local_model_path(model_name)
                if local_path:
                    cmd.extend(["--model", local_path])
                    self.log_updated.emit(f"Detected complete offline cache. Using local model path: {local_path}\n")
                else:
                    cmd.extend(["--model", model_name])
                    
                cmd.extend(["--output_dir", self.output_dir])
                cmd.extend(["--compute_type", self.config.get("compute_type")])
                
                # Formats
                formats = self.config.get("output_formats")
                if isinstance(formats, list) and len(formats) > 1:
                    cmd.extend(["--output_format", "all"])
                elif isinstance(formats, list) and len(formats) == 1:
                    cmd.extend(["--output_format", formats[0]])
                elif isinstance(formats, str):
                    cmd.extend(["--output_format", formats])
                else:
                    cmd.extend(["--output_format", "srt"])

                # Language
                if self.config.get("language") != "auto":
                    cmd.extend(["--language", self.config.get("language")])

                # Advanced
                if not self.config.get("align"):
                    cmd.append("--no_align")
                
                if self.config.get("diarize"):
                    cmd.append("--diarize")
                    hf_token = self.config.get_hf_token()
                    if hf_token:
                        cmd.extend(["--hf_token", hf_token])
                    else:
                        self.log_updated.emit("WARNING: Diarization enabled but no HF Token provided.\n")
                
                # Device
                if self.config.get("device") == "cpu":
                    cmd.extend(["--device", "cpu"])

                self.log_updated.emit(f"Command: {' '.join(cmd)}\n")

                from core.translator import translator
                self.log_updated.emit(translator.t("loading_model_tip"))

                current_stage = "Transcribing..."
                self.progress_updated.emit("Transcribing...")
                self.progress_percent.emit(0)

                returncode = -1
                try:
                    # Run subprocess with lock to prevent start/stop race condition
                    with self.lock:
                        if not self._is_running:
                            self.log_updated.emit("Stopped by user.")
                            self.transcription_finished.emit(False, "Stopped by user.")
                            return

                        env = os.environ.copy()
                        if self.config.get("use_hf_mirror"):
                            env["HF_ENDPOINT"] = "https://hf-mirror.com"

                        self.process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.STDOUT, 
                            text=True,
                            encoding="utf-8",
                            errors="replace",
                            env=env,
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0,
                            preexec_fn=os.setsid if os.name != 'nt' else None
                        )

                    while self._is_running:
                        line = self.process.stdout.readline()
                        if not line and self.process.poll() is not None:
                            break
                        if line:
                            self.log_updated.emit(line)
                            
                            # Parse stage
                            line_lower = line.lower()
                            if "diariz" in line_lower:
                                if current_stage != "Diarizing...":
                                    current_stage = "Diarizing..."
                                    self.progress_updated.emit("Diarizing...")
                                    self.progress_percent.emit(0)
                            elif "align" in line_lower:
                                if current_stage != "Aligning...":
                                    current_stage = "Aligning..."
                                    self.progress_updated.emit("Aligning...")
                                    self.progress_percent.emit(0)
                            elif "detect" in line_lower or "transcrib" in line_lower:
                                if current_stage != "Transcribing...":
                                    current_stage = "Transcribing..."
                                    self.progress_updated.emit("Transcribing...")
                                    self.progress_percent.emit(0)

                            # Parse progress percentage
                            match = tqdm_regex.search(line)
                            if match:
                                percent = int(match.group(1))
                                self.progress_percent.emit(percent)

                    self.process.communicate()
                    returncode = self.process.returncode
                finally:
                    with self.lock:
                        if self.process:
                            if self.process.poll() is None:
                                if os.name == 'nt':
                                    try:
                                        subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                                    except Exception:
                                        pass
                                else:
                                    try:
                                        import signal
                                        pgid = os.getpgid(self.process.pid)
                                        os.killpg(pgid, signal.SIGTERM)
                                    except Exception:
                                        try:
                                            self.process.terminate()
                                        except Exception:
                                            pass
                            if self.process.stdout:
                                try:
                                    self.process.stdout.close()
                                except Exception:
                                    pass
                            if returncode == -1 and self.process.returncode is not None:
                                returncode = self.process.returncode
                            self.process = None

                base_name = os.path.splitext(os.path.basename(file))[0]

                # Clean up output files if stopped or error occurred
                if returncode != 0 or not self._is_running:
                    for fmt in ["srt", "txt", "vtt", "tsv", "json"]:
                        partial_file = os.path.join(self.output_dir, f"{base_name}.{fmt}")
                        if os.path.exists(partial_file):
                            try:
                                os.remove(partial_file)
                            except Exception as ex:
                                self.log_updated.emit(f"Failed to delete partial output file {partial_file}: {str(ex)}\n")
                    
                    if not self._is_running:
                        self.log_updated.emit("Stopped by user.")
                        self.transcription_finished.emit(False, "Stopped by user.")
                        return
                    else:
                        self.log_updated.emit(f"Error processing {file}\n")
                        self.transcription_finished.emit(False, f"Error processing {file}")
                        return

                # Clean up unselected formats if 'all' was generated on success
                if returncode == 0 and self._is_running:
                    if isinstance(formats, list) and len(formats) > 1:
                        for fmt in ["srt", "txt", "vtt", "tsv", "json"]:
                            if fmt not in formats:
                                unused_file = os.path.join(self.output_dir, f"{base_name}.{fmt}")
                                if os.path.exists(unused_file):
                                    try:
                                        os.remove(unused_file)
                                    except Exception as ex:
                                        self.log_updated.emit(f"Failed to delete unused format {fmt}: {str(ex)}\n")
            
            if self._is_running:
                self.progress_updated.emit("All files processed successfully.")
                self.log_updated.emit("Finished successfully.\n")
                self.transcription_finished.emit(True, "Success")
                
        except Exception as e:
            self.log_updated.emit(f"Exception: {str(e)}\n")
            self.transcription_finished.emit(False, str(e))
        finally:
            with self.lock:
                if self.process:
                    if self.process.poll() is None:
                        if os.name == 'nt':
                            try:
                                subprocess.call(['taskkill', '/F', '/T', '/PID', str(self.process.pid)])
                            except Exception:
                                pass
                        else:
                            try:
                                import signal
                                pgid = os.getpgid(self.process.pid)
                                os.killpg(pgid, signal.SIGTERM)
                            except Exception:
                                try:
                                    self.process.terminate()
                                except Exception:
                                    pass
                    if self.process.stdout:
                        try:
                            self.process.stdout.close()
                        except Exception:
                            pass
                    self.process = None
