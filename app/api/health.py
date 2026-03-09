from __future__ import annotations

from fastapi import APIRouter, Request

router = APIRouter()


@router.get('/health')
def health(request: Request):
    settings = request.app.state.settings
    tts = request.app.state.tts_service
    checks = {
        'voices_dir_writable': settings.voices_dir.exists() and settings.voices_dir.is_dir(),
        'embeddings_dir_writable': settings.embeddings_dir.exists() and settings.embeddings_dir.is_dir(),
        'output_dir_writable': settings.output_dir.exists() and settings.output_dir.is_dir(),
    }
    avail = tts.availability()
    return {
        'status': 'ok',
        'pocket_tts_availability': avail['available'],
        'model_readiness': avail['model_ready'],
        'cloning_available': avail['cloning_available'],
        'directory_checks': checks,
        'auth_enabled': settings.enable_auth,
    }
