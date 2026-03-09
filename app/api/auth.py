from __future__ import annotations

from fastapi import APIRouter, Form, Request
from fastapi.responses import RedirectResponse

router = APIRouter()


@router.get('/login')
def login_page(request: Request):
    if request.app.state.auth_service.ui_authenticated(request):
        return RedirectResponse(url='/', status_code=302)
    return request.app.state.templates.TemplateResponse('login.html', {'request': request, 'error': None})


@router.post('/login')
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    auth = request.app.state.auth_service
    if (not auth.is_enabled()) or auth.verify_credentials(username, password):
        auth.login(request, username)
        return RedirectResponse(url='/', status_code=302)
    return request.app.state.templates.TemplateResponse('login.html', {'request': request, 'error': 'Invalid credentials'}, status_code=401)


@router.post('/logout')
def logout(request: Request):
    request.app.state.auth_service.logout(request)
    return RedirectResponse(url='/login', status_code=302)


@router.post('/settings/password')
def update_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
):
    auth = request.app.state.auth_service
    auth.require_user(request)
    if len(new_password) < 8:
        return request.app.state.templates.TemplateResponse(
            'settings.html',
            {'request': request, 'health': _health_data(request), 'message': 'Password must be at least 8 characters', 'error': True},
            status_code=400,
        )
    if new_password != confirm_password:
        return request.app.state.templates.TemplateResponse(
            'settings.html',
            {'request': request, 'health': _health_data(request), 'message': 'New passwords do not match', 'error': True},
            status_code=400,
        )
    try:
        auth.update_admin_password(current_password, new_password)
    except ValueError as exc:
        return request.app.state.templates.TemplateResponse(
            'settings.html',
            {'request': request, 'health': _health_data(request), 'message': str(exc), 'error': True},
            status_code=400,
        )

    return request.app.state.templates.TemplateResponse(
        'settings.html',
        {'request': request, 'health': _health_data(request), 'message': 'Admin password updated', 'error': False},
    )


def _health_data(request: Request) -> dict:
    return {
        'auth_enabled': request.app.state.settings.enable_auth,
        'hf_token_set': bool(request.app.state.settings.hf_token),
        'dirs': {
            'voices': str(request.app.state.settings.voices_dir),
            'embeddings': str(request.app.state.settings.embeddings_dir),
            'output': str(request.app.state.settings.output_dir),
        },
    }
