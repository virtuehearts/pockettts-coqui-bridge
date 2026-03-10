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
  ghcr.io/moltis-org/pockettts-coqui-bridge:latest
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
