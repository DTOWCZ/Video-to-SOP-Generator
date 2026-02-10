"""
Local Vision Language Model (VLM) Analyzer using Ollama
GPU-accelerated image analysis for SOP generation
Runs entirely on local RTX 6000 Blackwell GPU
"""

import os
import json
import base64
import httpx
from typing import List, Dict, Optional
from pathlib import Path


class OllamaVLMAnalyzer:
    """
    Local VLM analysis via Ollama.
    Uses GPU for processing vision models (llama3.2-vision, qwen2.5-vl, etc.)
    """
    
    def __init__(
        self,
        host: str = None,
        model: str = None,
        timeout: float = 300.0  # 5 minutes timeout for large models
    ):
        """
        Initialization of Ollama VLM client.
        
        Args:
            host: Ollama server URL (default from .env or localhost:11434)
            model: Model name (default from .env or auto-detected based on GPU)
            timeout: Timeout for API calls in seconds
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        
        # Auto-recommend model based on GPU if not explicitly specified
        if model is None and not os.getenv("OLLAMA_MODEL"):
            try:
                from gpu_detector import GPUDetector
                detector = GPUDetector()
                recommended = detector.recommend_model()
                
                if recommended != "API_MODE_RECOMMENDED":
                    self.model = recommended
                    print(f"ℹ️  Auto-detected GPU: {detector.gpu_info['name']} ({detector.gpu_info['vram_gb']:.1f}GB)")
                    print(f"ℹ️  Auto-selected model: {self.model}")
                else:
                    # Fallback to smaller model
                    self.model = "llama3.2-vision:11b"
            except Exception as e:
                # If detection fails, use default model
                self.model = "llama3.2-vision:11b"
        else:
            self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2-vision:90b")
        
        self.timeout = timeout
        
        # Remove trailing slash if it exists
        self.host = self.host.rstrip("/")
        
        print(f"Ollama VLM configured: {self.model} @ {self.host}")
    
    def check_connection(self) -> bool:
        """Verify that the Ollama server is running and the model is available."""
        try:
            with httpx.Client(timeout=10.0) as client:
                # Check if the server responds
                response = client.get(f"{self.host}/api/tags")
                
                if response.status_code != 200:
                    print(f"⚠️ Ollama server not responding properly")
                    return False
                
                # Check if the model is downloaded
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                
                # Search for exact match or prefix
                model_found = any(
                    self.model == m or self.model.split(":")[0] in m
                    for m in models
                )
                
                if not model_found:
                    print(f"⚠️ Model '{self.model}' not found. Available: {models}")
                    print(f"   Run: ollama pull {self.model}")
                    return False
                
                print(f"✓ Ollama ready with model: {self.model}")
                return True
                
        except httpx.ConnectError:
            print(f"❌ Cannot connect to Ollama at {self.host}")
            print("   Make sure Ollama is running: ollama serve")
            return False
        except Exception as e:
            print(f"❌ Error checking Ollama: {e}")
            return False
    
    def analyze_frames(
        self,
        frames: List[Dict],
        context: str = "",
        audio_transcript: str = ""
    ) -> Dict:
        """
        Analyzes video frames and generates SOP structure.
        
        Args:
            frames: List of dictionaries with 'image_data' (base64) and 'timestamp'
            context: Task context (e.g., "Tire replacement")
            audio_transcript: Timestamped audio transcript
            
        Returns:
            Dictionary with SOP structure (title, description, safety_notes, steps)
        """
        # Verify connection before analysis
        if not self.check_connection():
            raise ConnectionError("Ollama server is not available")
        
        print(f"Analyzing {len(frames)} frames with {self.model}...")
        
        # Ollama VLM models can typically handle max 10-20 images at once.
        # For longer videos, subsample evenly across the entire video.
        MAX_FRAMES = 20
        if len(frames) > MAX_FRAMES:
            # Evenly distribute frame selection across the video
            step = len(frames) / MAX_FRAMES
            sampled_frames = [frames[int(i * step)] for i in range(MAX_FRAMES)]
            print(f"ℹ️  Subsampled {len(frames)} frames → {len(sampled_frames)} frames (max {MAX_FRAMES} for VLM)")
            analysis_frames = sampled_frames
        else:
            analysis_frames = frames
        
        # Create prompt (using sampled frames for correct timestamp info)
        prompt = self._create_prompt(analysis_frames, context, audio_transcript)
        
        # Prepare images for Ollama API
        images_base64 = [frame["image_data"] for frame in analysis_frames]
        
        # Call Ollama API
        try:
            with httpx.Client(timeout=self.timeout) as client:
                response = client.post(
                    f"{self.host}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "images": images_base64,
                        "stream": False,
                        "options": {
                            "temperature": 0.4,
                            "top_p": 0.95,
                            "num_predict": 8192,  # Max tokens in output
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama API error: {response.text}")
                
                result = response.json()
                response_text = result.get("response", "")
                
                print("✓ Received response from Ollama")
                
                # Parse JSON response
                sop_data = self._parse_response(response_text)
                
                return sop_data
                
        except httpx.TimeoutException:
            raise TimeoutError(
                f"Ollama request timed out after {self.timeout}s. "
                "Try reducing the number of frames or using a smaller model."
            )
        except Exception as e:
            print(f"❌ Error during Ollama analysis: {e}")
            raise
    
    def _create_prompt(
        self,
        frames: List[Dict],
        context: str,
        audio_transcript: str = ""
    ) -> str:
        """Creates a system prompt for VLM analysis."""
        
        # Frame timestamp information
        timestamps = [
            f"Frame {i+1} at {frame['timestamp']:.2f}s"
            for i, frame in enumerate(frames)
        ]
        timestamp_info = "\n".join(timestamps)
        
        # Audio transcript section if available
        audio_section = ""
        if audio_transcript:
            audio_section = f"""

Audio Transcript (with timestamps):
{audio_transcript}

IMPORTANT: Use the audio transcript timestamps to match spoken words with the correct video frames. When someone explains an action at a specific time, that helps you identify which frame shows that action.
"""
        
        prompt = f"""You are an expert Technical Writer specializing in Standard Operating Procedures (SOPs) for industrial and manufacturing processes.

Task Context: {context if context else "Manufacturing/assembly process"}

You will receive a sequence of {len(frames)} frames from a video showing a worker performing a task.

Frame Timestamps:
{timestamp_info}
{audio_section}

Your job is to:
1. Watch the sequence carefully
2. Listen to the audio transcript (if provided) for additional context
3. Identify distinct actions/steps being performed (including disassembly AND reassembly)
4. Write clear, actionable instructions for each step
5. Select the best timestamp where each action is most clearly visible
6. Provide reasoning for why that step matters

CRITICAL INSTRUCTIONS FOR REPAIR/MAINTENANCE PROCEDURES:
- If the procedure involves disassembly (removing parts), YOU MUST include the reassembly steps
- After repair/replacement, include all steps to put components back together in REVERSE order
- Reference the disassembly steps when writing reassembly
- Include torque specifications, alignment checks, and final verification steps

Output Format (STRICT JSON):
{{
  "title": "Descriptive Task Name",
  "description": "Brief overview of the entire process",
  "safety_notes": ["Safety consideration 1", "Safety consideration 2"],
  "steps": [
    {{
      "step_number": 1,
      "instruction": "Clear, imperative instruction (e.g., 'Pick up the 5mm Allen wrench')",
      "timestamp_seconds": 12.5,
      "reasoning": "Why this step is important or what to watch for"
    }}
  ]
}}

Important Guidelines:
- Each step must be atomic (one clear action)
- Use imperative voice ("Pick up", "Turn", "Connect")
- Be specific about tools, parts, and measurements
- Include safety warnings if relevant
- Choose the timestamp where the action is MOST VISIBLE
- Include BOTH disassembly steps AND reassembly steps
- Include final verification steps
- Aim for 5-20 steps depending on complexity

Output ONLY valid JSON. Do not include any markdown formatting or code blocks."""
        
        return prompt
    
    def _parse_response(self, response_text: str) -> Dict:
        """Parses LLM response into structured JSON.
        
        Robust parsing – local models sometimes wrap JSON in surrounding text.
        """
        
        # Remove markdown blocks if present
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        # Try direct parsing first
        try:
            data = json.loads(text)
        except json.JSONDecodeError:
            # Fallback – find JSON object inside surrounding text
            start_idx = text.find('{')
            end_idx = text.rfind('}')
            
            if start_idx == -1 or end_idx == -1 or end_idx <= start_idx:
                print(f"Failed to find JSON in response")
                print(f"Response text: {text[:500]}...")
                raise ValueError("LLM did not return valid JSON")
            
            json_str = text[start_idx:end_idx + 1]
            
            try:
                data = json.loads(json_str)
            except json.JSONDecodeError as e:
                print(f"Failed to parse extracted JSON: {e}")
                print(f"Extracted JSON: {json_str[:500]}...")
                raise ValueError("LLM did not return valid JSON")
        
        # Validate structure
        if "title" not in data or "steps" not in data:
            raise ValueError("Response missing required fields: title or steps")
        
        # Ensure steps have all required fields
        for i, step in enumerate(data["steps"]):
            step.setdefault("step_number", i + 1)
            step.setdefault("reasoning", "")
            
            required_fields = ["instruction", "timestamp_seconds"]
            for field in required_fields:
                if field not in step:
                    raise ValueError(f"Step {i+1} missing required field: {field}")
        
        data.setdefault("description", "")
        data.setdefault("safety_notes", [])
        
        return data


def analyze_video_frames_local(
    frames: List[Dict],
    context: str = "",
    audio_transcript: str = ""
) -> Dict:
    """
    Wrapper function for easy local VLM analysis.
    
    Args:
        frames: List of frames with 'image_data' and 'timestamp'
        context: Task context
        audio_transcript: Audio transcript
        
    Returns:
        SOP structure
    """
    analyzer = OllamaVLMAnalyzer()
    return analyzer.analyze_frames(frames, context, audio_transcript)


# ============================================================
# Test / CLI
# ============================================================
if __name__ == "__main__":
    import sys
    
    print("=" * 60)
    print("Ollama VLM Analyzer - Connection Test")
    print("=" * 60)
    
    analyzer = OllamaVLMAnalyzer()
    
    if analyzer.check_connection():
        print("\n✅ Ollama is ready for SOP generation!")
        print(f"   Model: {analyzer.model}")
        print(f"   Host: {analyzer.host}")
    else:
        print("\n❌ Ollama is not ready. Please check:")
        print("   1. Is Ollama installed? (https://ollama.com/download)")
        print("   2. Is Ollama running? (ollama serve)")
        print(f"   3. Is the model downloaded? (ollama pull {analyzer.model})")
        sys.exit(1)
