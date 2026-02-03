#!/bin/bash
# Video-to-SOP Generator - Linux Setup Script
# Optimized for RTX 6000 PRO Blackwell and other NVIDIA GPUs

set -e  # Exit on error

echo "============================================================"
echo "Video-to-SOP Generator - Linux Setup"
echo "============================================================"

# Detect if running on Linux
if [[ "$OSTYPE" != "linux-gnu"* ]]; then
    echo "❌ This script is for Linux only"
    exit 1
fi

# Check for NVIDIA GPU
echo ""
echo "🔍 Checking for NVIDIA GPU..."
if ! command -v nvidia-smi &> /dev/null; then
    echo "⚠️  nvidia-smi not found. Make sure NVIDIA drivers are installed."
    echo "   Install with: sudo apt-get install nvidia-driver-XXX"
    exit 1
fi

nvidia-smi --query-gpu=name,memory.total --format=csv,noheader
echo ""

# Install system dependencies
echo "📦 Installing system dependencies..."
echo ""

# FFmpeg
if ! command -v ffmpeg &> /dev/null; then
    echo "Installing FFmpeg..."
    sudo apt-get update
    sudo apt-get install -y ffmpeg
else
    echo "✓ FFmpeg already installed"
fi

# Python3 and pip
if ! command -v python3 &> /dev/null; then
    echo "Installing Python 3..."
    sudo apt-get install -y python3 python3-pip python3-venv
else
    echo "✓ Python 3 already installed"
    python3 --version
fi

# Create virtual environment
echo ""
echo "🐍 Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✓ Virtual environment created"
else
    echo "✓ Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo ""
echo "📚 Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Install Ollama
echo ""
echo "🤖 Installing Ollama..."
if ! command -v ollama &> /dev/null; then
    echo "Downloading and installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh
else
    echo "✓ Ollama already installed"
    ollama --version
fi

# Start Ollama service
echo ""
echo "🚀 Starting Ollama service..."
if ! pgrep -x "ollama" > /dev/null; then
    echo "Starting Ollama in background..."
    nohup ollama serve > /dev/null 2>&1 &
    sleep 3
    echo "✓ Ollama service started"
else
    echo "✓ Ollama is already running"
fi

# Detect GPU and recommend model
echo ""
echo "🔍 Detecting GPU and recommending model..."
python3 gpu_detector.py

# Prompt for model download
echo ""
echo "============================================================"
echo "📥 Model Download"
echo "============================================================"
read -p "Do you want to download the recommended vision model now? [y/N] " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    # Run GPU detector to get recommendation
    MODEL=$(python3 -c "from gpu_detector import GPUDetector; d = GPUDetector(); print(d.recommend_model())")
    
    if [ "$MODEL" != "API_MODE_RECOMMENDED" ]; then
        echo "Downloading model: $MODEL"
        echo "⚠️  This may take several minutes (10-45GB download)..."
        ollama pull "$MODEL"
        echo "✓ Model downloaded successfully"
    else
        echo "⚠️  API mode recommended - skipping model download"
    fi
fi

# Create .env file if it doesn't exist
echo ""
echo "⚙️  Configuration..."
if [ ! -f ".env" ]; then
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ Created .env file"
    echo ""
    echo "📝 Please edit .env and configure:"
    echo "   - AI_MODE (LOCAL or API)"
    echo "   - API keys if using API mode"
else
    echo "✓ .env file already exists"
fi

# Final instructions
echo ""
echo "============================================================"
echo "✅ Setup Complete!"
echo "============================================================"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1. Activate virtual environment (if not already active):"
echo "   source venv/bin/activate"
echo ""
echo "2. Edit .env file with your configuration:"
echo "   nano .env"
echo ""
echo "3. Run the application:"
echo "   python main.py path/to/video.mp4"
echo ""
echo "============================================================"
