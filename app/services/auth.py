from __future__ import annotations

from fastapi import HTTPException, Request

from app.config import Settings


class AuthService:
    def __init__(self, settings: Settings):
        self.settings = settings

    def is_enabled(self) -> bool:
        return self.settings.enable_auth

    def verify_credentials(self, username: str, password: str) -> bool:
        return username == self.settings.app_username and password == self.settings.app_password

    def login(self, request: Request, username: str) -> None:
        request.session["user"] = username

    def logout(self, request: Request) -> None:
        request.session.clear()

    def require_user(self, request: Request) -> None:
        if not self.is_enabled():
            return
        if not request.session.get("user"):
            raise HTTPException(status_code=401, detail="Authentication required")

    def ui_authenticated(self, request: Request) -> bool:
        return (not self.is_enabled()) or bool(request.session.get("user"))
