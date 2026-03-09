# PocketTTS Coqui Bridge – Current Status and Remaining Work

This plan reflects the current repository state and highlights what is still required to reach a production-ready, fully tested bridge.

## Current implementation status

### Core architecture and local startup
- ✅ FastAPI app initializes runtime directories at startup.
- ✅ SQLite database (`data/voices.db`) is initialized automatically and stores voice metadata.
- ✅ Environment-driven configuration exists with sane defaults (`HF_TOKEN`, `APP_USERNAME`, `APP_PASSWORD`, `SESSION_SECRET`, `ENABLE_AUTH`, `PORT`).
- ✅ Dockerfile is present for containerized local runs with persisted `/app/data`.

### API compatibility and endpoints
- ✅ `POST /api/tts` supports JSON and multipart form payloads.
- ✅ Coqui-style voice aliases are supported (`speaker-id`, `speaker_id`, `speaker`, `voice`).
- ✅ `POST /v1/audio/speech` OpenAI-style endpoint is available.
- ✅ `GET /health` and `GET /api/voices` are implemented.
- ⚠️ Contract/compatibility tests against a Moltis-like client matrix are still limited.

### TTS engine and cloning
- ✅ `PocketTTSService` attempts real `pocket-tts` model loading and synthesis when dependencies are available.
- ✅ Cloning stores local sample + embedding/state artifacts under `data/voices` and `data/embeddings`.
- ✅ Health reports backend availability and model initialization error details.
- ⚠️ Service still includes tone-generation fallback when model init fails; this is useful for dev, but should be clearly framed as degraded mode.
- ⚠️ Startup warm-up/preload for model and common voice state is not implemented.

### Admin UI
- ✅ Login flow and admin pages exist (`/`, `/voices`, `/voices/new`, `/settings`).
- ✅ Voice deletion is available from the UI.
- ✅ Settings page includes password update path.
- ⚠️ Voice rename/edit controls are still missing in the UI (API supports update).
- ⚠️ Voice preview controls and richer operator diagnostics are still missing.

### Testing and quality
- ✅ Basic API/CLI tests exist in `tests/`.
- ⚠️ End-to-end cloned voice lifecycle tests are incomplete.
- ⚠️ Browser/UI automation (Playwright) is not yet added to the repository test suite.
- ⚠️ Explicit compatibility test matrix for multipart alias permutations and `/v1/audio/speech` contract behavior is still incomplete.

## Estimated completion
- **Estimated overall completion: ~78%**

Rationale:
- API + persistence + auth/UI scaffold are largely in place.
- Real backend integration path exists.
- Remaining work is primarily around hardening, compatibility contract coverage, UX completeness, and end-to-end test automation.

## Remaining work to reach 100%

### 1) Engine reliability and runtime behavior
1. Add startup warm-up for model initialization and one default voice state load.
2. Add clear degraded-mode indicator in UI and API docs when fallback synthesis is active.
3. Define and test timeout/memory guardrails for long synthesis inputs.

### 2) Voice lifecycle completion
1. Add rename/edit voice controls in `/voices` UI and wire to update endpoint.
2. Add voice preview playback in voice management pages.
3. Add optional “import local packaged voice assets” workflow with metadata manifest validation.

### 3) Compatibility hardening
1. Add table-driven contract tests for all Coqui alias permutations (JSON + multipart).
2. Add stricter response/error schema consistency tests for `/api/tts` and `/v1/audio/speech`.
3. Validate behavior against representative Moltis request patterns.

### 4) Test coverage and developer ergonomics
1. Add integration tests with temporary DB/data directories for clone → list → synth → delete lifecycle.
2. Add browser UI tests for login, synth submission, clone flow, delete flow, and settings update.
3. Add make targets (or equivalent scripts) for `test`, `test-api`, and `test-ui`.

### 5) Docs and operations
1. Document fallback vs real-model behavior more explicitly in README.
2. Document recommended production env vars and persistent volume strategy.
3. Add troubleshooting section for model download/cache failures.

## Definition of done
- Real `pocket-tts` synthesis/cloning path works reliably in local and container runs.
- Degraded fallback behavior is explicit, intentional, and observable.
- Full voice lifecycle is available in the admin UI (create/list/preview/rename/delete).
- API compatibility is proven by contract tests for Coqui/Moltis-style usage.
- UI and API automated tests pass in CI.
