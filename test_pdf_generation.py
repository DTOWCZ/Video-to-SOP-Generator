"""
Test script for PDF generation with already-extracted frames
"""

import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def test_pdf_generation():
    """Test PDF generation using the main pipeline"""
    
    print("=" * 60)
    print("TESTING PDF GENERATION")
    print("=" * 60)
    
    # Import main generator
    from main import VideoToSOPGenerator
    
    # Video path
    video_path = r"D:\SHEZAN\AI\Video-to-SOP Generator\Videos\test_video1.webm"
    
    # Output PDF path
    output_pdf = "test_zipper_repair.pdf"
    
    # Check if video exists
    if not os.path.exists(video_path):
        print(f"❌ Error: Video file not found: {video_path}")
        return False
    
    print(f"✓ Video file found: {video_path}")
    
    # Check API keys
    google_api_key = os.getenv("GOOGLE_API_KEY")
    groq_api_key = os.getenv("GROQ_API_KEY")
    
    if not google_api_key:
        print("❌ Error: GOOGLE_API_KEY not found in .env")
        return False
    print("✓ GOOGLE_API_KEY found")
    
    if not groq_api_key:
        print("⚠️  Warning: GROQ_API_KEY not found (audio transcription will be skipped)")
    else:
        print("✓ GROQ_API_KEY found")
    
    print("\n" + "=" * 60)
    print("Starting SOP generation...")
    print("=" * 60 + "\n")
    
    try:
        # Create generator
        generator = VideoToSOPGenerator()
        
        # Generate SOP
        sop_data = generator.generate_sop(
            video_path=video_path,
            output_pdf=output_pdf,
            context="Zipper repair tutorial",
            company_name="Guiding Bolt"
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
