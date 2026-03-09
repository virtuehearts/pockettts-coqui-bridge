from __future__ import annotations

import hashlib
import hmac
import secrets

from fastapi import HTTPException, Request

from app.config import Settings
from app.db import connect


class AuthService:
    def __init__(self, settings: Settings, db_path):
        self.settings = settings
        self.db_path = db_path
        self._seed_admin_credentials()

    def _hash_password(self, password: str, salt: str | None = None) -> str:
        raw_salt = salt or secrets.token_hex(16)
        digest = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), raw_salt.encode('utf-8'), 200000).hex()
        return f"pbkdf2_sha256${raw_salt}${digest}"

    def _verify_password(self, password: str, password_hash: str) -> bool:
        scheme, salt, digest = password_hash.split('$', 2)
        if scheme != 'pbkdf2_sha256':
            return False
        candidate = self._hash_password(password, salt)
        return hmac.compare_digest(candidate, password_hash)

    def _seed_admin_credentials(self) -> None:
        with connect(self.db_path) as conn:
            for key, value in (
                ('admin_username', self.settings.app_username),
                ('admin_password_hash', self._hash_password(self.settings.app_password)),
            ):
                row = conn.execute('SELECT value FROM app_config WHERE key = ?', (key,)).fetchone()
                if not row:
                    conn.execute('INSERT INTO app_config (key, value) VALUES (?, ?)', (key, value))
            conn.commit()

    def _get_config(self, key: str, fallback: str) -> str:
        with connect(self.db_path) as conn:
            row = conn.execute('SELECT value FROM app_config WHERE key = ?', (key,)).fetchone()
        return row['value'] if row else fallback

    def _set_config(self, key: str, value: str) -> None:
        with connect(self.db_path) as conn:
            conn.execute(
                'INSERT INTO app_config (key, value) VALUES (?, ?) ON CONFLICT(key) DO UPDATE SET value = excluded.value',
                (key, value),
            )
            conn.commit()

    def is_enabled(self) -> bool:
        return self.settings.enable_auth

    def verify_credentials(self, username: str, password: str) -> bool:
        current_user = self._get_config('admin_username', self.settings.app_username)
        current_hash = self._get_config('admin_password_hash', self._hash_password(self.settings.app_password))
        return username == current_user and self._verify_password(password, current_hash)

    def update_admin_password(self, current_password: str, new_password: str) -> None:
        current_hash = self._get_config('admin_password_hash', self._hash_password(self.settings.app_password))
        if not self._verify_password(current_password, current_hash):
            raise ValueError('Current password is incorrect')
        self._set_config('admin_password_hash', self._hash_password(new_password))

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
