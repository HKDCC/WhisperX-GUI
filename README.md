# WhisperX GUI

<div align="center">

**高精度、本地优先的 WhisperX 语音识别与智能字幕工作台**  
*A Modern, High-Performance Desktop Client for WhisperX Speech Recognition & Subtitle Generation.*

[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.10%20%7C%203.11%20%7C%203.12-blue)](https://www.python.org/)
[![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green.svg)](https://pypi.org/project/PyQt6/)

</div>

---

## ✨ 核心亮点 (Key Features)

- 🎙️ **本地优先与极致隐私**：所有音频处理与语音推理均在本地完成，无数据上传，确保数据资产 0 泄露。
- ⚡ **VAD 静音过滤**：集成语音活动检测（Voice Activity Detection），自动剔除无声冗余，杜绝字幕幻觉与复读卡死。
- 🎯 **词级时间戳对齐 (Word-level Alignment)**：利用音素对齐模型微调时间轴，实现音画毫秒级严丝合缝。
- 👥 **说话人角色分离 (Speaker Diarization)**：自动识别并标注音频中多位发言人身份（如 `Speaker_0`、`Speaker_1`）。
- 🚀 **国内一键镜像加速 (HF Mirror)**：内置 HuggingFace 镜像源加速开关，国内网络免配置高速下载模型。
- 🎨 **现代化美学界面**：采用精心调优的 iOS / macOS 现代质感设计，支持日间/夜间双主题无缝切换与拖拽导入。
- 📦 **全格式多路导出**：一键生成 `.srt`、`.txt`、`.vtt`、`.tsv`、`.json` 多维字幕与文本。

---

## 🖥️ 界面预览 (UI Showcase)

- **主界面**：支持批量文件拖拽、实时任务进度环、阶段状态解析（转录 / 对齐 / 角色分离）。
- **设置抽屉**：硬件加速（CUDA / CPU）、计算精度（float16 / int8）、模型选型（tiny ~ large-v3）及 HuggingFace Token 凭证管理。

---

## 🚀 快速启动 (Quick Start)

### 1. 前置依赖 (Prerequisites)

- **Python**: 3.10 ~ 3.12
- **FFmpeg**: 系统需安装 FFmpeg 并加入系统环境变量 `PATH`。
  ```bash
  # Windows (via Scoop / Winget / Chocolatey)
  winget install Gyan.FFmpeg
  ```
- **CUDA 环境（可选，GPU 加速推荐）**：
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu121
  ```

### 2. 安装与运行 (Installation)

```bash
# 克隆仓库
git clone https://github.com/HKDCC/WhisperX-GUI.git
cd WhisperX-GUI

# 安装依赖
pip install -r requirements.txt
pip install whisperx

# 启动客户端
python main.py
```

---

## ⚙️ 配置文件 (Configuration)

应用首次启动时会在系统用户目录（Windows: `%LOCALAPPDATA%\WhisperX_GUI\config.json`）自动初始化配置文件。

参考配置 [`config.example.json`](config.example.json)：

```json
{
    "model_name": "large-v3",
    "device": "cuda",
    "compute_type": "float16",
    "output_formats": ["srt", "txt"],
    "vad_filter": true,
    "align": true,
    "diarize": false,
    "language": "auto",
    "ui_language": "zh",
    "theme_mode": "light",
    "use_hf_mirror": true,
    "whisperx_path": "whisperx"
}
```

---

## 📦 项目结构 (Project Structure)

```text
WhisperX-GUI/
├── core/                  # 核心调度层
│   ├── config_manager.py  # 配置管理与硬件状态探测
│   ├── translator.py      # 中英多语言翻译引擎
│   └── whisper_runner.py  # 子进程异步执行器与实时输出解析
├── ui/                    # 界面视图层
│   ├── assets/            # 图标与静态资源
│   ├── components/        # 自定义控件 (DropZone, Switch, SettingsPanel 等)
│   ├── crash_dialog.py    # 友好崩溃与环境缺失拦截对话框
│   ├── main_window.py     # 主窗口业务逻辑与流式控制台
│   └── styles.py          # 现代质感 QSS 样式表
├── main.py                # 应用程序入口
├── requirements.txt       # Python 依赖清单
├── config.example.json    # 默认配置模板
└── LICENSE                # MIT 开源协议
```

---

## 📄 开源协议 (License)

本项目基于 [MIT License](LICENSE) 协议开源。
