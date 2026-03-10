# Task List (derived from `docs/PLAN.md`)

## Goal for this iteration
Make the bridge actually usable with `kyutai-labs/pocket-tts` for local testing while preserving fallback behavior when model dependencies are unavailable.

## Tasks
- [x] Replace the tone-only synthesizer path with real `pocket-tts` model calls when available.
- [x] Keep graceful fallback synthesis when `pocket-tts` is not installed or model init fails.
- [x] Support cloned voice assets as fast-load Pocket-TTS state files (`.safetensors`).
- [x] Wire cloned voice metadata (`sample_path`, `embedding_path`) into all synthesis routes.
- [x] Improve health output to report engine initialization errors.
- [x] Update setup docs so local testing with `pocket-tts` is straightforward.

## Next tasks
- [x] Add warm-up at app startup to pre-load model and first voice state.
- [x] Add API contract tests for OpenAI-format + multipart alias permutations.
- [ ] Add integration tests covering cloned voice lifecycle end-to-end.
