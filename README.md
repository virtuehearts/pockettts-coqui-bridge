# pockettts-coqui-bridge

Production-oriented local FastAPI service that exposes **Coqui-compatible TTS endpoints** for Moltis while offering a protected admin UI for voice management and cloning.

## Features
- Coqui-style API endpoint: `POST /api/tts` (JSON + multipart, alias support).
- OpenAI-style endpoint: `POST /v1/audio/speech`.
- Built-in + cloned voice registry with SQLite metadata.
- Protected admin UI (`/`, `/voices`, `/voices/new`, `/settings`) with session login.
- Public synth endpoints by default for Moltis compatibility.
- Minimal environment config.

## Project tree

```text
app/
  main.py
  config.py
  db.py
  models.py
  api/
    auth.py
    health.py
    tts.py
    ui.py
    voices.py
  services/
    auth.py
    audio.py
    pockettts.py
    voice_registry.py
  templates/
  static/
data/
  voices/
  embeddings/
  output/
  hf-cache/
requirements.txt
.env.example
```

## Minimal setup
1. Copy `.env.example` to `.env`
2. Set:
   - `APP_USERNAME`
   - `APP_PASSWORD`
   - `SESSION_SECRET`
3. Optionally set `HF_TOKEN` if you want cloning
4. Run the app

If `HF_TOKEN` is blank, the app still works with built-in voices.

## Local setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Cloning behavior
- Cloning endpoints require auth (unless `ENABLE_AUTH=false`).
- Cloning requires `HF_TOKEN`; if missing, cloning returns a clear actionable error.
- Built-in synthesis remains available without `HF_TOKEN`.

## API examples

### Health
```bash
curl http://localhost:8000/health
```

### Voices
```bash
curl http://localhost:8000/api/voices
```

### Coqui-compatible TTS
```bash
curl -X POST http://localhost:8000/api/tts \
  -F 'text=Hello from Moltis' \
  -F 'speaker-id=alba' \
  -o response.wav
```

### OpenAI-style speech
```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H 'Content-Type: application/json' \
  -d '{"model":"pocket-tts","input":"Hello world","voice":"alba","response_format":"wav"}' \
  -o speech.wav
```

### Clone voice (protected)
```bash
curl -X POST http://localhost:8000/api/voices/clone \
  -F 'name=My Voice' \
  -F 'audio_file=@sample.wav'
```

## Moltis configuration example

```toml
[voice.tts]
enabled = true
provider = "coqui"

[voice.tts.coqui]
endpoint = "http://localhost:8000"
```

## Future Dockerization notes
- Add `Dockerfile` with Python 3.11 slim + ffmpeg.
- Mount `./data` as persistent volume.
- Expose `8000` and pass `.env` values.
