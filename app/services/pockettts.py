from __future__ import annotations

import math
import struct
import wave
from pathlib import Path

from app.config import Settings


class PocketTTSService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.backend_name = "pocket-tts"

    def availability(self) -> dict:
        # In local/dev environments this stub remains available for built-in voices.
        return {
            "engine": self.backend_name,
            "available": True,
            "model_ready": True,
            "cloning_available": bool(self.settings.hf_token),
        }

    def ensure_cloning_available(self) -> None:
        if not self.settings.hf_token:
            raise RuntimeError("Cloning requires HF_TOKEN with model access. Set HF_TOKEN in .env")

    def synthesize_to_wav(self, text: str, voice: str, output_path: Path) -> Path:
        # Placeholder local synthesis to keep endpoint behavior stable offline.
        # Frequency shifts by voice for easy differentiation.
        freq = 220 if voice == "alba" else 280 if voice == "sol" else 330
        duration = max(0.35, min(4.0, len(text) * 0.03))
        self._write_tone(output_path, freq=freq, duration_s=duration)
        return output_path

    def clone_and_register_assets(self, sample_wav_path: Path, embedding_path: Path) -> None:
        self.ensure_cloning_available()
        embedding_path.write_text(f"embedding-generated-from:{sample_wav_path.name}\n", encoding="utf-8")

    @staticmethod
    def _write_tone(path: Path, *, freq: float, duration_s: float, sample_rate: int = 22050) -> None:
        n_samples = int(sample_rate * duration_s)
        amplitude = 8000
        path.parent.mkdir(parents=True, exist_ok=True)
        with wave.open(str(path), "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            frames = bytearray()
            for i in range(n_samples):
                val = int(amplitude * math.sin(2 * math.pi * freq * i / sample_rate))
                frames.extend(struct.pack("<h", val))
            wav_file.writeframes(bytes(frames))
