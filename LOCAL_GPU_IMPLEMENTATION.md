# 🚀 Implementace Lokálního GPU Módu (Ollama + faster-whisper)

**Datum zahájení:** 2026-02-02  
**Hardware:** RTX 6000 Blackwell PRO (96GB VRAM)  
**Status:** ✅ Kompletní - Připraveno k testování

---

## 📋 Checklist Implementace

### Fáze 1: Konfigurace
- [x] 1.1 Aktualizovat `.env.example` s novými proměnnými ✅
- [x] 1.2 Aktualizovat `requirements.txt` s novými závislostmi ✅

### Fáze 2: Implementace Whisper (Lokální transkripce)
- [x] 2.1 Vytvořit `local_whisper.py` pro faster-whisper ✅
- [x] 2.2 Upravit `whisper_transcription.py` pro hybridní režim ✅

### Fáze 3: Implementace VLM (Ollama Vision)
- [x] 3.1 Vytvořit `local_vlm.py` pro Ollama komunikaci ✅
- [x] 3.2 Upravit `sop_analyzer.py` pro hybridní režim ✅

### Fáze 4: Integrace
- [x] 4.1 Upravit `main.py` pro automatickou detekci režimu ✅
- [x] 4.2 Upravit `webapp/app.py` pro webové rozhraní ✅

### Fáze 5: Testování (ČEKÁ NA UŽIVATELE)
- [ ] 5.1 Nainstalovat Ollama a stáhnout model
- [ ] 5.2 Nainstalovat Python závislosti
- [ ] 5.3 Test lokálního Whisper
- [ ] 5.4 Test Ollama VLM
- [ ] 5.5 End-to-end test celého pipeline

### Fáze 6: Dokumentace
- [x] 6.1 Tento dokument - LOCAL_GPU_IMPLEMENTATION.md ✅
- [ ] 6.2 Aktualizovat hlavní README.md (po testování)

---

## 🔧 CO MUSÍŠ UDĚLAT TY (prerekvizity)

### Krok 1: Nainstalovat Ollama
```powershell
# Stáhni instalátor z:
# https://ollama.com/download/windows

# Po instalaci ověř:
ollama --version
```

### Krok 2: Stáhnout Vision model
```powershell
# Pro tvých 96GB VRAM - nejlepší kvalita (90B parametrů):
ollama pull llama3.2-vision:90b

# Alternativy (menší, rychlejší):
# ollama pull qwen2.5-vl:72b
# ollama pull llava:34b

# Ověření, že model je stažený:
ollama list
```

### Krok 3: Spustit Ollama server
```powershell
# Ollama musí běžet na pozadí:
ollama serve

# Nebo spusť Ollama přes GUI (po instalaci běží automaticky)
```

### Krok 4: Nainstalovat Python závislosti
```powershell
# Aktivuj venv:
.\venv\Scripts\activate

# Nainstaluj nové závislosti:
pip install -r requirements.txt
```

### Krok 5: Vytvořit .env soubor
```powershell
# Zkopíruj šablonu:
copy .env.example .env

# Uprav .env soubor - nastav tyto hodnoty:
```

```ini
# Hlavní přepínač - LOCAL = GPU, API = Cloud
AI_MODE=LOCAL

# Ollama konfigurace
OLLAMA_HOST=http://localhost:11434
OLLAMA_MODEL=llama3.2-vision:90b

# Whisper konfigurace
WHISPER_MODEL=large-v3
WHISPER_COMPUTE_TYPE=float16
```

### Krok 6: Otestovat
```powershell
# Test Ollama připojení:
python local_vlm.py

# Test celého pipeline:
python main.py "cesta/k/testovaci.mp4" -o test_output.pdf
```

---

## 📊 Progress Log

| Čas | Akce | Status |
|-----|------|--------|
| 12:49 | Vytvořen tracking dokument | ✅ |
| 12:50 | Aktualizován .env.example | ✅ |
| 12:50 | Aktualizován requirements.txt | ✅ |
| 12:51 | Vytvořen local_whisper.py | ✅ |
| 12:52 | Vytvořen local_vlm.py | ✅ |
| 12:53 | Upraven whisper_transcription.py | ✅ |
| 12:54 | Upraven sop_analyzer.py | ✅ |
| 12:55 | Upraven main.py | ✅ |
| 12:56 | Upraven webapp/app.py | ✅ |
| **---** | **IMPLEMENTACE KOMPLETNÍ** | **✅** |

---

## 📁 Nové/Upravené soubory

| Soubor | Typ | Popis | Status |
|--------|-----|-------|--------|
| `local_whisper.py` | **NEW** | Lokální Whisper přes faster-whisper | ✅ |
| `local_vlm.py` | **NEW** | Ollama VLM klient | ✅ |
| `sop_analyzer.py` | MODIFIED | Hybridní režim (API/Local) | ✅ |
| `whisper_transcription.py` | MODIFIED | Hybridní režim (API/Local) | ✅ |
| `main.py` | MODIFIED | Detekce režimu + prerekvizity | ✅ |
| `.env.example` | MODIFIED | Nové proměnné pro LOCAL mód | ✅ |
| `requirements.txt` | MODIFIED | faster-whisper, httpx | ✅ |
| `webapp/app.py` | MODIFIED | Webové rozhraní s hybridním módem | ✅ |

---

## 🎯 Cílová architektura

```
┌─────────────────────────────────────────────────────────────┐
│                        main.py                               │
│              (automatická detekce AI_MODE)                   │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              AI_MODE = ? (z .env)                            │
└──────────┬──────────────────────────────┬───────────────────┘
           │                              │
           ▼                              ▼
┌──────────────────────┐      ┌──────────────────────┐
│   AI_MODE = "API"    │      │  AI_MODE = "LOCAL"   │
├──────────────────────┤      ├──────────────────────┤
│ • Gemini API         │      │ • Ollama VLM         │
│ • Groq Whisper       │      │ • faster-whisper     │
│ • Cloud processing   │      │ • RTX 6000 GPU       │
│ • Pay per use        │      │ • Zero cost          │
│ • Vyžaduje API klíče │      │ • Vyžaduje Ollama    │
└──────────────────────┘      └──────────────────────┘
```

---

## 🚀 Jak spustit

### Lokální mód (GPU) - DOPORUČENO PRO TEBE:
```powershell
# 1. Ujisti se, že Ollama běží:
ollama serve

# 2. Měj v .env nastaveno AI_MODE=LOCAL

# 3. CLI verze:
python main.py "cesta/k/videu.mp4" -o vystup.pdf

# 4. Nebo web verze:
cd webapp
python app.py
# Otevři http://localhost:5000
```

### API mód (Cloud):
```powershell
# 1. Nastav v .env:
#    AI_MODE=API
#    GOOGLE_API_KEY=tvuj_klic
#    GROQ_API_KEY=tvuj_klic

# 2. Spusť:
python main.py "cesta/k/videu.mp4" -o vystup.pdf
```

---

## ⚙️ Kompletní .env konfigurace

```ini
# ============================================================
# AI MODE SELECTION
# ============================================================
# Options: "API" (cloud) or "LOCAL" (GPU)
AI_MODE=LOCAL

# ============================================================
# LOCAL MODE SETTINGS (used when AI_MODE=LOCAL)
# ============================================================

# Ollama server address
OLLAMA_HOST=http://localhost:11434

# Ollama Vision model
# Pro 96GB VRAM: llama3.2-vision:90b (nejlepší)
# Alternativy: qwen2.5-vl:72b, llava:34b
OLLAMA_MODEL=llama3.2-vision:90b

# Local Whisper model size
# Options: tiny, base, small, medium, large-v3
WHISPER_MODEL=large-v3

# Whisper compute type
# float16 = best quality, int8 = faster
WHISPER_COMPUTE_TYPE=float16

# ============================================================
# API MODE SETTINGS (used when AI_MODE=API)
# ============================================================

# Google Gemini API Key
GOOGLE_API_KEY=your_key_here

# Groq API Key (for Whisper)
GROQ_API_KEY=your_key_here

# ============================================================
# FLASK WEB APP
# ============================================================
SECRET_KEY=your_secret_key_here
```

---

## 🔍 Troubleshooting

### "Ollama not responding"
```powershell
# Spusť Ollama server:
ollama serve

# Nebo zkontroluj, zda běží:
curl http://localhost:11434/api/tags
```

### "Model not found"
```powershell
# Stáhni model:
ollama pull llama3.2-vision:90b

# Ověř dostupné modely:
ollama list
```

### "CUDA not available"
```powershell
# Ověř CUDA instalaci:
python -c "import torch; print(torch.cuda.is_available(), torch.cuda.get_device_name(0))"

# Pokud vrátí False, nainstaluj PyTorch s CUDA:
pip install torch --index-url https://download.pytorch.org/whl/cu121
```

### "faster-whisper import error"
```powershell
pip install faster-whisper
```

### "httpx import error"
```powershell
pip install httpx
```

---

## 📈 Očekávaný výkon

| Operace | API Mode | LOCAL Mode (96GB VRAM) |
|---------|----------|------------------------|
| Whisper transkripce (4min video) | ~30s | **~5-8s** |
| VLM analýza (20 snímků) | ~75s | **~20-40s** |
| PDF generace | ~5s | ~5s |
| **Celkem** | ~2 min | **~30-60s** |
| **Náklady** | $0.01-0.05/video | **$0** |

---

## ✅ HOTOVO!

Implementace je kompletní. Nyní proveď kroky v sekci **"CO MUSÍŠ UDĚLAT TY"** výše.

Po instalaci Ollama a stažení modelu můžeš otestovat příkazem:
```powershell
python main.py "tvoje_video.mp4" -o test.pdf
```

Pokud narazíš na problémy, podívej se do sekce Troubleshooting nebo se zeptej.
