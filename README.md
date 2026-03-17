<div align="center">
  <img src="https://raw.githubusercontent.com/moltis-org/moltis/main/website/favicon.svg" width="100" height="100" alt="PocketTTS Coqui Bridge">
  <h1>PocketTTS Coqui Bridge</h1>
  <p><strong>The Sovereign Voice Layer for Moltis</strong></p>
  <p><em>Real-time TTS. Zero Latency. 100% Local.</em></p>

  <p>
    <a href="#key-advantages">Advantages</a> •
    <a href="#installation">Installation</a> •
    <a href="#comparison">The Killer Edge</a> •
    <a href="#moltis-integration">Moltis Integration</a> •
    <a href="#features">Features</a>
  </p>
</div>

---

## 🚀 Stop Paying for Your Own Voice

**PocketTTS Coqui Bridge** is a game-changing, production-grade bridge that brings elite-level Text-to-Speech directly to your hardware. No expensive GPUs, no predatory API fees, and absolutely no data harvesting.

We built this because sovereign infrastructure isn't just a luxury—it's a requirement. Whether you're powering a [Moltis](https://github.com/moltis-org/moltis) agent or building a private assistant, this bridge is your ticket to high-performance, cost-free voice synthesis.

### 💎 Key Advantages

*   **⚡ Real-Time CPU Performance** — Optimized to run lightning-fast on standard CPUs. Get instant response times without the need for high-end GPUs.
*   **💰 100% Free & Self-Hosted** — Zero costs. Zero subscriptions. Zero character limits. You own the compute, you own the voice.
*   **👥 Custom Voice Cloning** — Seamlessly clone any voice with just seconds of audio. Your clones stay private, local, and under your control.
*   **🤖 Moltis-Native** — Designed from the ground up to integrate perfectly into the Moltis ecosystem.
*   **🐳 One-Click Deployment** — Fully Dockerized for a "it just works" experience on any server.
*   **🎨 Admin UI** — A professional, dark-themed dashboard to manage, test, and export your custom voices.

## 🏆 The Killer Edge: Why We Win

| Feature | OpenAI / ElevenLabs | Traditional Coqui | **PocketTTS Bridge** |
| :--- | :--- | :--- | :--- |
| **Price** | Per-character tax | Free | **$0.00 (Forever)** |
| **Hardware** | Cloud (Non-Sovereign) | Usually requires GPU | **Standard CPU (Fast)** |
| **Privacy** | They own your data | Local | **Zero-Knowledge** |
| **Speed** | Network Latency | Heavy Load | **Instant / Real-time** |
| **Setup** | API Key | Complex Config | **One-Click Docker** |

## 🛠 Installation

### Deploy in 60 Seconds (Docker)
The fastest path to sovereign voice:

```bash
docker run -d \
  --name tts-bridge \
  -p 8000:8000 \
  -e APP_USERNAME=admin \
  -e APP_PASSWORD=your_secure_password \
  -e SESSION_SECRET=$(openssl rand -hex 32) \
  -v $(pwd)/data:/app/data \
  --restart always \
  ghcr.io/virtuehearts/pockettts-coqui-bridge:latest
```

### Tutorial: Build & Deploy from Source
If you want to build the image yourself from the source code:

1. **Clone the repository:**
   ```bash
   git clone https://github.com/virtuehearts/pockettts-coqui-bridge.git
   cd pockettts-coqui-bridge
   ```

2. **Build the Docker image:**
   ```bash
   docker build -t pockettts-bridge .
   ```

3. **Run the container:**
   ```bash
   docker run -d \
     --name tts-bridge \
     -p 8000:8000 \
     -e APP_USERNAME=admin \
     -e APP_PASSWORD=your_password \
     -e SESSION_SECRET=$(openssl rand -hex 32) \
     -v $(pwd)/data:/app/data \
     --restart always \
     pockettts-bridge
   ```

## 🔑 Authentication

When `ENABLE_AUTH=true` (default), all API requests must be authenticated. You can manage API keys in the **Settings** tab of the Admin UI.

### Supported Authentication Methods

1.  **X-API-Key Header (Recommended):**
    ```bash
    -H "X-API-Key: your_api_key_here"
    ```

2.  **Bearer Token (OpenAI Compatibility):**
    Used primarily for the `/v1/audio/speech` endpoint.
    ```bash
    -H "Authorization: Bearer your_api_key_here"
    ```

3.  **Query Parameter:**
    ```
    ?api_key=your_api_key_here
    ```

## 🔌 Moltis Integration

Integrating with your Moltis bot is effortless. Update your `config.toml` to point to your new bridge:

```toml
[voice.tts]
enabled = true
provider = "coqui"

[voice.tts.coqui]
endpoint = "http://your-server-ip:8000"
```

### Using Custom Voices with Moltis

To use a specific cloned voice (e.g., `Mya-01`) with Moltis, you have two primary options:

1.  **Environment Variable (Global Default):**
    Set the `DEFAULT_VOICE` environment variable on the bridge container to the ID of your cloned voice.
    ```bash
    -e DEFAULT_VOICE=mya-01
    ```
    *Note: Voice IDs are typically the lowercase, slugified version of the name.*

2.  **Moltis Configuration:**
    Ensure your Moltis setup is configured to request the specific voice ID. If Moltis supports passing a speaker ID to the Coqui provider, use the ID found in the Bridge Admin UI.

3.  **Default Output Format:**
    If your client requires MP3 by default, you can set:
    ```bash
    -e DEFAULT_OUTPUT_FORMAT=mp3
    ```

## 👥 Voice Management

### Cloning via Admin UI
1.  Log in to the Admin UI (`http://your-server-ip:8000`).
2.  Navigate to the **Voices** tab.
3.  Click **Clone New Voice**.
4.  Upload a clean 5-10 second audio sample (WAV, MP3, OGG, OPUS, etc.).
5.  Give it a name (e.g., `Mya-01`) and click **Clone**.
6.  The voice is now ready for use via the API.

### Cloning via API
You can programmatically clone voices by sending a `multipart/form-data` request:

```bash
curl -X POST http://localhost:8000/api/voices/clone \
  -H "Authorization: Basic $(echo -n 'admin:your_password' | base64)" \
  -F "name=Mya-01" \
  -F "audio_file=@path/to/sample.wav"
```

## 🛠 API Reference

PocketTTS Coqui Bridge provides two primary interfaces: a Coqui-compatible API and an OpenAI-compatible Speech API.

### 1. Coqui-Compatible TTS (`/api/tts`)

The primary endpoint for generating high-quality speech. Supports JSON or multipart/form-data.

**Endpoint:** `POST /api/tts`

**JSON Parameters:**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | string | Yes | The text to be synthesized into speech. |
| `speaker_id` | string | No | The ID of the voice to use (e.g., `alba`, `mya-01`). |
| `format` | string | No | Output format: `wav` (default) or `mp3`. |
| `voice` | string | No | Alias for `speaker_id`. |
| `speaker` | string | No | Alias for `speaker_id`. |

**Multipart Parameters (for On-the-Fly Cloning):**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `text` | string | Yes | The text to be synthesized. |
| `speaker_wav` | file | No | A reference audio file (WAV/MP3/etc.) for instant cloning. |
| `save_voice` | boolean | No | If `true`, the cloned voice is permanently saved. |
| `clone_name` | string | No | The name to assign if `save_voice` is `true`. |

### 2. OpenAI-Compatible Speech (`/v1/audio/speech`)

A drop-in replacement for OpenAI's `v1/audio/speech` endpoint, making it compatible with any tool that supports OpenAI's TTS.

**Endpoint:** `POST /v1/audio/speech`

**JSON Parameters:**
| Parameter | Type | Required | Description |
| :--- | :--- | :--- | :--- |
| `input` | string | Yes | The text to synthesize (alias for `text`). |
| `voice` | string | Yes | The voice ID to use. |
| `response_format`| string | No | Output format: `mp3` (default) or `wav`. |
| `model` | string | No | Ignored (provided for compatibility). |

### 3. Voice Management API

Manage your voice library programmatically.

*   **List Voices:** `GET /api/voices` — Returns a list of all available built-in and cloned voices.
*   **Get Voice Details:** `GET /api/voices/{voice_id}` — Returns metadata for a specific voice.
*   **Clone Voice:** `POST /api/voices/clone` — Permanently clone a voice via `multipart/form-data`.
*   **Export Voice:** `GET /api/voices/{voice_id}/export` — Download a ZIP archive containing the voice model and sample.
*   **Delete Voice:** `DELETE /api/voices/{voice_id}` — Remove a cloned voice from the registry.

## 🚀 Examples for OpenClaw and Other Apps

Use these practical `curl` examples to integrate PocketTTS Bridge into any bot or application. Replace `your_api_key_here` with a key from the Bridge Settings.

### 1. Simple MP3 Generation (via `X-API-Key`)
Generate an MP3 using a specific voice:

```bash
curl -X POST http://localhost:8000/api/tts \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "The sovereign voice layer is ready for deployment.",
    "voice": "alba",
    "format": "mp3"
  }' \
  --output output.mp3
```

### 2. Using Custom Cloned Voices
If you've cloned a voice via the UI or API and its ID is `mya-01`:

```bash
curl -X POST http://localhost:8000/api/tts \
  -H "X-API-Key: your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Hello! I am your custom voice assistant.",
    "voice": "mya-01",
    "format": "mp3"
  }' \
  --output voice.mp3
```

### 3. OpenAI-Compatible Request (OpenClaw / ChatGPT)
Many bots (like OpenClaw) use OpenAI's TTS schema. Point them to `http://your-server-ip:8000/v1` and use your API key:

```bash
curl -X POST http://localhost:8000/v1/audio/speech \
  -H "Authorization: Bearer your_api_key_here" \
  -H "Content-Type: application/json" \
  -d '{
    "input": "This is synthesized via the OpenAI-compatible endpoint.",
    "voice": "mya-01",
    "model": "tts-1",
    "response_format": "mp3"
  }' \
  --output openai_speech.mp3
```

### 4. Instant On-the-Fly Cloning
Synthesize speech with a voice from a local file without saving it to the registry:

```bash
curl -X POST http://localhost:8000/api/tts \
  -H "X-API-Key: your_api_key_here" \
  -F "text=I will speak using the provided reference file." \
  -F "speaker_wav=@path/to/my_voice_sample.wav" \
  -F "format=mp3" \
  --output cloned_output.mp3
```

## ✨ Features

*   **Coqui-Compatible API** — Standardized `POST /api/tts` endpoint. Drop-in replacement for existing Coqui setups.
*   **Advanced Voice Registry** — Managed via SQLite with built-in voices and instant cloning.
*   **Professional Admin UI** — A polished, dark-themed interface for managing your voice library.
*   **Real-time Testing** — Test any voice with custom text input and get immediate playback/download.
*   **Multi-Format Support** — High-quality `.wav` and compressed `.mp3` output.
*   **Voice Export** — Bundle and export your cloned voices as ZIP archives for easy migration.

---

## 🛡 License
MIT. Built for the community that values sovereignty. Stop the API tax today.
