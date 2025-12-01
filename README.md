# Video-to-SOP Generator 🎬 → 📄

Convert training videos into professional Standard Operating Procedure (SOP) manuals automatically using AI.

## ✨ What's New in v2.0

- ⚡ **15x Faster** - FFmpeg-powered frame extraction
- 🎯 **Better Accuracy** - Timestamped audio transcription
- ✅ **Complete Procedures** - Includes reassembly and verification steps
- 📊 **Timing Display** - See performance breakdown for each phase
- 🧹 **Auto Cleanup** - Automatic frame cleanup after generation

## Overview

This tool uses multimodal AI (Gemini 1.5 Flash) and Whisper to watch industrial/manufacturing training videos and generate step-by-step instruction manuals with screenshots.

## Features

- 🎥 **FFmpeg Video Processing**: Extracts key frames 15x faster than traditional methods
- 🎙️ **Timestamped Audio**: High-quality speech-to-text with precise timestamps using Whisper AI
- 🤖 **AI Analysis**: Uses Gemini 1.5 Flash to understand and document complete procedures
- 📄 **Professional PDFs**: Creates polished SOP manuals with images and clear instructions
- ⚡ **Fast Processing**: 4-minute video → Complete SOP in ~2 minutes
- 🔒 **Safety Notes**: Automatically identifies safety considerations
- ✅ **Complete Procedures**: Includes disassembly, repair, reassembly, and verification steps
- 🧹 **Auto Cleanup**: Automatically removes temporary frames after generation

## Performance

**4-minute video (1920x1080):**
- Audio Transcription: ~30s
- Frame Extraction: ~8s (15x faster with FFmpeg!)
- AI Analysis: ~75s
- PDF Generation: ~5s
- **Total: ~2 minutes** ⚡

## Installation

### Prerequisites

- Python 3.8+
- FFmpeg ([Installation guide](FFMPEG_SETUP.md))
- Google Gemini API key ([Get one here](https://makersuite.google.com/app/apikey))
- Groq API key for Whisper transcription ([Get one here](https://console.groq.com/))

### Setup

1. **Clone or download this repository**

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv myvenv
   .\myvenv\Scripts\activate  # Windows
   source myvenv/bin/activate  # Linux/Mac
   ```

3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Install FFmpeg** (for fast frame extraction):
   - Windows: `choco install ffmpeg` or see [FFMPEG_SETUP.md](FFMPEG_SETUP.md)
   - Verify: `ffmpeg -version`

5. **Set up your API keys**:
   - Copy `.env.example` to `.env`
   - Add your API keys:
     ```
     GOOGLE_API_KEY=your_google_gemini_api_key_here
     GROQ_API_KEY=your_groq_api_key_here
     ```

## Usage

### Basic Usage

```bash
python main.py path/to/video.mp4
```

This will:
1. Extract audio and create timestamped transcript
2. Extract key frames (fast with FFmpeg!)
3. Analyze with AI to generate complete procedure
4. Generate professional PDF
5. Automatically cleanup temporary frames

### Advanced Usage

```bash
python main.py video.mp4 \
  --output my_sop.pdf \
  --context "Car Tire Repair and Replacement" \
  --company "Shezan Car Garage"
```

### Command-Line Options

| Option | Description | Default |
|--------|-------------|---------|
| `video` | Path to input video file | (required) |
| `-o, --output` | Output PDF filename | `output_sop.pdf` |
| `-c, --context` | Task context for better analysis | Auto-detected |
| `--company` | Company name for PDF header | "Your Company" |

## How It Works

### Pipeline

```
Video Input → Frame Extraction → AI Analysis → PDF Generation
```

### 1. Video Processing (`video_processor.py`)
- Extracts frames at 1-2 second intervals
- Resizes images for optimal AI processing
- Maintains timestamp information

### 2. AI Analysis (`sop_analyzer.py`)
- Sends frames/video to Gemini 1.5 Pro
- Uses specialized prompt for SOP generation
- Returns structured JSON with steps and timestamps

### 3. PDF Generation (`pdf_generator.py`)
- Creates professional document layout
- Embeds images at relevant steps
- Includes safety notes and table of contents

## Project Structure

```
Video-to-SOP Generator/
├── main.py                 # Main application
├── video_processor.py      # Frame extraction
├── sop_analyzer.py        # AI analysis
├── pdf_generator.py       # PDF creation
├── requirements.txt       # Dependencies
├── .env.example          # API key template
└── README.md             # This file
```

## Example Output

Here's what the generated SOP looks like:

### 📄 Sample: Flat Tire Repair SOP

**Input:** 4-minute training video  
**Output:** Professional 18-page SOP manual  
**Processing Time:** 2 minutes

#### Cover Page
<img src="Example_output/test_cleanup_page-0001.jpg" width="400" alt="SOP Cover Page">

*Professional cover page with title, company name, and date*

#### Table of Contents & Safety Notes
<img src="Example_output/test_cleanup_page-0002.jpg" width="400" alt="Table of Contents">

*Automatically generated table of contents with safety considerations*

#### Procedure Steps with Images
<img src="Example_output/test_cleanup_page-0003.jpg" width="400" alt="Step 1">
<img src="Example_output/test_cleanup_page-0005.jpg" width="400" alt="Step 3">
<img src="Example_output/test_cleanup_page-0008.jpg" width="400" alt="Step 6">

*Each step includes clear instructions, timestamp reference, and corresponding image from the video*

#### Complete Procedure
<img src="Example_output/test_cleanup_page-0015.jpg" width="400" alt="Final Steps">

*Includes reassembly and verification steps for complete procedures*

**[View All Pages →](Example_output/)**

### What's Included in Every SOP:

- ✅ **Cover Page** - Professional title page with company branding
- ✅ **Table of Contents** - Easy navigation to all sections
- ✅ **Safety Section** - Automatically identified safety considerations
- ✅ **Step-by-Step Instructions** - Clear, actionable steps with:
  - Numbered steps in logical order
  - Timestamp references from video
  - High-quality images showing each action
  - Reasoning/tips for each step
- ✅ **Complete Procedures** - Includes:
  - Disassembly steps
  - Repair/maintenance actions
  - Reassembly in correct order
  - Final verification and testing

---

## Project Structure

```
Video-to-SOP Generator/
├── main.py                    # Main application
├── video_processor.py         # Frame extraction (FFmpeg)
├── sop_analyzer.py           # AI analysis (Gemini)
├── whisper_transcription.py  # Audio transcription (Whisper)
├── pdf_generator.py          # PDF creation
├── requirements.txt          # Dependencies
├── .env.example             # API key template
├── Example_output/          # Sample output PDFs (18 pages)
└── README.md                # This file
```

---

## How It Works

### Pipeline

```
Video Input → Audio Transcription → Frame Extraction → AI Analysis → PDF Generation → Cleanup
     ↓              ↓                     ↓                 ↓              ↓           ↓
  .mp4/.webm   Timestamped text      Key frames       Complete SOP   Professional  Auto delete
                                                                          PDF        temp files
```

### Detailed Process

### 1. Audio Transcription (`whisper_transcription.py`)
- Extracts audio from video using FFmpeg
- Transcribes with Whisper Large V3 via Groq
- Generates timestamped segments: `[15.3s - 18.7s]: spoken text`
- Provides context for better frame-to-instruction matching

### 2. Frame Extraction (`video_processor.py`)
- Uses FFmpeg for fast extraction (15x faster than OpenCV!)
- Extracts frames at specified intervals (default: 2 seconds)
- Resizes images for optimal AI processing
- Maintains timestamp information for correlation

### 3. AI Analysis (`sop_analyzer.py`)
- Sends frames and timestamped transcript to Gemini 1.5 Flash
- Uses enhanced prompt for complete procedures
- Cross-references audio timestamps with frame timestamps
- Returns structured JSON with steps, safety notes, and reasoning

### 4. PDF Generation (`pdf_generator.py`)
- Creates professional document layout
- Embeds images at relevant steps
- Includes safety notes and table of contents
- Professional formatting with headers and page numbers

### 5. Automatic Cleanup (`main.py`)
- Deletes temporary extracted frames
- Keeps only the final PDF
- Prevents old/new frame mixing on next run

---

## Example Output (Detailed)

The generated PDF includes:

- **Title Page**: Task name, description, document info
- **Table of Contents**: Quick navigation
- **Safety Section**: Important safety considerations
- **Procedure Steps**: Step-by-step instructions with:
  - Clear numbered steps
  - Action-oriented instructions
  - Screenshot at each step
  - Timestamp reference
  - Additional notes/reasoning

## Configuration

### Frame Extraction Settings

Edit `video_processor.py`:
```python
extractor = VideoFrameExtractor(
    interval_seconds=2,    # Extract 1 frame every 2 seconds
    resize_width=512      # Resize width (maintains aspect ratio)
)
```

### AI Model Settings

Edit `sop_analyzer.py`:
```python
generation_config={
    "temperature": 0.4,        # Lower = more consistent
    "max_output_tokens": 8192  # Maximum response length
}
```

## Troubleshooting

### "GEMINI_API_KEY not found"
- Make sure you created `.env` file (not `.env.example`)
- Verify the API key is valid

### "Import cv2 could not be resolved"
- Install OpenCV: `pip install opencv-python`

### Video processing fails
- Check video format (MP4, MOV supported)
- Ensure video file is not corrupted
- Try with a shorter video first

### PDF generation fails
- Install ReportLab: `pip install reportlab`
- Check disk space for output file

## Business Applications

### Target Customers
- Manufacturing companies
- Industrial training departments
- Safety compliance teams
- Equipment vendors
- Consulting firms

### Pricing Model Ideas
1. **Per-video pricing**: $50-200 per video
2. **SaaS subscription**: $99-499/month
3. **Enterprise license**: Custom pricing
4. **API access**: Pay per API call

### Value Proposition
- Saves 10+ hours per manual
- Ensures consistency
- Easy updates when procedures change
- Reduces training time
- Improves compliance

## Limitations

- Video quality affects AI accuracy
- Works best with clear, well-lit videos
- Requires stable camera angle
- English language optimized (can be adapted)
- Processing time depends on video length

## Future Enhancements

- [ ] Web interface (Flask/Django)
- [ ] Multi-language support
- [ ] Video quality validation
- [ ] Custom branding options
- [ ] Step editing interface
- [ ] Voice narration in video
- [ ] Multiple video formats
- [ ] Batch processing

## Dependencies

- `opencv-python`: Video frame extraction
- `google-generativeai`: Gemini AI API
- `reportlab`: PDF generation
- `Pillow`: Image processing
- `python-dotenv`: Environment configuration

## License

This project is for educational and commercial use.

## Support

For questions or issues, please check:
1. This README
2. Code comments in source files
3. API documentation

## Credits

Built with:
- Google Gemini 2.5 Pro
- OpenCV
- ReportLab

---

**Made for industrial training excellence** 🏭
