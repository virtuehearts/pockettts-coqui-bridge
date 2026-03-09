from __future__ import annotations

import shutil
import subprocess
import wave
from datetime import datetime, timezone
from pathlib import Path


SUPPORTED_UPLOAD_EXTENSIONS = {".wav", ".mp3", ".m4a", ".flac"}


def sanitize_voice_id(name: str) -> str:
    base = "".join(ch.lower() if ch.isalnum() else "-" for ch in name).strip("-")
    return base or "voice"


def timestamped_output(prefix: str, suffix: str = ".wav") -> str:
    return f"{prefix}_{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{suffix}"


def validate_upload(filename: str, size_bytes: int, max_upload_mb: int) -> None:
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_UPLOAD_EXTENSIONS:
        raise ValueError(f"Unsupported upload format: {ext}")
    if size_bytes > max_upload_mb * 1024 * 1024:
        raise ValueError(f"Upload exceeds max size of {max_upload_mb} MB")


def ffmpeg_available() -> bool:
    return shutil.which("ffmpeg") is not None


def normalize_to_wav(source: Path, target: Path) -> Path:
    if source.suffix.lower() == ".wav":
        if source != target:
            target.write_bytes(source.read_bytes())
        return target
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg is required for non-wav uploads but is not installed")
    cmd = ["ffmpeg", "-y", "-i", str(source), "-ar", "22050", "-ac", "1", str(target)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg conversion failed: {proc.stderr.strip()}")
    return target


def wav_to_mp3(source_wav: Path, target_mp3: Path) -> Path:
    if not ffmpeg_available():
        raise RuntimeError("ffmpeg is required for mp3 output but is not installed")
    cmd = ["ffmpeg", "-y", "-i", str(source_wav), str(target_mp3)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        raise RuntimeError(f"ffmpeg mp3 conversion failed: {proc.stderr.strip()}")
    return target_mp3


def wav_duration_seconds(path: Path) -> float:
    with wave.open(str(path), "rb") as wf:
        return wf.getnframes() / float(wf.getframerate() or 1)
