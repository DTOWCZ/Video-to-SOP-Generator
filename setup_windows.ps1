# Video-to-SOP Generator - Windows Setup Script
# Optimized for RTX 4090 and other NVIDIA GPUs

# Cz: Ověření spuštění v PowerShellu
$ErrorActionPreference = "Stop"

Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "Video-to-SOP Generator - Windows Setup" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host ""

# Cz: Kontrola NVIDIA GPU
Write-Host "🔍 Checking for NVIDIA GPU..." -ForegroundColor Yellow
try {
    $gpuInfo = nvidia-smi --query-gpu=name,memory.total --format=csv,noheader 2>&1
    Write-Host $gpuInfo -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "⚠️  nvidia-smi not found. Make sure NVIDIA drivers are installed." -ForegroundColor Red
    Write-Host "   Download from: https://www.nvidia.com/Download/index.aspx" -ForegroundColor Yellow
    exit 1
}

# Cz: Kontrola Pythonu
Write-Host "🐍 Checking Python installation..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ Python not found!" -ForegroundColor Red
    Write-Host "   Download from: https://www.python.org/downloads/" -ForegroundColor Yellow
    Write-Host "   Make sure to check 'Add Python to PATH' during installation" -ForegroundColor Yellow
    exit 1
}

# Cz: Kontrola FFmpeg
Write-Host ""
Write-Host "🎬 Checking FFmpeg installation..." -ForegroundColor Yellow
try {
    $ffmpegVersion = ffmpeg -version 2>&1 | Select-Object -First 1
    Write-Host "✓ FFmpeg installed" -ForegroundColor Green
} catch {
    Write-Host "⚠️  FFmpeg not found" -ForegroundColor Yellow
    Write-Host "   Installing via winget..." -ForegroundColor Yellow
    try {
        winget install Gyan.FFmpeg
        Write-Host "✓ FFmpeg installed successfully" -ForegroundColor Green
        Write-Host "⚠️  You may need to restart your terminal" -ForegroundColor Yellow
    } catch {
        Write-Host "❌ Could not install FFmpeg automatically" -ForegroundColor Red
        Write-Host "   Please download manually from: https://www.ffmpeg.org/download.html" -ForegroundColor Yellow
    }
}

# Cz: Vytvoření virtuálního prostředí
Write-Host ""
Write-Host "📦 Setting up Python virtual environment..." -ForegroundColor Yellow
if (-not (Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created" -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists" -ForegroundColor Green
}

# Cz: Aktivace virtuálního prostředí
Write-Host ""
Write-Host "⚡ Activating virtual environment..." -ForegroundColor Yellow
& .\venv\Scripts\Activate.ps1

# Cz: Instalace Python závislostí
Write-Host ""
Write-Host "📚 Installing Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r requirements.txt
Write-Host "✓ Python dependencies installed" -ForegroundColor Green

# Cz: Kontrola Ollama
Write-Host ""
Write-Host "🤖 Checking Ollama installation..." -ForegroundColor Yellow
try {
    $ollamaVersion = ollama --version 2>&1
    Write-Host "✓ Ollama already installed: $ollamaVersion" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Ollama not found" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "   Please install Ollama manually:" -ForegroundColor Yellow
    Write-Host "   1. Download from: https://ollama.com/download/windows" -ForegroundColor Cyan
    Write-Host "   2. Run the installer" -ForegroundColor Cyan
    Write-Host "   3. Restart your terminal" -ForegroundColor Cyan
    Write-Host ""
    $installNow = Read-Host "Open download page in browser now? [Y/n]"
    if ($installNow -ne 'n') {
        Start-Process "https://ollama.com/download/windows"
    }
}

# Cz: Detekce GPU a doporučení modelu
Write-Host ""
Write-Host "🔍 Detecting GPU and recommending configuration..." -ForegroundColor Yellow
python gpu_detector.py

# Cz: Stažení modelu
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
Write-Host "📥 Model Download" -ForegroundColor Cyan
Write-Host "============================================================" -ForegroundColor Cyan
$downloadModel = Read-Host "Do you want to download the recommended vision model now? [y/N]"
if ($downloadModel -eq 'y' -or $downloadModel -eq 'Y') {
    # Cz: Získání doporučeného modelu z GPU detectoru
    $recommendedModel = python -c "from gpu_detector import GPUDetector; d = GPUDetector(); print(d.recommend_model())"
    
    if ($recommendedModel -ne "API_MODE_RECOMMENDED") {
        Write-Host "Downloading model: $recommendedModel" -ForegroundColor Yellow
        Write-Host "⚠️  This may take several minutes (10-45GB download)..." -ForegroundColor Yellow
        ollama pull $recommendedModel
        Write-Host "✓ Model downloaded successfully" -ForegroundColor Green
    } else {
        Write-Host "⚠️  API mode recommended - skipping model download" -ForegroundColor Yellow
    }
}

# Cz: Vytvoření .env souboru
Write-Host ""
Write-Host "⚙️  Configuration..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "✓ Created .env file" -ForegroundColor Green
    Write-Host ""
    Write-Host "📝 Please edit .env and configure:" -ForegroundColor Cyan
    Write-Host "   - AI_MODE (LOCAL or API)" -ForegroundColor Cyan
    Write-Host "   - API keys if using API mode" -ForegroundColor Cyan
} else {
    Write-Host "✓ .env file already exists" -ForegroundColor Green
}

# Cz: Závěrečné instrukce
Write-Host ""
Write-Host "============================================================" -ForegroundColor Green
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "============================================================" -ForegroundColor Green
Write-Host ""
Write-Host "📋 Next Steps:" -ForegroundColor Cyan
Write-Host ""
Write-Host "1. Edit .env file with your configuration:" -ForegroundColor White
Write-Host "   notepad .env" -ForegroundColor Gray
Write-Host ""
Write-Host "2. Activate virtual environment (if not already active):" -ForegroundColor White
Write-Host "   .\venv\Scripts\Activate.ps1" -ForegroundColor Gray
Write-Host ""
Write-Host "3. Run the application:" -ForegroundColor White
Write-Host "   python main.py path\to\video.mp4" -ForegroundColor Gray
Write-Host ""
Write-Host "============================================================" -ForegroundColor Cyan
