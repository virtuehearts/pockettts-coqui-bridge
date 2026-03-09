from __future__ import annotations

import io
import wave

from fastapi.testclient import TestClient

from app.main import create_app


def _client(enable_auth: str = "true", hf_token: str = "") -> TestClient:
    import os

    os.environ["ENABLE_AUTH"] = enable_auth
    os.environ["APP_USERNAME"] = "admin"
    os.environ["APP_PASSWORD"] = "pass"
    os.environ["SESSION_SECRET"] = "secret"
    os.environ["HF_TOKEN"] = hf_token
    return TestClient(create_app())


def _wav_bytes() -> bytes:
    bio = io.BytesIO()
    with wave.open(bio, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(22050)
        w.writeframes(b"\x00\x00" * 22050)
    return bio.getvalue()


def test_health():
    client = _client()
    resp = client.get('/health')
    assert resp.status_code == 200
    payload = resp.json()
    assert payload['status'] == 'ok'
    assert 'auth_enabled' in payload


def test_api_voices():
    client = _client()
    resp = client.get('/api/voices')
    assert resp.status_code == 200
    assert any(v['id'] == 'alba' for v in resp.json()['voices'])


def test_api_tts_builtin_voice():
    client = _client()
    resp = client.post('/api/tts', json={'text': 'hello', 'voice': 'alba'})
    assert resp.status_code == 200
    assert resp.headers['content-type'].startswith('audio/wav')
    assert len(resp.content) > 44


def test_clone_requires_auth():
    client = _client(enable_auth='true')
    files = {'audio_file': ('sample.wav', _wav_bytes(), 'audio/wav')}
    data = {'name': 'my voice'}
    resp = client.post('/api/voices/clone', data=data, files=files)
    assert resp.status_code == 401
