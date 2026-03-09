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
