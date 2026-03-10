<div align="center">
  <img src="https://raw.githubusercontent.com/moltis-org/moltis/main/website/favicon.svg" width="100" height="100" alt="PocketTTS Coqui Bridge">
  <h1>PocketTTS Coqui Bridge</h1>
  <p><strong>The Sovereign Voice Layer for Moltis</strong></p>
  <p><em>Production-grade TTS. Zero API costs. Total privacy.</em></p>

  <p>
    <a href="#installation">Installation</a> •
    <a href="#comparison">Comparison</a> •
    <a href="#architecture">Architecture</a> •
    <a href="#features">Features</a> •
    <a href="#getting-started">Getting Started</a>
  </p>
</div>

---

> "I’ve spent my career building systems at Google scale and defending digital sovereignty at Darknet.ca. The conclusion is always the same: if you don't own the infrastructure, you don't own the message. We built the PocketTTS Coqui Bridge to kill the 'API Tax' and bring elite-level Text-to-Speech back to your own hardware."
> — *Founder of Darknet.ca & Ex-Googler*

## Why PocketTTS Coqui Bridge?

**PocketTTS Coqui Bridge** is a production-oriented FastAPI service that exposes Coqui-compatible TTS endpoints. Designed primarily for the [Moltis](https://github.com/moltis-org/moltis) ecosystem, it allows you to swap expensive, privacy-invasive paid APIs (like OpenAI or ElevenLabs) for a self-hosted powerhouse.

*   **Secure by Design** — Your voice data never leaves your network. No telemetry, no "AI safety" filters, no surveillance.
*   **Production-Ready** — This isn't a hobby script. It’s a FastAPI-wrapped service with session-based authentication, SQLite persistence, and a protected Admin UI.
*   **Moltis-Native** — Drop-in compatibility for Moltis. Configure it once and your bot has a voice forever, for free.
*   **One-Click Docker** — Deployment so easy it feels like cheating.

## Installation

### The 60-Second Docker Deploy (Recommended)
This is the fastest way to get your sovereign voice layer online.

```bash
docker run -d \
  --name tts-bridge \
  -p 8000:8000 \
  -e APP_USERNAME=admin \
  -e APP_PASSWORD=your_secure_password \
  -e SESSION_SECRET=$(openssl rand -hex 32) \
  -v $(pwd)/data:/app/data \
  --restart always \
  ghcr.io/your-username/pockettts-coqui-bridge:latest
```

*Don't have a pre-built image? Build it locally in seconds:*
```bash
docker build -t pockettts-coqui-bridge .
```

## Comparison: The End of Paid APIs

| Feature | OpenAI TTS | ElevenLabs | **PocketTTS Bridge** |
| :--- | :--- | :--- | :--- |
| **Cost** | Per-character | Tiered / Expensive | **$0.00 (Forever)** |
| **Privacy** | Logged/Analyzed | Data Harvesting | **Zero-Knowledge** |
| **Offline** | No | No | **Yes** |
| **Latency** | Network Dependent | Variable | **Local-speed** |
| **Custom Voices** | Limited | Paid | **Unlimited Cloning** |

## Architecture

```text
┌─────────────────┐      ┌──────────────────────────┐      ┌─────────────────┐
│     Moltis      │      │  PocketTTS Coqui Bridge  │      │   Local Data    │
│  (Or any App)   │      │       (FastAPI)          │      │    (SQLite)     │
└────────┬────────┘      └────────────┬─────────────┘      └────────┬────────┘
         │                            │                             │
         │   POST /api/tts            │      Register Voice         │
         ├───────────────────────────►├────────────────────────────►│
         │                            │      Store Embeddings       │
         │   Receive .wav             │                             │
         │◄───────────────────────────┤                             │
         │                            │      Synthesize             │
         │                            │◄────────────────────────────┘
         │                            │      (Pocket-TTS + Coqui)
```

## Features

*   **Coqui-Compatible API** — Standardized `POST /api/tts` endpoint supporting JSON and Multipart.
*   **Voice Registry** — Managed via SQLite. Built-in voices + your own high-fidelity clones.
*   **Protected Admin UI** — Manage voices, test synthesis, and update settings through a clean, Pico.css-powered dashboard.
*   **Instant Voice Cloning** — Upload a sample, generate an embedding, and use it immediately.
*   **Multi-Format Support** — Returns high-quality `.wav` or compressed `.mp3` on the fly.

## Getting Started

### 1. Configure Moltis
To use this bridge with your Moltis instance, update your `config.toml`:

```toml
[voice.tts]
enabled = true
provider = "coqui"

[voice.tts.coqui]
endpoint = "http://localhost:8000"
```

### 2. Access the Admin UI
Navigate to `http://localhost:8000` to access the management dashboard.
*   **Clone voices** by uploading 10-30 seconds of clear audio.
*   **Preview** voices before deploying them to your bot.
*   **Monitor** the SQLite registry.

## Local Development (Non-Docker)

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install pocket-tts torch --index-url https://download.pytorch.org/whl/cpu
cp .env.example .env
# Edit .env with your credentials
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## License
MIT. Built for the community, by the community. Stop paying for your own voice.
