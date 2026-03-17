from __future__ import annotations

import io
import wave
from pathlib import Path

import pytest
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


def test_api_key_lifecycle():
    client = _client(enable_auth="true")
    # Login as admin to manage keys
    login = client.post("/login", data={"username": "admin", "password": "pass"})
    assert login.status_code in (200, 302)

    # Create a key
    resp = client.post("/api-keys/create", data={"name": "test-key"})
    # It might return RedirectResponse 303 or 200 depending on how I called it
    assert resp.status_code in (200, 302, 303)

    # Let's extract it from the HTML (it's inside <code>)
    import re
    match = re.search(r'>(pt_[a-zA-Z0-9_\-]+)</code>', resp.text)
    assert match, "API key not found in response HTML"
    api_key = match.group(1)

    # Verify key appears in list
    resp = client.get("/api-keys")
    assert "test-key" in resp.text

    # Use the key for TTS
    resp = client.post("/api/tts", json={"text": "hello", "voice": "alba"}, headers={"X-API-Key": api_key})
    assert resp.status_code == 200

    # Verify usage incremented
    resp = client.get("/api-keys")
    # Usage of '5' (for 'hello') should be in the table
    assert "5</td>" in resp.text

    # Use key via query param
    resp = client.post(f"/api/tts?api_key={api_key}", json={"text": "hi", "voice": "alba"})
    assert resp.status_code == 200

    # Verify usage incremented again (5 + 2 = 7)
    resp = client.get("/api-keys")
    assert "7</td>" in resp.text

    # Use key for OpenAI endpoint
    resp = client.post("/v1/audio/speech",
                       json={"input": "test", "voice": "alba"},
                       headers={"Authorization": f"Bearer {api_key}"})
    assert resp.status_code == 200

    # Verify usage (7 + 4 = 11)
    resp = client.get("/api-keys")
    assert "11</td>" in resp.text

    # Delete the key
    # First get key_id from the list. It's in the hidden input.
    match_id = re.search(r'name="key_id" value="([a-f0-9]+)"', resp.text)
    assert match_id
    key_id = match_id.group(1)

    resp = client.post("/api-keys/delete", data={"key_id": key_id}, follow_redirects=True)
    assert resp.status_code == 200
    assert "test-key" not in resp.text

    # Logout to ensure we are testing ONLY the API key authentication
    client.post("/logout")

    # Key should no longer work
    resp = client.post("/api/tts", json={"text": "hello", "voice": "alba"}, headers={"X-API-Key": api_key})
    assert resp.status_code == 401

def test_tts_requires_auth_when_enabled():
    client = _client(enable_auth="true")
    resp = client.post("/api/tts", json={"text": "hello", "voice": "alba"})
    assert resp.status_code == 401

def test_tts_works_without_key_when_auth_disabled():
    client = _client(enable_auth="false")
    resp = client.post("/api/tts", json={"text": "hello", "voice": "alba"})
    assert resp.status_code == 200

def test_v1_mp3_output():
    client = _client(enable_auth="false")
    resp = client.post("/v1/audio/speech", json={"input": "hello", "voice": "alba", "response_format": "mp3"})
    if resp.status_code == 400 and "ffmpeg is required" in resp.json().get("detail", ""):
        return
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/mpeg"

def test_api_tts_mp3_output():
    client = _client(enable_auth="false")
    resp = client.post("/api/tts", json={"text": "hello", "voice": "alba", "format": "mp3"})
    if resp.status_code == 400 and "ffmpeg is required" in resp.json().get("detail", ""):
        return
    assert resp.status_code == 200
    assert resp.headers["content-type"] == "audio/mpeg"
