from __future__ import annotations

from pydantic import BaseModel


class VoiceRecord(BaseModel):
    id: str
    name: str
    type: str
    language: str = "en"
    sample_url: str | None = None


class OpenAISpeechRequest(BaseModel):
    model: str = "pocket-tts"
    input: str
    voice: str = "alba"
    response_format: str = "wav"
