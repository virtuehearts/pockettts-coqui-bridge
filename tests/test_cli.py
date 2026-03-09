import argparse
from pathlib import Path

from pockettts_bridge.cli import _resolve_text, build_parser


def test_parser_defaults():
    parser = build_parser()
    args = parser.parse_args(["hello"])
    assert args.text == "hello"
    assert args.model == "tts_models/en/ljspeech/tacotron2-DDC"
    assert args.output == Path("output.wav")


def test_resolve_text_from_positional():
    args = argparse.Namespace(text="hi", text_file=None)
    assert _resolve_text(args) == "hi"
