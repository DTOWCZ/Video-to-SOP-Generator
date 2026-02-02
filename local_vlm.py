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
    Lokální VLM analýza přes Ollama.
    Využívá GPU pro zpracování vision modelů (llama3.2-vision, qwen2.5-vl, atd.)
    """
    
    def __init__(
        self,
        host: str = None,
        model: str = None,
        timeout: float = 300.0  # CZ: 5 minut timeout pro velké modely
    ):
        """
        Inicializace Ollama VLM klienta.
        
        Args:
            host: Ollama server URL (default z .env nebo localhost:11434)
            model: Název modelu (default z .env nebo llama3.2-vision:90b)
            timeout: Timeout pro API volání v sekundách
        """
        from dotenv import load_dotenv
        load_dotenv()
        
        self.host = host or os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.2-vision:90b")
        self.timeout = timeout
        
        # CZ: Odstraníme trailing slash pokud existuje
        self.host = self.host.rstrip("/")
        
        print(f"Ollama VLM configured: {self.model} @ {self.host}")
    
    def check_connection(self) -> bool:
        """Ověří, že Ollama server běží a model je dostupný."""
        try:
            with httpx.Client(timeout=10.0) as client:
                # CZ: Kontrola, zda server odpovídá
                response = client.get(f"{self.host}/api/tags")
                
                if response.status_code != 200:
                    print(f"⚠️ Ollama server not responding properly")
                    return False
                
                # CZ: Kontrola, zda je model stažený
                data = response.json()
                models = [m["name"] for m in data.get("models", [])]
                
                # CZ: Hledáme přesnou shodu nebo prefix
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
        Analyzuje video snímky a generuje SOP strukturu.
        
        Args:
            frames: List slovníků s 'image_data' (base64) a 'timestamp'
            context: Kontext úlohy (např. "Výměna pneumatiky")
            audio_transcript: Časovaný přepis audia
            
        Returns:
            Slovník s SOP strukturou (title, description, safety_notes, steps)
        """
        # CZ: Ověření připojení před analýzou
        if not self.check_connection():
            raise ConnectionError("Ollama server is not available")
        
        print(f"Analyzing {len(frames)} frames with {self.model}...")
        
        # CZ: Vytvoření promptu
        prompt = self._create_prompt(frames, context, audio_transcript)
        
        # CZ: Příprava obrázků pro Ollama API
        images_base64 = [frame["image_data"] for frame in frames]
        
        # CZ: Volání Ollama API
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
                            "num_predict": 8192,  # CZ: Max tokenů ve výstupu
                        }
                    }
                )
                
                if response.status_code != 200:
                    raise RuntimeError(f"Ollama API error: {response.text}")
                
                result = response.json()
                response_text = result.get("response", "")
                
                print("✓ Received response from Ollama")
                
                # CZ: Parsování JSON odpovědi
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
        """Vytvoří systémový prompt pro VLM analýzu."""
        
        # CZ: Informace o časových značkách snímků
        timestamps = [
            f"Frame {i+1} at {frame['timestamp']:.2f}s"
            for i, frame in enumerate(frames)
        ]
        timestamp_info = "\n".join(timestamps)
        
        # CZ: Sekce s audio přepisem pokud je k dispozici
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
        """Parsuje LLM odpověď do strukturovaného JSON."""
        
        # CZ: Odstranění markdown bloků pokud jsou přítomny
        text = response_text.strip()
        if text.startswith("```json"):
            text = text[7:]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("```"):
            text = text[:-3]
        
        text = text.strip()
        
        try:
            data = json.loads(text)
            
            # CZ: Validace struktury
            if "title" not in data or "steps" not in data:
                raise ValueError("Response missing required fields: title or steps")
            
            # CZ: Kontrola požadovaných polí v krocích
            for step in data["steps"]:
                required_fields = ["step_number", "instruction", "timestamp_seconds"]
                for field in required_fields:
                    if field not in step:
                        raise ValueError(f"Step missing required field: {field}")
            
            return data
            
        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON response: {e}")
            print(f"Response text: {text[:500]}...")
            raise ValueError("LLM did not return valid JSON")


def analyze_video_frames_local(
    frames: List[Dict],
    context: str = "",
    audio_transcript: str = ""
) -> Dict:
    """
    Wrapper funkce pro snadné použití lokální VLM analýzy.
    
    Args:
        frames: List snímků s 'image_data' a 'timestamp'
        context: Kontext úlohy
        audio_transcript: Přepis audia
        
    Returns:
        SOP struktura
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
