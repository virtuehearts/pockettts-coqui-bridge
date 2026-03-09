from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import FileResponse

from app.services.audio import normalize_to_wav, timestamped_output, wav_to_mp3

router = APIRouter(prefix='/api')


def _pick(params: dict, *keys: str, default=None):
    for key in keys:
        if key in params and params[key] not in (None, ""):
            return params[key]
    return default


@router.post('/tts')
async def tts(request: Request):
    settings = request.app.state.settings
    registry = request.app.state.voice_registry
    tts_service = request.app.state.tts_service

    params = {}
    upload_file = None
    ctype = request.headers.get('content-type', '')
    if 'application/json' in ctype:
        params = await request.json()
    else:
        form = await request.form()
        params = dict(form)
        upload_file = form.get('speaker_wav') or form.get('speaker-wav')

    text = _pick(params, 'text')
    if not text:
        raise HTTPException(status_code=400, detail='text is required')

    voice = _pick(params, 'speaker-id', 'speaker_id', 'voice', 'speaker', default=settings.default_voice)
    fmt = _pick(params, 'format', default='wav').lower()
    save_voice = str(_pick(params, 'save_voice', default='false')).lower() in {'1', 'true', 'yes'}
    clone_name = _pick(params, 'clone_name', default='cloned-voice')

    output_wav = settings.output_dir / timestamped_output('tts', '.wav')

    if upload_file and hasattr(upload_file, 'filename'):
        raw = await upload_file.read()
        src = settings.output_dir / timestamped_output('speaker_upload', Path(upload_file.filename).suffix or '.wav')
        src.write_bytes(raw)
        normalized = settings.output_dir / timestamped_output('speaker_norm', '.wav')
        try:
            normalize_to_wav(src, normalized)
            tts_service.ensure_cloning_available()
        except Exception as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        finally:
            src.unlink(missing_ok=True)
        tts_service.synthesize_to_wav(text, voice='clone', output_path=output_wav)
        if save_voice:
            voice_id = clone_name.lower().replace(' ', '-')
            sample_path = settings.voices_dir / f'{voice_id}.wav'
            sample_path.write_bytes(normalized.read_bytes())
            emb_path = settings.embeddings_dir / f'{voice_id}.emb.txt'
            tts_service.clone_and_register_assets(sample_path, emb_path)
            registry.create_cloned(voice_id, clone_name, str(sample_path), str(emb_path))
        normalized.unlink(missing_ok=True)
    else:
        if not registry.get(voice):
            raise HTTPException(status_code=404, detail='voice not found')
        tts_service.synthesize_to_wav(text, voice, output_wav)

    if fmt == 'mp3':
        mp3_path = settings.output_dir / output_wav.with_suffix('.mp3').name
        try:
            wav_to_mp3(output_wav, mp3_path)
        except RuntimeError as exc:
            raise HTTPException(status_code=400, detail=str(exc)) from exc
        return FileResponse(mp3_path, media_type='audio/mpeg', filename=mp3_path.name)

    return FileResponse(output_wav, media_type='audio/wav', filename=output_wav.name)


@router.post('/preview')
async def preview(request: Request):
    if request.app.state.settings.enable_auth:
        request.app.state.auth_service.require_user(request)
    payload = await request.json()
    text = payload.get('text', '').strip()
    voice = payload.get('voice', request.app.state.settings.default_voice)
    if not text:
        raise HTTPException(status_code=400, detail='text is required')
    out = request.app.state.settings.output_dir / timestamped_output('preview', '.wav')
    request.app.state.tts_service.synthesize_to_wav(text, voice, out)
    return {'ok': True, 'audio_url': f'/generated/{out.name}'}


@router.post('/v1/audio/speech')
async def openai_speech(request: Request):
    payload = await request.json()
    text = payload.get('input')
    voice = payload.get('voice', request.app.state.settings.default_voice)
    response_format = payload.get('response_format', 'wav').lower()
    if not text:
        raise HTTPException(status_code=400, detail='input is required')
    out = request.app.state.settings.output_dir / timestamped_output('openai', '.wav')
    request.app.state.tts_service.synthesize_to_wav(text, voice, out)
    if response_format == 'mp3':
        mp3 = out.with_suffix('.mp3')
        wav_to_mp3(out, mp3)
        return FileResponse(mp3, media_type='audio/mpeg', filename=mp3.name)
    return FileResponse(out, media_type='audio/wav', filename=out.name)
