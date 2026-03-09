from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from starlette.templating import Jinja2Templates

from app.api import auth, health, tts, ui, voices
from app.config import get_settings
from app.db import init_db
from app.services.auth import AuthService
from app.services.pockettts import PocketTTSService
from app.services.voice_registry import VoiceRegistry


def create_app() -> FastAPI:
    settings = get_settings()

    for p in (settings.voices_dir, settings.embeddings_dir, settings.output_dir, settings.hf_cache_dir):
        p.mkdir(parents=True, exist_ok=True)

    db_path = Path('data/voices.db')
    init_db(db_path)

    app = FastAPI(title='pockettts-coqui-bridge')
    app.add_middleware(SessionMiddleware, secret_key=settings.session_secret)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=['*'],
        allow_headers=['*'],
    )

    app.state.settings = settings
    app.state.voice_registry = VoiceRegistry(db_path)
    app.state.tts_service = PocketTTSService(settings)
    app.state.auth_service = AuthService(settings)
    app.state.templates = Jinja2Templates(directory='app/templates')

    app.mount('/static', StaticFiles(directory='app/static'), name='static')
    app.mount('/generated', StaticFiles(directory=str(settings.output_dir)), name='generated')

    app.include_router(health.router)
    app.include_router(auth.router)
    app.include_router(ui.router)
    app.include_router(voices.router)
    app.include_router(tts.router)

    return app


app = create_app()
