from __future__ import annotations

import json
from pathlib import Path

import io
import zipfile
from fastapi import APIRouter, Body, File, Form, HTTPException, Request, UploadFile
from fastapi.responses import StreamingResponse

from app.services.audio import normalize_to_wav, sanitize_voice_id, timestamped_output, validate_upload

router = APIRouter(prefix='/api')


@router.get('/voices')
def list_voices(request: Request):
    registry = request.app.state.voice_registry
    voices = []
    for voice in registry.list_all():
        voices.append(
            {
                'id': voice['id'],
                'name': voice['name'],
                'type': voice['type'],
                'language': voice.get('language', 'en'),
                'sample_url': f"/api/voice-samples/{voice['id']}.wav",
            }
        )
    return {'voices': voices}


@router.get('/voices/{voice_id}')
def get_voice(voice_id: str, request: Request):
    voice = request.app.state.voice_registry.get(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail='Voice not found')
    return voice


@router.put('/voices/{voice_id}')
def update_voice(voice_id: str, request: Request, payload: dict | None = Body(default=None)):
    request.app.state.auth_service.require_user(request)
    registry = request.app.state.voice_registry
    try:
        payload = payload or {}
        updated = registry.update(voice_id, name=payload.get('name'), metadata=payload.get('metadata'))
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return updated


@router.delete('/voices/{voice_id}')
def delete_voice(voice_id: str, request: Request):
    request.app.state.auth_service.require_user(request)
    registry = request.app.state.voice_registry
    try:
        deleted = registry.delete(voice_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    for key in ('sample_path', 'embedding_path'):
        path = deleted.get(key)
        if path and Path(path).exists():
            Path(path).unlink(missing_ok=True)
    return {'ok': True, 'deleted': voice_id}


@router.post('/voices/clone')
async def clone_voice(
    request: Request,
    name: str = Form(...),
    audio_file: UploadFile = File(...),
    metadata: str | None = Form(default=None),
):
    request.app.state.auth_service.require_user(request)
    settings = request.app.state.settings
    registry = request.app.state.voice_registry
    tts = request.app.state.tts_service

    data = await audio_file.read()
    validate_upload(audio_file.filename or 'upload.wav', len(data), settings.max_upload_size_mb)

    voice_id = sanitize_voice_id(name)
    temp_source = settings.output_dir / timestamped_output('upload', Path(audio_file.filename or 'x.wav').suffix)
    temp_source.write_bytes(data)
    sample_path = settings.voices_dir / f'{voice_id}.wav'
    normalize_to_wav(temp_source, sample_path)
    temp_source.unlink(missing_ok=True)

    embedding_path = settings.embeddings_dir / f'{voice_id}.safetensors'
    persisted_embedding: str | None = str(embedding_path)
    try:
        tts.clone_and_register_assets(sample_path, embedding_path)
    except RuntimeError as exc:
        if 'Pocket-TTS model is unavailable' in str(exc):
            persisted_embedding = None
        else:
            raise HTTPException(status_code=400, detail=str(exc)) from exc

    metadata_json = json.loads(metadata) if metadata else {}
    created = registry.create_cloned(
        voice_id=voice_id,
        name=name,
        sample_path=str(sample_path),
        embedding_path=persisted_embedding,
        metadata=metadata_json,
    )
    return created


@router.get('/voices/{voice_id}/export')
def export_voice(voice_id: str, request: Request):
    registry = request.app.state.voice_registry
    voice = registry.get(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail='Voice not found')

    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zip_file:
        # metadata.json
        metadata = {
            'id': voice['id'],
            'name': voice['name'],
            'type': voice['type'],
            'language': voice.get('language', 'en'),
            'metadata': voice.get('metadata', {}),
        }
        zip_file.writestr('metadata.json', json.dumps(metadata, indent=2))

        # Audio sample
        sample_path = voice.get('sample_path')
        if sample_path and Path(sample_path).exists():
            zip_file.write(sample_path, f"{voice_id}.wav")
        else:
            # Generate a sample if it doesn't exist
            settings = request.app.state.settings
            tts = request.app.state.tts_service
            temp_path = settings.output_dir / f'export_preview_{voice_id}.wav'
            tts.synthesize_to_wav('Hello from PocketTTS sample.', voice_id, temp_path)
            zip_file.write(temp_path, f"{voice_id}.wav")
            temp_path.unlink(missing_ok=True)

    buffer.seek(0)
    return StreamingResponse(
        buffer,
        media_type='application/zip',
        headers={'Content-Disposition': f'attachment; filename=voice_{voice_id}.zip'},
    )


@router.get('/voice-samples/{voice_id}.wav')
def voice_sample(voice_id: str, request: Request):
    settings = request.app.state.settings
    registry = request.app.state.voice_registry
    tts = request.app.state.tts_service
    voice = registry.get(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail='Voice not found')

    out_path = settings.output_dir / f'preview_{voice_id}.wav'
    if voice.get('sample_path') and Path(voice['sample_path']).exists():
        out_path.write_bytes(Path(voice['sample_path']).read_bytes())
    elif not out_path.exists():
        tts.synthesize_to_wav('Hello from PocketTTS sample.', voice_id, out_path)

    from fastapi.responses import FileResponse

    return FileResponse(out_path, media_type='audio/wav', filename=out_path.name)
