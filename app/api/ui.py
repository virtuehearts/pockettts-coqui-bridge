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


@router.get('/settings')
def settings_page(request: Request, message: str | None = None, error: bool = False):
    guard = _guard(request)
    if guard:
        return guard
    health_data = {
        'auth_enabled': request.app.state.settings.enable_auth,
        'hf_token_set': bool(request.app.state.settings.hf_token),
        'hf_token': request.app.state.settings.hf_token if request.app.state.settings.hf_token else "",
        'dirs': {
            'voices': str(request.app.state.settings.voices_dir),
            'embeddings': str(request.app.state.settings.embeddings_dir),
            'output': str(request.app.state.settings.output_dir),
        },
    }
    return request.app.state.templates.TemplateResponse('settings.html', {'request': request, 'health': health_data, 'message': message, 'error': error})


@router.get('/api-keys')
def api_keys_page(request: Request, new_key: str | None = None):
    guard = _guard(request)
    if guard:
        return guard
    keys = request.app.state.auth_service.list_api_keys()
    return request.app.state.templates.TemplateResponse('api_keys.html', {'request': request, 'keys': keys, 'new_key': new_key})


@router.post('/api-keys/create')
async def create_api_key(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    form = await request.form()
    name = form.get('name', 'New Key')
    new_key = request.app.state.auth_service.create_api_key(name)
    keys = request.app.state.auth_service.list_api_keys()
    return request.app.state.templates.TemplateResponse('api_keys.html', {'request': request, 'keys': keys, 'new_key': new_key})


@router.post('/api-keys/delete')
async def delete_api_key(request: Request):
    guard = _guard(request)
    if guard:
        return guard
    form = await request.form()
    key_id = form.get('key_id')
    if key_id:
        request.app.state.auth_service.delete_api_key(key_id)
    return RedirectResponse('/api-keys', status_code=303)


@router.post('/settings/hf_token')
async def update_hf_token(request: Request):
    guard = _guard(request)
    if guard:
        return guard

    from fastapi import Form
    form_data = await request.form()
    hf_token = form_data.get('hf_token', '').strip()

    from app.db import connect
    from pathlib import Path
    db_path = Path("data/voices.db")
    with connect(db_path) as conn:
        conn.execute("INSERT OR REPLACE INTO app_config (key, value) VALUES ('hf_token', ?)", (hf_token,))
        conn.commit()

    request.app.state.settings.hf_token = hf_token

    # Reload the model to pick up the new token
    request.app.state.tts_service.reload_model()

    # Check if cloning is now available
    availability = request.app.state.tts_service.availability()
    if availability['cloning_available']:
        msg = "HuggingFace token updated and voice cloning is now ENABLED."
        err = False
    elif availability['available']:
        msg = "HuggingFace token updated, but voice cloning is still UNSUPPORTED. Verify your token has access to the model."
        err = True
    else:
        msg = f"HuggingFace token updated, but model failed to load: {availability.get('error', 'Unknown error')}"
        err = True

    return settings_page(request, message=msg, error=err)
