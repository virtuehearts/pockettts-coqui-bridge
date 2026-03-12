import os
import unittest.mock as mock
from pathlib import Path
from app.services.pockettts import PocketTTSService
from app.config import Settings

def test_reload_model_updates_env_and_reloads():
    settings = Settings(
        hf_token="initial_token",
        app_username="admin",
        app_password="password",
        session_secret="secret",
        hf_cache_dir=Path("data/hf-cache")
    )

    with mock.patch("pocket_tts.TTSModel.load_model") as mock_load:
        mock_model = mock.Mock()
        mock_model.has_voice_cloning = False
        mock_load.return_value = mock_model

        service = PocketTTSService(settings)

        # Initial load
        service._ensure_model_loaded()
        assert os.environ.get("HF_TOKEN") == "initial_token"
        assert mock_load.call_count == 1

        # Update settings and reload
        settings.hf_token = "new_token"
        mock_model_v2 = mock.Mock()
        mock_model_v2.has_voice_cloning = True
        mock_load.return_value = mock_model_v2

        service.reload_model()

        assert os.environ.get("HF_TOKEN") == "new_token"
        assert mock_load.call_count == 2
        assert service.availability()["cloning_available"] is True

def test_ensure_cloning_available_checks_attribute():
    settings = Settings(
        hf_token="token",
        app_username="admin",
        app_password="password",
        session_secret="secret"
    )

    with mock.patch("pocket_tts.TTSModel.load_model") as mock_load:
        mock_model = mock.Mock()
        mock_model.has_voice_cloning = False
        mock_load.return_value = mock_model

        service = PocketTTSService(settings)

        import pytest
        with pytest.raises(RuntimeError, match="voice cloning is unsupported"):
            service.ensure_cloning_available()

        mock_model.has_voice_cloning = True
        service.ensure_cloning_available() # Should not raise
