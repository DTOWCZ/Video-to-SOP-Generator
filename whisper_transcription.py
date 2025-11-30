"""
Whisper Audio Transcription using Groq API
High-quality audio transcription for video files
"""

import os
import subprocess
import tempfile
from typing import Optional


def extract_audio_from_video(video_path: str, output_audio_path: str = None) -> Optional[str]:
    """
    Extract audio from video file using ffmpeg
    
    Args:
        video_path: Path to video file
        output_audio_path: Path for output audio file (optional)
        
    Returns:
        Path to extracted audio file
    """
    if output_audio_path is None:
        # Create temporary file
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3')
        output_audio_path = temp_file.name
        temp_file.close()
    
    print(f"Extracting audio from video...")
    
    try:
        # Use ffmpeg to extract audio
        # ffmpeg comes with imageio_ffmpeg which is already installed
        from imageio_ffmpeg import get_ffmpeg_exe
        ffmpeg_path = get_ffmpeg_exe()
        
        # Extract audio as MP3
        cmd = [
            ffmpeg_path,
            '-i', video_path,
            '-vn',  # No video
            '-acodec', 'libmp3lame',  # MP3 codec
            '-ar', '16000',  # 16kHz sample rate (good for speech)
            '-ac', '1',  # Mono
            '-y',  # Overwrite output
            output_audio_path
        ]
        
        # Run ffmpeg
        result = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0
        )
        
        if result.returncode == 0 and os.path.exists(output_audio_path):
            print(f"✓ Audio extracted: {output_audio_path}")
            return output_audio_path
        else:
            print(f"⚠️  Error extracting audio: {result.stderr.decode()}")
            return None
        
    except Exception as e:
        print(f"❌ Error extracting audio: {e}")
        return None


def transcribe_with_whisper_groq(audio_path: str, groq_api_key: str) -> Optional[str]:
    """
    Transcribe audio using Whisper via Groq API
    
    Args:
        audio_path: Path to audio file
        groq_api_key: Groq API key
        
    Returns:
        Transcribed text
    """
    try:
        from groq import Groq
        
        print("Transcribing audio with Whisper (Groq)...")
        
        client = Groq(api_key=groq_api_key)
        
        with open(audio_path, "rb") as file:
            transcription = client.audio.transcriptions.create(
                file=(audio_path, file.read()),
                model="whisper-large-v3",
                temperature=0,
                response_format="verbose_json",
            )
        
        transcript = transcription.text
        print(f"✓ Transcription complete: {len(transcript)} characters")
        
        return transcript
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        return None


def transcribe_video_audio(video_path: str, groq_api_key: str) -> Optional[str]:
    """
    Complete pipeline: Extract audio from video and transcribe it
    
    Args:
        video_path: Path to video file
        groq_api_key: Groq API key
        
    Returns:
        Transcribed text
    """
    print("\n" + "=" * 60)
    print("AUDIO TRANSCRIPTION (Whisper via Groq)")
    print("=" * 60)
    
    # Step 1: Extract audio
    audio_path = extract_audio_from_video(video_path)
    
    if not audio_path:
        return None
    
    try:
        # Step 2: Transcribe with Whisper
        transcript = transcribe_with_whisper_groq(audio_path, groq_api_key)
        
        # Clean up temporary audio file
        if os.path.exists(audio_path):
            os.remove(audio_path)
            print("✓ Temporary audio file cleaned up")
        
        return transcript
        
    except Exception as e:
        print(f"❌ Error during transcription: {e}")
        
        # Clean up
        if os.path.exists(audio_path):
            os.remove(audio_path)
        
        return None


if __name__ == "__main__":
    # Test transcription
    import sys
    from dotenv import load_dotenv
    
    load_dotenv()
    
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        print("ERROR: GROQ_API_KEY not found in .env")
        print("Please add: GROQ_API_KEY=your_key_here")
        sys.exit(1)
    
    if len(sys.argv) < 2:
        print("Usage: python whisper_transcription.py <video_path>")
        sys.exit(1)
    
    video_path = sys.argv[1]
    
    if not os.path.exists(video_path):
        print(f"ERROR: Video file not found: {video_path}")
        sys.exit(1)
    
    transcript = transcribe_video_audio(video_path, groq_api_key)
    
    if transcript:
        print("\n" + "=" * 60)
        print("TRANSCRIPT:")
        print("=" * 60)
        print(transcript)
        print("\n" + "=" * 60)
        print(f"Total characters: {len(transcript)}")
