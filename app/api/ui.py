from __future__ import annotations

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


def _guard(request: Request):
    if request.app.state.settings.enable_auth and not request.app.state.auth_service.ui_authenticated(request):
        return RedirectResponse('/login', status_code=302)
    return None


@router.get('/')
def index(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    voices = request.app.state.voice_registry.list_all()
    return request.app.state.templates.TemplateResponse('index.html', {'request': request, 'voices': voices})


@router.get('/voices')
def voices_page(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    voices = [v for v in request.app.state.voice_registry.list_all() if v['type'] == 'cloned']
    return request.app.state.templates.TemplateResponse('voices.html', {'request': request, 'voices': voices})


@router.get('/voices/new')
def voices_new_page(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    return request.app.state.templates.TemplateResponse('voices_new.html', {'request': request})


@router.get('/settings')
def settings_page(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    health_data = {
        'auth_enabled': request.app.state.settings.enable_auth,
        'hf_token_set': bool(request.app.state.settings.hf_token),
        'dirs': {
            'voices': str(request.app.state.settings.voices_dir),
            'embeddings': str(request.app.state.settings.embeddings_dir),
            'output': str(request.app.state.settings.output_dir),
        },
    }
    return request.app.state.templates.TemplateResponse('settings.html', {'request': request, 'health': health_data})
