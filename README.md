# pockettts-coqui-bridge

Production-oriented local FastAPI service that exposes **Coqui-compatible TTS endpoints** for Moltis while offering a protected admin UI for voice management and cloning.

## Features
- Coqui-style API endpoint: `POST /api/tts` (JSON + multipart, alias support).
- Built-in + cloned voice registry with SQLite metadata.
- Protected admin UI (`/`, `/voices`, `/voices/new`, `/settings`) with session login.
- Changeable admin password from the Settings page (persisted in SQLite).
- Public synth endpoints by default for Moltis compatibility.
- Docker support with persistent data volume.

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
# real Pocket-TTS backend
pip install pocket-tts torch
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Docker

```bash
docker build -t pockettts-coqui-bridge .
docker run --rm -p 8000:8000 \
  -e APP_USERNAME=admin \
  -e APP_PASSWORD=change_me \
  -e SESSION_SECRET=replace_me \
  -v $(pwd)/data:/app/data \
  pockettts-coqui-bridge
```

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
