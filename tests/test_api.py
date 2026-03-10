from __future__ import annotations

from pathlib import Path

import io
import wave

from fastapi.testclient import TestClient

from app.main import create_app


def _client(enable_auth: str = "true", hf_token: str = "") -> TestClient:
    import os

    db_path = Path("data/voices.db")
    if db_path.exists():
        db_path.unlink()

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




def test_clone_voice_falls_back_when_model_unavailable():
    client = _client(enable_auth='false')
    files = {'audio_file': ('sample.wav', _wav_bytes(), 'audio/wav')}
    data = {'name': 'my custom voice'}
    resp = client.post('/api/voices/clone', data=data, files=files)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload['id'] == 'my-custom-voice'
    assert payload['sample_path'].endswith('my-custom-voice.wav')
    assert payload['embedding_path'] is None

def test_change_admin_password():
    client = _client(enable_auth='true')
    login = client.post('/login', data={'username': 'admin', 'password': 'pass'})
    assert login.status_code in (200, 302)

    update = client.post('/settings/password', data={
        'current_password': 'pass',
        'new_password': 'newpass123',
        'confirm_password': 'newpass123',
    })
    assert update.status_code == 200

    client.post('/logout')
    bad_old = client.post('/login', data={'username': 'admin', 'password': 'pass'})
    assert bad_old.status_code == 401

    good_new = client.post('/login', data={'username': 'admin', 'password': 'newpass123'})
    assert good_new.status_code in (200, 302)


def test_api_tts_alias_permutations_json():
    client = _client()
    for key in ('speaker-id', 'speaker_id', 'speaker', 'voice'):
        resp = client.post('/api/tts', json={'text': 'hello', key: 'alba'})
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('audio/wav')


def test_api_tts_alias_permutations_multipart():
    client = _client()
    for key in ('speaker-id', 'speaker_id', 'speaker', 'voice'):
        resp = client.post('/api/tts', data={'text': 'hello', key: 'alba'})
        assert resp.status_code == 200
        assert resp.headers['content-type'].startswith('audio/wav')


def test_v1_audio_speech_contract():
    client = _client()
    resp = client.post('/v1/audio/speech', json={'model': 'gpt-4o-mini-tts', 'input': 'hello', 'voice': 'alba'})
    assert resp.status_code == 200
    assert resp.headers['content-type'].startswith('audio/wav')
    assert len(resp.content) > 44


def test_v1_audio_speech_missing_input():
    client = _client()
    resp = client.post('/v1/audio/speech', json={'voice': 'alba'})
    assert resp.status_code == 400
    assert resp.json()['detail'] == 'input is required'


def test_v1_audio_speech_unknown_voice():
    client = _client()
    resp = client.post('/v1/audio/speech', json={'input': 'hello', 'voice': 'unknown-voice'})
    assert resp.status_code == 404
    assert resp.json()['detail'] == 'voice not found'
