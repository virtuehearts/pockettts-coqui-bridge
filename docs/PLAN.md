# PocketTTS Coqui Bridge Plan (Saved for Future Reference)

This repository now includes an executable command and prompt template so the project can move from planning to implementation.

## What was implemented now
- A CLI command named `pockettts`.
- Input options for direct text or text file.
- Coqui TTS model selection and output path management.
- Optional speaker/language arguments.
- A reusable prompt template for bot integration (`prompts/discord_command_prompt.md`).

## Next steps
1. Add chunking and queue support for long responses.
2. Add bot adapters (Discord and Telegram) around the command.
3. Persist per-guild/per-chat voice settings.
4. Add health checks and startup model warmup.
5. Containerize with GPU/CPU variants.

## Command quickstart
```bash
pockettts "Hello world from PocketTTS" -o artifacts/hello.wav
```

## Notes
- The original requested plan was provided as an external shared link that is not reachable from this environment.
- This saved plan is designed to be a practical bridge aligned with the repo goal and Pocket TTS Web UI style usage.
