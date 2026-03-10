from __future__ import annotations

import math
import os
import struct
import threading
import wave
from pathlib import Path

from app.config import Settings


class PocketTTSService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self.backend_name = "pocket-tts"
        self._lock = threading.Lock()
        self._model = None
        self._export_model_state = None
        self._voice_state_cache: dict[str, object] = {}
        self._init_error: str | None = None

    def availability(self) -> dict:
        self._ensure_model_loaded()
        return {
            "engine": self.backend_name,
            "available": self._model is not None,
            "model_ready": self._model is not None,
            "cloning_available": self._model is not None,
            "error": self._init_error,
        }

    def ensure_cloning_available(self) -> None:
        self._ensure_model_loaded()
        if self._model is None:
            raise RuntimeError(
                "Pocket-TTS model is unavailable. Install dependencies (`pip install pocket-tts torch`) and ensure model assets can be downloaded."
            )

    def synthesize_to_wav(
        self,
        text: str,
        voice: str,
        output_path: Path,
        *,
        voice_sample: str | None = None,
        voice_embedding: str | None = None,
    ) -> Path:
        self._ensure_model_loaded()
        if self._model is None:
            freq = 220 if voice == "alba" else 280 if voice == "sol" else 330
            duration = max(0.35, min(4.0, len(text) * 0.03))
            self._write_tone(output_path, freq=freq, duration_s=duration)
            return output_path

        model = self._model
        voice_prompt = voice_embedding or voice_sample or voice
        cache_key = str(voice_prompt)

        if cache_key not in self._voice_state_cache:
            self._voice_state_cache[cache_key] = model.get_state_for_audio_prompt(voice_prompt)

        audio = model.generate_audio(self._voice_state_cache[cache_key], text)
        self._write_tensor_wav(output_path, audio, sample_rate=model.sample_rate)
        return output_path


    def warm_up(self, default_voice: str) -> None:
        """Best-effort model and default voice state warm-up."""
        self._ensure_model_loaded()
        if self._model is None:
            return
        try:
            if default_voice not in self._voice_state_cache:
                self._voice_state_cache[default_voice] = self._model.get_state_for_audio_prompt(default_voice)
        except Exception:
            # Keep warm-up non-fatal; synth requests can still proceed with lazy loading.
            return

    def clone_and_register_assets(self, sample_wav_path: Path, embedding_path: Path) -> None:
        self.ensure_cloning_available()
        model = self._model
        state = model.get_state_for_audio_prompt(str(sample_wav_path))
        embedding_path.parent.mkdir(parents=True, exist_ok=True)
        self._export_model_state(state, str(embedding_path))
        self._voice_state_cache[str(embedding_path)] = state

    def _ensure_model_loaded(self) -> None:
        if self._model is not None or self._init_error is not None:
            return
        with self._lock:
            if self._model is not None or self._init_error is not None:
                return
            try:
                os.environ.setdefault("HF_HOME", str(self.settings.hf_cache_dir))
                os.environ.setdefault("HUGGINGFACE_HUB_CACHE", str(self.settings.hf_cache_dir))
                if self.settings.hf_token:
                    os.environ["HF_TOKEN"] = self.settings.hf_token

                from pocket_tts import TTSModel, export_model_state

                self._model = TTSModel.load_model()
                self._export_model_state = export_model_state
            except Exception as exc:
                self._init_error = str(exc)

    @staticmethod
    def _write_tensor_wav(path: Path, audio, sample_rate: int) -> None:
        import scipy.io.wavfile

        path.parent.mkdir(parents=True, exist_ok=True)
        scipy.io.wavfile.write(str(path), sample_rate, audio.detach().cpu().numpy())

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
