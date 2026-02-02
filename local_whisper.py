"""
Local Whisper Transcription using faster-whisper
GPU-accelerated audio transcription for video files
Runs entirely on local RTX 6000 Blackwell GPU
"""

import os
import subprocess
import tempfile
from typing import Optional, List, Dict
from pathlib import Path


class LocalWhisperTranscriber:
    """
    Lokální Whisper transkripce přes faster-whisper.
    Využívá GPU pro maximální rychlost.
    """
    
    def __init__(
        self,
        model_size: str = "large-v3",
        compute_type: str = "float16",
        device: str = "cuda"
    ):
        """
        Inicializace lokálního Whisper modelu.
        
        Args:
            model_size: Velikost modelu (tiny, base, small, medium, large-v3)
            compute_type: Typ výpočtu (float16, int8, int8_float16)
            device: Zařízení pro inference (cuda, cpu)
        """
        self.model_size = model_size
        self.compute_type = compute_type
        self.device = device
        self.model = None
        
    def _load_model(self):
        """Lazy loading modelu - načte se až při prvním použití."""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                
                print(f"Loading Whisper model: {self.model_size} ({self.compute_type})...")
                
                # CZ: Načtení modelu na GPU s optimalizovaným compute typem
                self.model = WhisperModel(
                    self.model_size,
                    device=self.device,
                    compute_type=self.compute_type
                )
                
                print(f"✓ Whisper model loaded on {self.device.upper()}")
                
            except ImportError:
                raise ImportError(
                    "faster-whisper not installed. Run: pip install faster-whisper"
                )
            except Exception as e:
                raise RuntimeError(f"Failed to load Whisper model: {e}")
    
    def transcribe(
        self,
        audio_path: str,
        language: str = None,
        task: str = "transcribe"
    ) -> str:
        """
        Přepis audio souboru na text s časovými značkami.
        
        Args:
            audio_path: Cesta k audio souboru
            language: Jazyk nahrávky (None = auto-detect)
            task: "transcribe" nebo "translate" (do angličtiny)
            
        Returns:
            Formátovaný přepis s časovými značkami
        """
        self._load_model()
        
        print(f"Transcribing: {audio_path}")
        
        # CZ: Spuštění transkripce s timestamps
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            beam_size=5,
            word_timestamps=False,  # CZ: Segmenty stačí, slova by bylo moc
            vad_filter=True,  # CZ: Filtruje ticho pro rychlejší zpracování
        )
        
        # CZ: Detekovaný jazyk
        print(f"✓ Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        # CZ: Formátování výstupu s časovými značkami
        formatted_segments = []
        for segment in segments:
            start_time = segment.start
            end_time = segment.end
            text = segment.text.strip()
            formatted_segments.append(f"[{start_time:.1f}s - {end_time:.1f}s]: {text}")
        
        formatted_transcript = "\n".join(formatted_segments)
        
        print(f"✓ Transcription complete: {len(formatted_segments)} segments")
        
        return formatted_transcript
    
    def get_segments(
        self,
        audio_path: str,
        language: str = None
    ) -> List[Dict]:
        """
        Získá detailní segmenty s metadaty.
        
        Returns:
            List slovníků s 'start', 'end', 'text'
        """
        self._load_model()
        
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            beam_size=5,
            vad_filter=True,
        )
        
        result = []
        for segment in segments:
            result.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip()
            })
        
        return result


def extract_audio_ffmpeg(video_path: str, output_path: str = None) -> Optional[str]:
    """
    Extrahuje audio z videa pomocí FFmpeg.
    
    Args:
        video_path: Cesta k video souboru
        output_path: Cesta pro výstupní audio (optional)
        
    Returns:
        Cesta k extrahovanému audio souboru
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_path = temp_file.name
        temp_file.close()
    
    print(f"Extracting audio from video...")
    
    try:
        # CZ: Pokusíme se použít systémový FFmpeg
        ffmpeg_cmd = "ffmpeg"
        
        # CZ: Pokud není v PATH, zkusíme imageio_ffmpeg
        try:
            result = subprocess.run(
                [ffmpeg_cmd, "-version"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except FileNotFoundError:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_cmd = get_ffmpeg_exe()
        
        # CZ: Extrakce audia jako MP3, mono, 16kHz (optimální pro speech)
        cmd = [
            ffmpeg_cmd,
            '-i', video_path,
            '-vn',  # CZ: Bez videa
            '-acodec', 'libmp3lame',
            '-ar', '16000',  # CZ: 16kHz sample rate
            '-ac', '1',  # CZ: Mono
            '-y',  # CZ: Přepsat výstup
            output_path
        ]
        
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode == 0 and os.path.exists(output_path):
            print(f"✓ Audio extracted: {output_path}")
            return output_path
        else:
            print(f"⚠️ Error extracting audio: {result.stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return None


def transcribe_video_local(
    video_path: str,
    model_size: str = None,
    compute_type: str = None
) -> Optional[str]:
    """
    Kompletní pipeline: Extrakce audia + lokální Whisper transkripce.
    
    Args:
        video_path: Cesta k video souboru
        model_size: Velikost Whisper modelu (default z .env)
        compute_type: Typ výpočtu (default z .env)
        
    Returns:
        Formátovaný přepis s časovými značkami
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # CZ: Načtení konfigurace z .env nebo použití defaultů
    model_size = model_size or os.getenv("WHISPER_MODEL", "large-v3")
    compute_type = compute_type or os.getenv("WHISPER_COMPUTE_TYPE", "float16")
    
    print("\n" + "=" * 60)
    print("LOCAL AUDIO TRANSCRIPTION (faster-whisper on GPU)")
    print("=" * 60)
    print(f"Model: {model_size}, Compute: {compute_type}")
    
    # CZ: Krok 1 - Extrakce audia
    audio_path = extract_audio_ffmpeg(video_path)
    
    if not audio_path:
        return None
    
    try:
        # CZ: Krok 2 - Transkripce přes faster-whisper
        transcriber = LocalWhisperTranscriber(
            model_size=model_size,
            compute_type=compute_type,
            device="cuda"
        )
        
        transcript = transcriber.transcribe(audio_path)
        
        # CZ: Cleanup dočasného audio souboru
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("✓ Temporary audio file cleaned up")
        
        return transcript
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        
        # CZ: Cleanup při chybě
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return None


# ============================================================
# Test / CLI
# ============================================================
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python local_whisper.py <video_path>")
        print("\nThis script uses local GPU for Whisper transcription.")
        print("No API keys required!")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        sys.exit(1)
    
    transcript = transcribe_video_local(video_path)
    
    if transcript:
        print("\n" + "=" * 60)
        print("TRANSCRIPT:")
        print("=" * 60)
        print(transcript)
        print("\n" + "=" * 60)
        print(f"Total characters: {len(transcript)}")
    else:
        print("Transcription failed!")
        sys.exit(1)
