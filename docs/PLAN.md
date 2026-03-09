# PocketTTS Coqui Bridge – Implementation Status and 100% Completion Plan

This document maps the current repository state to the product goals and lists the remaining tasks to make the project fully production-ready and easy to test locally.

## Current implementation status

### Core architecture and local startup
- ✅ FastAPI app factory exists and initializes all runtime directories at startup.
- ✅ SQLite is initialized automatically (`data/voices.db`) with a `voices` table.
- ✅ `.env.example` is minimal (`HF_TOKEN`, `APP_USERNAME`, `APP_PASSWORD`, `SESSION_SECRET`, optional `PORT`, `ENABLE_AUTH`).
- ⚠️ Containerization scaffolding (`Dockerfile`, compose, healthcheck wiring) is not yet implemented.

### Coqui/Moltis API compatibility
- ✅ `POST /api/tts` exists and supports JSON and multipart forms with Coqui-like aliases (`speaker-id`, `speaker_id`, `speaker`, `voice`).
- ✅ `POST /v1/audio/speech` exists for OpenAI-style compatibility.
- ✅ `GET /health` and `GET /api/voices` exist.
- ⚠️ Response and error schemas are practical but not yet validated against Moltis integration tests.

### Voice support (built-in + cloned)
- ✅ Built-in voices are available without `HF_TOKEN`.
- ✅ Cloned voices are stored in SQLite and can be listed/updated/deleted.
- ✅ Voice sample and embedding artifacts are persisted under `data/voices` and `data/embeddings`.
- ⚠️ Pre-bundled custom voice import workflow (shipping ready-made local voices with package) is not implemented yet.

### Cloning workflow
- ✅ Clone endpoint and UI flow exist (`/api/voices/clone`, `/voices/new`).
- ⚠️ Cloning currently hard-requires `HF_TOKEN` in the service layer.
- ⚠️ Current PocketTTS implementation is a placeholder/stub synthesizer (tone generator), not full Pocket-TTS inference for either synthesis or cloning.

### Browser UI
- ✅ Login page, synth form, voice selector, output format selector, create clone page, delete flow, settings page exist.
- ⚠️ Rename voice UI is missing (API endpoint exists but no UI control).
- ⚠️ Health/settings page is basic and not yet an operator-focused dashboard.
- ⚠️ No automated browser/UI test harness exists yet.

## Direct answer to key questions

1. **Is there a local SQLite backend, with default startup behavior?**
   - **Yes.** The app creates and uses `data/voices.db` at startup and creates the `voices` table automatically.

2. **Can custom voices be used later by API without HF token?**
   - **Partially.**
   - Existing cloned voices already stored locally can be used by the API without checking `HF_TOKEN` at synthesis time.
   - Creating *new* cloned voices currently requires `HF_TOKEN`.
   - A first-class “pre-made packaged voices” workflow (import/seed/migrate) is not yet implemented.

3. **How much is implemented overall for your stated goal?**
   - **Estimated overall completion: ~65%**
   - Backend/API scaffold: high
   - Auth/UI scaffold: medium
   - True Pocket-TTS integration + offline/packaged custom-voice lifecycle + UI/compat testing: still pending

## Task list to reach 100% functionality

### Phase 1 — Real engine integration (highest priority)
1. Replace stub synthesis in `PocketTTSService` with real Pocket-TTS inference calls.
2. Implement real voice cloning/embedding generation via Pocket-TTS-supported pipeline.
3. Add deterministic model/cache initialization and startup warmup.
4. Define fallback behavior when model assets are missing (clear health + actionable errors).

### Phase 2 — HF-token-free packaged custom voices
1. Add a `data/packaged_voices/` convention (sample + embedding + metadata manifest).
2. Implement startup seeding: scan packaged voices and upsert them into SQLite.
3. Add migration strategy for packaged voice updates (versioning/hash).
4. Ensure API synthesis path for packaged/custom voices does **not** require `HF_TOKEN`.
5. Add admin action: “import local voice assets” to register new pre-made voices.

### Phase 3 — Coqui/Moltis compatibility hardening
1. Add contract tests for Moltis-compatible request variants.
2. Normalize and document accepted field aliases and default behavior.
3. Add stable error response shape and status code matrix.
4. Add response-time and timeout defaults suitable for local model inference.

### Phase 4 — UI completion
1. Add rename voice form in `/voices` UI and wire to `PUT /api/voices/{id}`.
2. Improve clone flow UX (upload validation, progress, clear failure messages).
3. Add voice preview/play controls in voices management page.
4. Expand settings page: runtime config, model status, storage usage, and API examples.
5. Add CSRF-safe patterns or documented trusted-local deployment assumptions.

### Phase 5 — Testability (API + UI)
1. Keep current API unit tests and expand with:
   - clone success/failure cases,
   - delete/rename cases,
   - OpenAI endpoint format checks,
   - Moltis-compatible multipart permutations.
2. Add integration tests with temporary SQLite DB and temporary data dirs.
3. Add browser UI tests (Playwright) for:
   - login/logout,
   - synth playback flow,
   - clone voice flow,
   - rename/delete flows,
   - settings visibility.
4. Add `make test`, `make test-api`, and `make test-ui` developer commands.

### Phase 6 — Local-to-container readiness
1. Add `Dockerfile` (python:3.11-slim, optional ffmpeg).
2. Add `docker-compose.yml` with mounted `./data` volume.
3. Add startup command + healthcheck + persistent env handling.
4. Verify first-run experience from clean checkout in container.

## Definition of done (100%)
- Real Pocket-TTS synthesis and cloning working locally.
- Packaged custom voices can be shipped and used by API without HF token.
- Moltis can point to endpoint and pass compatibility tests.
- Admin UI supports full voice lifecycle (create/list/preview/rename/delete).
- API + UI automated tests pass in CI.
- Containerized local deployment works with minimal `.env`.
