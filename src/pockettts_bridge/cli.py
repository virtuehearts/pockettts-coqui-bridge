from __future__ import annotations

import argparse
from pathlib import Path


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="pockettts",
        description=(
            "Generate speech from text using Coqui TTS. "
            "Designed as a bridge command for Pocket TTS-style workflows."
        ),
    )
    parser.add_argument(
        "text",
        nargs="?",
        default=None,
        help="Text to synthesize. If omitted, --text-file is required.",
    )
    parser.add_argument(
        "--text-file",
        type=Path,
        help="Path to a UTF-8 text file used as synthesis input.",
    )
    parser.add_argument(
        "--output",
        "-o",
        type=Path,
        default=Path("output.wav"),
        help="Output WAV file path (default: output.wav).",
    )
    parser.add_argument(
        "--model",
        default="tts_models/en/ljspeech/tacotron2-DDC",
        help="Coqui model name.",
    )
    parser.add_argument("--speaker", default=None, help="Optional speaker id/name.")
    parser.add_argument("--language", default=None, help="Optional language code.")
    parser.add_argument(
        "--device",
        choices=["auto", "cpu", "cuda"],
        default="auto",
        help="Execution device hint for TTS model loading.",
    )
    return parser


def _resolve_text(args: argparse.Namespace) -> str:
    if args.text_file:
        file_text = args.text_file.read_text(encoding="utf-8").strip()
        if not file_text:
            raise ValueError("Input text file is empty.")
        return file_text

    if args.text and args.text.strip():
        return args.text.strip()

    raise ValueError("No text provided. Use positional text or --text-file.")


def run(args: argparse.Namespace) -> Path:
    text = _resolve_text(args)
    args.output.parent.mkdir(parents=True, exist_ok=True)

    from TTS.api import TTS

    if args.device == "auto":
        tts = TTS(model_name=args.model)
    else:
        tts = TTS(model_name=args.model, gpu=(args.device == "cuda"))

    tts.tts_to_file(
        text=text,
        speaker=args.speaker,
        language=args.language,
        file_path=str(args.output),
    )
    return args.output


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    path = run(args)
    print(f"Created audio: {path}")


if __name__ == "__main__":
    main()
