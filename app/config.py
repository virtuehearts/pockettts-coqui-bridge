from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    hf_token: str
    app_username: str
    app_password: str
    session_secret: str
    host: str = "0.0.0.0"
    port: int = 8000
    enable_auth: bool = True
    log_level: str = "info"
    voices_dir: Path = Path("data/voices")
    embeddings_dir: Path = Path("data/embeddings")
    output_dir: Path = Path("data/output")
    hf_cache_dir: Path = Path("data/hf-cache")
    default_voice: str = "alba"
    max_upload_size_mb: int = 25
    cors_origins: list[str] = None

    def __post_init__(self) -> None:
        if self.cors_origins is None:
            self.cors_origins = ["*"]



def _bool_env(name: str, default: bool) -> bool:
    value = os.getenv(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}



def get_settings() -> Settings:
    return Settings(
        hf_token=os.getenv("HF_TOKEN", ""),
        app_username=os.getenv("APP_USERNAME", "admin"),
        app_password=os.getenv("APP_PASSWORD", "change_me"),
        session_secret=os.getenv("SESSION_SECRET", "change_this_to_a_long_random_string"),
        port=int(os.getenv("PORT", "8000")),
        enable_auth=_bool_env("ENABLE_AUTH", True),
    )
