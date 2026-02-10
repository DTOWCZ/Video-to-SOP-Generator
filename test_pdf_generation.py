"""
Test script for PDF generation with already-extracted frames

Test script for PDF generation - video path via argument or auto-discovery.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def find_test_video() -> str:
    """
    Find a test video file in common locations.
    
    Searches for a test video in common project directories.
    """
    # Common locations to search for test videos
    search_paths = [
        "Videos",
        "test_videos",
        "Example_output",
        ".",
    ]
    
    video_extensions = {".mp4", ".webm", ".avi", ".mov", ".mkv"}
    
    for search_dir in search_paths:
        if os.path.isdir(search_dir):
            for f in os.listdir(search_dir):
                if Path(f).suffix.lower() in video_extensions:
                    return os.path.join(search_dir, f)
    
    return None


def test_pdf_generation():
    """Test PDF generation using the main pipeline"""
    
    print("=" * 60)
    print("TESTING PDF GENERATION")
    print("=" * 60)
    
    # Video path from argument or auto-discovery
    if len(sys.argv) >= 2:
        video_path = sys.argv[1]
    else:
        video_path = find_test_video()
    
    if not video_path or not os.path.exists(video_path):
        print("❌ Error: No test video found!")
        print("\nUsage: python test_pdf_generation.py <video_path>")
        print("\nOr place a video file in one of these directories:")
        print("  - Videos/")
        print("  - test_videos/")
        print("  - current directory")
        return False
    
    # Output PDF path
    output_pdf = "test_sop_output.pdf"
    
    print(f"✓ Video file found: {video_path}")
    
    # Determine AI mode
    ai_mode = os.getenv("AI_MODE", "API").upper()
    print(f"✓ AI Mode: {ai_mode}")
    
    if ai_mode == "API":
        # Check API keys
        google_api_key = os.getenv("GOOGLE_API_KEY")
        groq_api_key = os.getenv("GROQ_API_KEY")
        
        if not google_api_key or google_api_key == "your_google_api_key_here":
            print("❌ Error: GOOGLE_API_KEY not configured in .env")
            return False
        print("✓ GOOGLE_API_KEY found")
        
        if not groq_api_key or groq_api_key == "your_groq_api_key_here":
            print("⚠️  Warning: GROQ_API_KEY not configured (audio transcription will be skipped)")
        else:
            print("✓ GROQ_API_KEY found")
    else:
        print("✓ LOCAL mode – no API keys needed")
    
    print("\n" + "=" * 60)
    print("Starting SOP generation...")
    print("=" * 60 + "\n")
    
    try:
        # Import main generator
        from main import VideoToSOPGenerator
        
        # Create generator
        generator = VideoToSOPGenerator()
        
        # Generate SOP
        sop_data = generator.generate_sop(
            video_path=video_path,
            output_pdf=output_pdf,
            context="Test procedure",
            company_name="Test Company"
        )
        
        print("\n" + "=" * 60)
        print("✓ TEST PASSED!")
        print("=" * 60)
        print(f"PDF generated: {output_pdf}")
        print(f"Title: {sop_data['title']}")
        print(f"Steps: {len(sop_data['steps'])}")
        
        # Check if PDF exists
        if os.path.exists(output_pdf):
            file_size = os.path.getsize(output_pdf)
            print(f"File size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
        
        return True
        
    except Exception as e:
        print("\n" + "=" * 60)
        print("❌ TEST FAILED!")
        print("=" * 60)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_pdf_generation()
    sys.exit(0 if success else 1)
