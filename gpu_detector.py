"""
GPU Detection and Auto-Configuration Module
Detects available GPU and recommends optimal settings for SOP generation
"""

import os
import subprocess
import platform
from typing import Dict, Optional


class GPUDetector:
    """Detects GPU capabilities and recommends optimal model configuration."""
    
    def __init__(self):
        self.system = platform.system()
        self.gpu_info = self._detect_gpu()
    
    def _detect_gpu(self) -> Dict:
        """
        Detect GPU information using nvidia-smi.
        
        Returns:
            Dictionary with GPU name, VRAM, and other info
        """
        try:
            # Try to run nvidia-smi and get GPU info
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=name,memory.total', '--format=csv,noheader,nounits'],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                # Parse first GPU (if multiple GPUs, take the first one)
                line = result.stdout.strip().split('\n')[0]
                name, vram_mb = line.split(',')
                
                return {
                    'name': name.strip(),
                    'vram_gb': float(vram_mb.strip()) / 1024,
                    'available': True,
                    'system': self.system
                }
        except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
            print(f"⚠️ GPU detection failed: {e}")
        
        # If detection failed, return default values
        return {
            'name': 'Unknown',
            'vram_gb': 0,
            'available': False,
            'system': self.system
        }
    
    def recommend_model(self) -> str:
        """
        Recommend optimal Ollama vision model based on available VRAM.
        
        Returns:
            Model name (e.g., "llama3.2-vision:11b" or "llama3.2-vision:90b")
        """
        vram = self.gpu_info['vram_gb']
        
        # Model recommendation based on available VRAM
        if vram >= 80:
            # RTX 6000 Blackwell (~96GB) or similar
            return "llama3.2-vision:90b"
        elif vram >= 40:
            # A100 40GB, RTX 6000 Ada
            return "llama3.2-vision:90b"
        elif vram >= 20:
            # RTX 4090 (24GB), RTX 3090 (24GB)
            return "llama3.2-vision:11b"
        elif vram >= 12:
            # RTX 4070 Ti, RTX 3080 Ti
            return "llama3.2-vision:11b"
        else:
            # Less than 12GB - recommend API mode
            return "API_MODE_RECOMMENDED"
    
    def recommend_whisper_model(self) -> str:
        """
        Recommend optimal Whisper model for faster-whisper.
        
        Returns:
            Model size (e.g., "large-v3", "medium", "base")
        """
        vram = self.gpu_info['vram_gb']
        
        # Whisper large-v3 requires ~10GB VRAM for fast processing
        if vram >= 16:
            return "large-v3"
        elif vram >= 8:
            return "medium"
        else:
            return "base"
    
    def print_recommendations(self):
        """Print GPU info and recommended configuration."""
        print("=" * 60)
        print("GPU DETECTION & RECOMMENDATIONS")
        print("=" * 60)
        
        if not self.gpu_info['available']:
            print("❌ No NVIDIA GPU detected")
            print("\n📋 RECOMMENDATION:")
            print("   Use API mode (Gemini + Groq) instead of LOCAL mode")
            print("   Set in .env: AI_MODE=API")
            return
        
        print(f"✅ GPU Detected: {self.gpu_info['name']}")
        print(f"   VRAM: {self.gpu_info['vram_gb']:.1f} GB")
        print(f"   System: {self.gpu_info['system']}")
        
        print("\n📋 RECOMMENDED CONFIGURATION:")
        
        # Vision model recommendation
        vision_model = self.recommend_model()
        if vision_model == "API_MODE_RECOMMENDED":
            print("   ⚠️ Insufficient VRAM for local models")
            print("   Use API mode: AI_MODE=API")
        else:
            print(f"   Vision Model: {vision_model}")
            print(f"   Whisper Model: {self.recommend_whisper_model()}")
            print("\n   Add to .env:")
            print(f"   AI_MODE=LOCAL")
            print(f"   OLLAMA_MODEL={vision_model}")
            print(f"   WHISPER_MODEL={self.recommend_whisper_model()}")
        
        print("=" * 60)
    
    def get_install_commands(self) -> Dict[str, str]:
        """
        Get platform-specific installation commands.
        
        Returns:
            Dictionary with install commands for current platform
        """
        if self.system == "Linux":
            return {
                'ffmpeg': 'sudo apt-get update && sudo apt-get install -y ffmpeg',
                'ollama': 'curl -fsSL https://ollama.com/install.sh | sh',
                'python_deps': 'pip install -r requirements.txt',
                'model': f'ollama pull {self.recommend_model()}'
            }
        elif self.system == "Windows":
            return {
                'ffmpeg': 'winget install Gyan.FFmpeg',
                'ollama': 'Download from https://ollama.com/download/windows',
                'python_deps': 'pip install -r requirements.txt',
                'model': f'ollama pull {self.recommend_model()}'
            }
        else:  # macOS
            return {
                'ffmpeg': 'brew install ffmpeg',
                'ollama': 'brew install ollama',
                'python_deps': 'pip install -r requirements.txt',
                'model': f'ollama pull {self.recommend_model()}'
            }


def detect_and_configure() -> Dict:
    """
    Main function to detect GPU and return recommended configuration.
    
    Returns:
        Configuration dictionary
    """
    detector = GPUDetector()
    detector.print_recommendations()
    
    vision_model = detector.recommend_model()
    
    return {
        'gpu_name': detector.gpu_info['name'],
        'vram_gb': detector.gpu_info['vram_gb'],
        'ai_mode': 'API' if vision_model == 'API_MODE_RECOMMENDED' else 'LOCAL',
        'ollama_model': vision_model if vision_model != 'API_MODE_RECOMMENDED' else None,
        'whisper_model': detector.recommend_whisper_model(),
        'system': detector.system
    }


if __name__ == "__main__":
    # CLI for GPU detection testing
    config = detect_and_configure()
    
    print("\n📝 Configuration Summary:")
    print(f"   AI_MODE={config['ai_mode']}")
    if config['ollama_model']:
        print(f"   OLLAMA_MODEL={config['ollama_model']}")
        print(f"   WHISPER_MODEL={config['whisper_model']}")
