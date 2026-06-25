#!/usr/bin/env python3
"""
AI Voice Over — CLI / Text Mode
================================
Usage examples:

  # Single text argument
  python cli.py "Hello, welcome to AI Voice Over!"

  # Interactive mode
  python cli.py --interactive

  # Read from stdin (pipe)
  echo "Today is a great day." | python cli.py

  # Save audio to file instead of playing
  python cli.py "Hello world" --output hello.mp3

  # Choose a different character and voice
  python cli.py "Good evening, folks." --character professional --voice en-GB-SoniaNeural

  # Use offline TTS (no internet required)
  python cli.py "Hello world" --engine pyttsx3 --no-llm

  # Indonesian voice example
  python cli.py "Selamat datang di aplikasi voice over AI." --voice id-ID-GadisNeural
"""

import argparse
import os
import subprocess
import sys
import tempfile

BANNER = r"""
  ___   _____   ____  _               ___                     
 / _ \ |_   _| / ___|| |             / _ \__   _____ _ __     
| | | |  | |   \___ \| |   ___  __  | | | \ \ / / _ \ '__|   
| |_| |  | |    ___) | |__/ _ \/ _| | |_| |\ V /  __/ |      
 \___/   |_|   |____/|_____\___/\__|  \___/  \_/ \___|_|      
"""


def _play_audio(audio_bytes: bytes, audio_format: str = "mp3") -> None:
    """Write audio to a temp file and play it using available system tools."""
    suffix = f".{audio_format}"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        tmp.write(audio_bytes)
        tmp_path = tmp.name

    try:
        players = {
            "mp3": ["mpg123", "mpv", "ffplay", "mplayer", "cvlc"],
            "wav": ["aplay", "paplay", "mpv", "ffplay", "mplayer", "cvlc"],
        }
        for player in players.get(audio_format, ["mpv", "ffplay"]):
            try:
                subprocess.run(
                    [player, tmp_path],
                    check=True,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
                return
            except (FileNotFoundError, subprocess.CalledProcessError):
                continue
        print(
            f"[WARN] No audio player found. Audio saved to {tmp_path}",
            file=sys.stderr,
        )
        tmp_path = None  # Prevent deletion so user can access the file
    finally:
        if tmp_path and os.path.exists(tmp_path):
            os.unlink(tmp_path)


def _process(text: str, args: argparse.Namespace) -> None:
    """Run the full pipeline: optional LLM → TTS → play/save."""
    from core.llm import generate_narration
    from core.tts import synthesize

    narration = text

    if not args.no_llm:
        print("⚙  Generating AI narration …", file=sys.stderr)
        try:
            narration = generate_narration(
                text,
                model=args.model,
                character=args.character,
            )
            print(f"📝 Narration:\n{narration}\n", file=sys.stderr)
        except Exception as exc:
            print(
                f"[WARN] LLM unavailable ({exc}). Using raw text.",
                file=sys.stderr,
            )
            narration = text

    print("🔊 Synthesizing voice …", file=sys.stderr)
    audio_bytes, mime_type = synthesize(narration, engine=args.engine, voice=args.voice)
    audio_format = "mp3" if args.engine == "edge_tts" else "wav"

    if args.output:
        with open(args.output, "wb") as fh:
            fh.write(audio_bytes)
        print(f"✅ Audio saved → {args.output}", file=sys.stderr)
    else:
        _play_audio(audio_bytes, audio_format)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="voiceover-cli",
        description="AI Voice Over — CLI / Text Mode",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Text to convert to speech. If omitted, reads from stdin.",
    )
    parser.add_argument(
        "--model",
        default="llama3",
        metavar="MODEL",
        help="Ollama model tag (default: llama3).",
    )
    parser.add_argument(
        "--character",
        default="friendly",
        choices=["friendly", "professional", "storyteller", "assistant"],
        help="AI character personality (default: friendly).",
    )
    parser.add_argument(
        "--engine",
        default="edge_tts",
        choices=["edge_tts", "pyttsx3"],
        help="TTS engine (default: edge_tts).",
    )
    parser.add_argument(
        "--voice",
        default="en-US-JennyNeural",
        metavar="VOICE",
        help="Voice name for edge_tts (default: en-US-JennyNeural).",
    )
    parser.add_argument(
        "--no-llm",
        action="store_true",
        help="Skip LLM processing; use the input text directly for TTS.",
    )
    parser.add_argument(
        "--output",
        "-o",
        metavar="FILE",
        help="Save audio to FILE instead of playing it.",
    )
    parser.add_argument(
        "--interactive",
        "-i",
        action="store_true",
        help="Run in interactive mode (keeps prompting for text).",
    )
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List locally available Ollama models and exit.",
    )
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    print(BANNER, file=sys.stderr)

    if args.list_models:
        from core.llm import list_local_models

        models = list_local_models()
        if models:
            print("Available Ollama models:")
            for m in models:
                print(f"  • {m}")
        else:
            print("No Ollama models found (is Ollama running?).")
        return

    if args.interactive:
        print("─" * 50, file=sys.stderr)
        print("Interactive mode  (type 'quit' or press Ctrl-C to exit)", file=sys.stderr)
        print("─" * 50, file=sys.stderr)
        while True:
            try:
                text = input("Enter text › ").strip()
            except (KeyboardInterrupt, EOFError):
                print("\nGoodbye!", file=sys.stderr)
                break
            if text.lower() in ("quit", "exit", "q", ""):
                if text.lower() in ("quit", "exit", "q"):
                    break
                continue
            _process(text, args)
        return

    if args.text:
        _process(args.text, args)
    else:
        # Read from stdin
        print("Reading from stdin (Ctrl-D to finish) …", file=sys.stderr)
        text = sys.stdin.read().strip()
        if text:
            _process(text, args)
        else:
            parser.print_help()
            sys.exit(1)


if __name__ == "__main__":
    main()
