# Platform-Specific Setup Guide

## Quick Start

### Windows (RTX 4090)
```powershell
# Run automated setup
.\setup_windows.ps1
```

### Linux (RTX 6000 PRO Blackwell)
```bash
# Make script executable
chmod +x setup_linux.sh

# Run automated setup
./setup_linux.sh
```

---

## Manual Setup

### Windows

#### Prerequisites
- **Python 3.8+**: https://www.python.org/downloads/
- **NVIDIA Drivers**: https://www.nvidia.com/Download/index.aspx
- **Git**: https://git-scm.com/download/win

#### Installation Steps

1. **Install FFmpeg**
   ```powershell
   winget install Gyan.FFmpeg
   ```
   Or download manually: https://www.ffmpeg.org/download.html

2. **Install Ollama**
   - Download: https://ollama.com/download/windows
   - Run installer
   - Verify: `ollama --version`

3. **Clone Repository**
   ```powershell
   git clone https://github.com/DTOWCZ/Video-to-SOP-Generator.git
   cd Video-to-SOP-Generator
   ```

4. **Create Virtual Environment**
   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

5. **Install Dependencies**
   ```powershell
   pip install -r requirements.txt
   ```

6. **Detect GPU and Get Recommendations**
   ```powershell
   python gpu_detector.py
   ```

7. **Download Vision Model**
   - For RTX 4090 (24GB):
     ```powershell
     ollama pull llama3.2-vision:11b
     ```

8. **Configure Environment**
   ```powershell
   copy .env.example .env
   notepad .env
   ```
   Set `AI_MODE=LOCAL`

9. **Run Application**
   ```powershell
   python main.py path\to\video.mp4
   ```

---

### Linux

#### Prerequisites
- **Python 3.8+**: `sudo apt install python3 python3-pip python3-venv`
- **NVIDIA Drivers**: Should already be installed (check with `nvidia-smi`)
- **CUDA**: Already installed (verified from your output)

#### Installation Steps

1. **Install FFmpeg**
   ```bash
   sudo apt update
   sudo apt install ffmpeg
   ```

2. **Install Ollama**
   ```bash
   curl -fsSL https://ollama.com/install.sh | sh
   ```

3. **Start Ollama Service**
   ```bash
   # Start in background
   ollama serve &
   
   # Or use systemd (recommended)
   sudo systemctl enable ollama
   sudo systemctl start ollama
   ```

4. **Clone Repository**
   ```bash
   git clone https://github.com/DTOWCZ/Video-to-SOP-Generator.git
   cd Video-to-SOP-Generator
   ```

5. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

6. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

7. **Detect GPU and Get Recommendations**
   ```bash
   python gpu_detector.py
   ```

8. **Download Vision Model**
   - For RTX 6000 Blackwell (96GB):
     ```bash
     ollama pull llama3.2-vision:90b
     ```
   - This will download ~45GB, optimized for your GPU

9. **Configure Environment**
   ```bash
   cp .env.example .env
   nano .env
   ```
   Set `AI_MODE=LOCAL` and leave `OLLAMA_MODEL=` empty for auto-detection

10. **Run Application**
    ```bash
    python main.py path/to/video.mp4
    ```

---

## GPU-Specific Recommendations

### RTX 4090 (24GB VRAM) - Windows
```ini
AI_MODE=LOCAL
OLLAMA_MODEL=llama3.2-vision:11b
WHISPER_MODEL=large-v3
WHISPER_COMPUTE_TYPE=float16
```

**Expected Performance:**
- Video (4 min) → SOP: ~60-90 seconds
- Whisper: ~5-8s
- VLM Analysis: ~25-35s
- Quality: Excellent

### RTX 6000 PRO Blackwell (96GB VRAM) - Linux
```ini
AI_MODE=LOCAL
OLLAMA_MODEL=llama3.2-vision:90b
WHISPER_MODEL=large-v3
WHISPER_COMPUTE_TYPE=float16
```

**Expected Performance:**
- Video (4 min) → SOP: ~30-50 seconds
- Whisper: ~3-5s
- VLM Analysis: ~15-25s
- Quality: Maximum (largest model)

---

## Troubleshooting

### Windows

**Issue: "nvidia-smi not found"**
- Install NVIDIA drivers from https://www.nvidia.com/Download/index.aspx

**Issue: "Ollama connection refused"**
- Make sure Ollama is running (check system tray icon)
- Restart Ollama Desktop app

**Issue: "FFmpeg not found"**
- Add FFmpeg to PATH or reinstall via `winget install Gyan.FFmpeg`

### Linux

**Issue: "Ollama server not responding"**
```bash
# Check if Ollama is running
ps aux | grep ollama

# Start Ollama
ollama serve &

# Or use systemd
sudo systemctl status ollama
sudo systemctl start ollama
```

**Issue: "CUDA out of memory"**
- You're using too large a model for your GPU
- Run `python gpu_detector.py` to get the right model
- Or manually set a smaller model in `.env`

**Issue: "Permission denied on setup_linux.sh"**
```bash
chmod +x setup_linux.sh
```

---

## Switching Between Systems

You can use the same repository on both Windows and Linux machines. The application automatically detects the platform and adjusts paths accordingly.

**On Windows:**
```powershell
python main.py C:\Videos\training.mp4
```

**On Linux:**
```bash
python main.py /home/user/Videos/training.mp4
```

The `.env` file is compatible across both platforms - just adjust model settings based on the GPU.
