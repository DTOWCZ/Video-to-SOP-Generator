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
    Local Whisper transcription via faster-whisper.
    Uses GPU for maximum speed.
    """
    
    def __init__(
        self,
        model_size: str = "large-v3",
        compute_type: str = "float16",
        device: str = "cuda"
    ):
        """
        Initialize the local Whisper model.
        
        Args:
            model_size: Model size (tiny, base, small, medium, large-v3)
            compute_type: Computation type (float16, int8, int8_float16)
            device: Inference device (cuda, cpu)
        """
        self.model_size = model_size
        self.compute_type = compute_type
        self.device = device
        self.model = None
        
    def _load_model(self):
        """Lazy loading of the model - loads only on first use."""
        if self.model is None:
            try:
                from faster_whisper import WhisperModel
                
                print(f"Loading Whisper model: {self.model_size} ({self.compute_type})...")
                
                # Load model on GPU with optimized compute type
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
        Transcription of audio file to text with timestamps.
        
        Args:
            audio_path: Path to audio file
            language: Audio language (None = auto-detect)
            task: "transcribe" or "translate" (to English)
            
        Returns:
            Formatted transcript with timestamps
        """
        self._load_model()
        
        print(f"Transcribing: {audio_path}")
        
        # Run transcription with timestamps
        segments, info = self.model.transcribe(
            audio_path,
            language=language,
            task=task,
            beam_size=5,
            word_timestamps=False,  # Segments are enough, words would be too many
            vad_filter=True,  # Filter silence for faster processing
        )
        
        # Detected language
        print(f"✓ Detected language: {info.language} (probability: {info.language_probability:.2f})")
        
        # Format output with timestamps
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
        Get detailed segments with metadata.
        
        Returns:
            List of dictionaries with 'start', 'end', 'text'
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
    Extract audio from video using FFmpeg.
    
    Args:
        video_path: Path to video file
        output_path: Path for output audio (optional)
        
    Returns:
        Path to extracted audio file
    """
    if output_path is None:
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_path = temp_file.name
        temp_file.close()
    
    print(f"Extracting audio from video...")
    
    try:
        # Try to use system FFmpeg
        ffmpeg_cmd = "ffmpeg"
        
        # If not in PATH, try imageio_ffmpeg
        try:
            result = subprocess.run(
                [ffmpeg_cmd, "-version"],
                capture_output=True,
                creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
            )
        except FileNotFoundError:
            from imageio_ffmpeg import get_ffmpeg_exe
            ffmpeg_cmd = get_ffmpeg_exe()
        
        # Extract audio as MP3, mono, 16kHz (optimal for speech)
        cmd = [
            ffmpeg_cmd,
            '-i', video_path,
            '-vn',  # No video stream
            '-acodec', 'libmp3lame',
            '-ar', '16000',  # 16kHz sample rate (optimal for speech)
            '-ac', '1',  # Mono channel
            '-y',  # Overwrite output
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
    Complete pipeline: Audio extraction + local Whisper transcription.
    
    Args:
        video_path: Path to video file
        model_size: Whisper model size (default from .env)
        compute_type: Computation type (default from .env)
        
    Returns:
        Formatted transcript with timestamps
    """
    from dotenv import load_dotenv
    load_dotenv()
    
    # Load configuration from .env or use defaults
    model_size = model_size or os.getenv("WHISPER_MODEL", "large-v3")
    compute_type = compute_type or os.getenv("WHISPER_COMPUTE_TYPE", "float16")
    
    print("\n" + "=" * 60)
    print("LOCAL AUDIO TRANSCRIPTION (faster-whisper on GPU)")
    print("=" * 60)
    print(f"Model: {model_size}, Compute: {compute_type}")
    
    # Step 1 - Audio extraction
    audio_path = extract_audio_ffmpeg(video_path)
    
    if not audio_path:
        return None
    
    try:
        # Step 2 - Transcription via faster-whisper
        transcriber = LocalWhisperTranscriber(
            model_size=model_size,
            compute_type=compute_type,
            device="cuda"
        )
        
        transcript = transcriber.transcribe(audio_path)
        
        # Cleanup temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("✓ Temporary audio file cleaned up")
        
        return transcript
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        
        # Cleanup on error
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
