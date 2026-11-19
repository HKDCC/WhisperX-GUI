import os
import re
import subprocess
import threading
from PyQt6.QtCore import QThread, pyqtSignal

ALL_EXPORT_FORMATS = ["srt", "txt", "vtt", "tsv", "json", "aud"]


def get_local_model_path(model_name):
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
        self.files = list(files)
        self.output_dir = output_dir
        self._is_running = True
        self.process = None
        self.lock = threading.Lock()

    @staticmethod
    def build_command(config, file_path, output_dir, local_model_resolver=get_local_model_path):
        resolved_out_dir = os.path.abspath(output_dir or os.path.dirname(file_path) or ".")
        whisperx_exe = (config.get("whisperx_path") or "whisperx").strip() or "whisperx"
        cmd = [whisperx_exe, file_path]

        model_name = config.get("model_name") or "large-v3"
        local_path = local_model_resolver(model_name) if local_model_resolver else None
        if local_path:
            cmd.extend(["--model", local_path])
        else:
            cmd.extend(["--model", model_name])

        cmd.extend(["--output_dir", resolved_out_dir])

        device = config.get("device") or "cpu"
        cmd.extend(["--device", device])

        compute_type = config.get("compute_type") or ("float16" if device == "cuda" else "int8")
        if device == "cpu" and compute_type == "float16":
            compute_type = "int8"
        cmd.extend(["--compute_type", compute_type])

        formats = config.get("output_formats")
        if isinstance(formats, list) and len(formats) > 1:
            cmd.extend(["--output_format", "all"])
        elif isinstance(formats, list) and len(formats) == 1:
            cmd.extend(["--output_format", formats[0]])
        elif isinstance(formats, str) and formats:
            cmd.extend(["--output_format", formats])
        else:
            cmd.extend(["--output_format", "srt"])

        language = config.get("language") or "auto"
        if language != "auto":
            cmd.extend(["--language", language])

        # Wire VAD filter setting directly to WhisperX VAD parameters
        vad_filter = config.get("vad_filter")
        if vad_filter is False:
            cmd.extend(["--vad_onset", "0.05", "--vad_offset", "0.05", "--no_speech_threshold", "1.0"])
        else:
            cmd.extend(["--vad_method", "pyannote", "--vad_onset", "0.5", "--vad_offset", "0.363"])

        if not config.get("align"):
            cmd.append("--no_align")

        warning_msg = None
        if config.get("diarize"):
            cmd.append("--diarize")
            hf_token = config.get_hf_token()
            if hf_token:
                cmd.extend(["--hf_token", hf_token])
            else:
                warning_msg = "WARNING: Diarization enabled but no HF Token provided.\n"

        cmd.extend(["--print_progress", "True"])

        return cmd, local_path, warning_msg, resolved_out_dir

    def _terminate_process(self, proc):
        if not proc:
            return
        if os.name == "nt":
            try:
                subprocess.call(
                    ["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            except Exception as e:
                print(f"Failed to taskkill process: {e}")
        else:
            try:
                import signal
                pgid = os.getpgid(proc.pid)
                os.killpg(pgid, signal.SIGTERM)
            except Exception as e:
                try:
                    proc.terminate()
                except Exception:
                    pass
                print(f"Failed to terminate process group: {e}")

    def stop(self):
        with self.lock:
            self._is_running = False
            if self.process:
                self._terminate_process(self.process)

    def run(self):
        tqdm_regex = re.compile(r"(\d+)%\s*\|")
        progress_regex = re.compile(r"Progress:\s*(\d+(?:\.\d+)?)%")

        try:
            for file in self.files:
                if not self._is_running:
                    self.log_updated.emit("Stopped by user.")
                    self.transcription_finished.emit(False, "Stopped by user.")
                    return

                self.progress_updated.emit(f"Processing: {os.path.basename(file)}")
                self.log_updated.emit(f"Starting {os.path.basename(file)}...\n")

                cmd, local_path, warning_msg, target_out_dir = self.build_command(
                    self.config, file, self.output_dir
                )
                os.makedirs(target_out_dir, exist_ok=True)

                if local_path:
                    self.log_updated.emit(
                        f"Detected complete offline cache. Using local model path: {local_path}\n"
                    )
                if warning_msg:
                    self.log_updated.emit(warning_msg)

                # Mask HF token when printing command to console log
                safe_cmd_parts = []
                skip_mask = False
                for part in cmd:
                    if skip_mask:
                        safe_cmd_parts.append("***")
                        skip_mask = False
                    elif part == "--hf_token":
                        safe_cmd_parts.append(part)
                        skip_mask = True
                    else:
                        safe_cmd_parts.append(part)
                self.log_updated.emit(f"Command: {' '.join(safe_cmd_parts)}\n")

                from core.translator import translator
                self.log_updated.emit(translator.t("loading_model_tip"))

                current_stage = "Transcribing..."
                self.progress_updated.emit("Transcribing...")
                self.progress_percent.emit(0)

                returncode = -1
                try:
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
                            creationflags=subprocess.CREATE_NO_WINDOW if os.name == "nt" else 0,
                            preexec_fn=os.setsid if os.name != "nt" else None,
                        )

                    while self._is_running:
                        line = self.process.stdout.readline()
                        if not line and self.process.poll() is not None:
                            break
                        if line:
                            self.log_updated.emit(line)

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

                            match = tqdm_regex.search(line)
                            if match:
                                self.progress_percent.emit(min(100, max(0, int(match.group(1)))))
                            else:
                                prog_match = progress_regex.search(line)
                                if prog_match:
                                    self.progress_percent.emit(
                                        min(100, max(0, int(float(prog_match.group(1)))))
                                    )

                    self.process.communicate()
                    returncode = self.process.returncode
                finally:
                    with self.lock:
                        if self.process:
                            if self.process.poll() is None:
                                self._terminate_process(self.process)
                            if self.process.stdout:
                                try:
                                    self.process.stdout.close()
                                except Exception:
                                    pass
                            if returncode == -1 and self.process.returncode is not None:
                                returncode = self.process.returncode
                            self.process = None

                base_name = os.path.splitext(os.path.basename(file))[0]
                formats = self.config.get("output_formats")

                if returncode != 0 or not self._is_running:
                    for fmt in ALL_EXPORT_FORMATS:
                        partial_file = os.path.join(target_out_dir, f"{base_name}.{fmt}")
                        if os.path.exists(partial_file):
                            try:
                                os.remove(partial_file)
                            except Exception as ex:
                                self.log_updated.emit(
                                    f"Failed to delete partial output file {partial_file}: {str(ex)}\n"
                                )

                    if not self._is_running:
                        self.log_updated.emit("Stopped by user.")
                        self.transcription_finished.emit(False, "Stopped by user.")
                        return
                    else:
                        self.log_updated.emit(f"Error processing {file}\n")
                        self.transcription_finished.emit(False, f"Error processing {file}")
                        return

                if returncode == 0 and self._is_running:
                    if isinstance(formats, list) and len(formats) > 1:
                        for fmt in ALL_EXPORT_FORMATS:
                            if fmt not in formats:
                                unused_file = os.path.join(target_out_dir, f"{base_name}.{fmt}")
                                if os.path.exists(unused_file):
                                    try:
                                        os.remove(unused_file)
                                    except Exception as ex:
                                        self.log_updated.emit(
                                            f"Failed to delete unused format {fmt}: {str(ex)}\n"
                                        )

            if self._is_running:
                self.progress_percent.emit(100)
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
                        self._terminate_process(self.process)
                    if self.process.stdout:
                        try:
                            self.process.stdout.close()
                        except Exception:
                            pass
                    self.process = None
