# 🔧 FIX CHECKLIST - Video-to-SOP Generator

> Datum analýzy: 2026-02-10
> Cíl: Opravit projekt tak, aby spolehlivě vytvořil PDF SOP z jednoho videa

---

## 🔴 KRITICKÉ (musí se opravit, jinak nefunguje)

- [x] **FIX-01**: `sop_analyzer.py` – top-level import `google.generativeai` crashne LOCAL mód ✅
  - Soubor: `sop_analyzer.py`, řádek 13
  - Problém: Import se provede vždy, i v LOCAL módu → ImportError pokud není pip balíček
  - Řešení: Přesunuto do `SOPAnalyzer.__init__()` (lazy import)

- [x] **FIX-02**: `video_processor.py` – hardcoded `'ffmpeg'` bez fallbacku ✅
  - Soubor: `video_processor.py`, řádek 72
  - Problém: Na Windows FFmpeg často není v PATH → FileNotFoundError
  - Řešení: Přidána metoda `_get_ffmpeg_path()` s fallbackem na `imageio_ffmpeg`

- [x] **FIX-03**: `requirements.txt` – chybí `imageio_ffmpeg`, duplicity, nepoužité balíčky ✅
  - Soubor: `requirements.txt`
  - Problém: `imageio_ffmpeg` chybí, `python-dotenv` duplicitní, `moviepy` nepoužitý
  - Řešení: Vyčištěno a doplněny chybějící závislosti

- [x] **FIX-04**: `video_processor.py` – chybí `creationflags` pro Windows subprocess ✅
  - Soubor: `video_processor.py`, řádek 77
  - Problém: Na Windows se otevře console okno při FFmpeg
  - Řešení: Přidán `creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0`

---

## 🟡 STŘEDNÍ (ovlivňuje spolehlivost)

- [x] **FIX-05**: `local_vlm.py` – posílá VŠECHNY framy do Ollama najednou ✅
  - Soubor: `local_vlm.py`, řádek 131
  - Problém: Pro 4min video = ~120 obrázků → timeout/OOM na GPU
  - Řešení: Subsample na max 20 frameů rovnoměrně přes video

- [x] **FIX-06**: `test_pdf_generation.py` – hardcoded cesta původního autora ✅
  - Soubor: `test_pdf_generation.py`, řádek 23
  - Problém: Cesta `D:\SHEZAN\AI\...` neexistuje na tvém stroji
  - Řešení: Přepsáno na dynamické hledání + CLI argument

- [x] **FIX-07**: `sop_analyzer.py` + `local_vlm.py` – `_parse_response` nezvládá JSON uvnitř textu ✅
  - Soubory: `sop_analyzer.py`, `local_vlm.py`
  - Problém: Pokud LLM vrátí text PŘED JSON blokem, parsing selže
  - Řešení: Přidán fallback hledání `{...}` uvnitř textu + defaulty pro chybějící pole

---

## 🟢 NICE-TO-HAVE (zlepšení kvality)

- [ ] **FIX-08**: Přidat retry logiku pro API volání (Gemini/Groq/Ollama)
- [ ] **FIX-09**: Přidat validaci video formátu před zpracováním
- [ ] **FIX-10**: Webapp `/webapp/app.py` neintegruje hybrid LOCAL/API mód

---

## ✅ CO UŽ FUNGUJE SPRÁVNĚ

- [x] Pipeline orchestrace (`main.py`) – kroky navázané správně
- [x] Hybrid mode routing (`get_transcript()`, `analyze_frames()`)
- [x] PDF generátor – profesionální PDF s obrázky, TOC, safety notes
- [x] Timestamp matching (frame ↔ step) – `min()` najde nejbližší frame
- [x] Cleanup – automatické smazání temp souborů
- [x] GPU detekce (`gpu_detector.py`)
- [x] JSON parsing – robustní s fallback hledáním
- [x] Error handling – try/catch + traceback

---

## 🔍 SYNTAX VERIFICATION

```
py_compile: main.py ✅
py_compile: sop_analyzer.py ✅
py_compile: video_processor.py ✅
py_compile: local_vlm.py ✅
py_compile: local_whisper.py ✅
py_compile: pdf_generator.py ✅
py_compile: whisper_transcription.py ✅
py_compile: gpu_detector.py ✅
py_compile: test_pdf_generation.py ✅
```

---

## 📋 Jak spustit

### LOCAL mód (GPU):
```powershell
# 1. Nakopíruj .env
cp .env.example .env
# 2. Nastav AI_MODE=LOCAL v .env
# 3. Spusť Ollama: ollama serve
# 4. Stáhni model: ollama pull llama3.2-vision:11b
# 5. Spusť:
py main.py cesta/k/videu.mp4 -o muj_sop.pdf --company "Moje Firma"
```

### API mód (Cloud):
```powershell
# 1. Nakopíruj .env a vyplň API klíče (GOOGLE_API_KEY, GROQ_API_KEY)
cp .env.example .env
# 2. Nastav AI_MODE=API v .env
# 3. Spusť:
py main.py cesta/k/videu.mp4 -o muj_sop.pdf --company "Moje Firma"
```
