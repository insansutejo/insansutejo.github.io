#!/usr/bin/env python3
"""Local Llama voice over app with CLI text mode and built-in web mode."""

from __future__ import annotations

import argparse
import html
import json
import mimetypes
import os
import shlex
import shutil
import subprocess
import sys
import textwrap
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Callable


DEFAULT_OUTPUT_DIR = Path(__file__).resolve().parent / "tmp" / "voiceover-output"


class VoiceoverService:
    def __init__(
        self,
        model: str | None = None,
        ollama_url: str | None = None,
        output_dir: Path | None = None,
        urlopen: Callable = urllib.request.urlopen,
    ) -> None:
        self.model = model or os.getenv("OLLAMA_MODEL", "llama3.1")
        self.ollama_url = ollama_url or os.getenv(
            "OLLAMA_URL", "http://127.0.0.1:11434/api/generate"
        )
        self.output_dir = (output_dir or DEFAULT_OUTPUT_DIR).resolve()
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.urlopen = urlopen

    def build_character_prompt(self, text: str, character: str) -> str:
        return textwrap.dedent(
            f"""
            Kamu adalah sutradara voice over untuk AI lokal.
            Rapikan teks berikut agar lebih enak dibacakan, tetap dalam Bahasa Indonesia,
            dan jaga karakter suara ini: {character.strip() or "natural"}.
            Jangan ubah makna, jangan tambahkan penjelasan lain, cukup hasil naskah final.

            Teks asli:
            {text.strip()}
            """
        ).strip()

    def refine_script(self, text: str, character: str) -> str:
        text = text.strip()
        if not text:
            raise ValueError("Teks tidak boleh kosong.")

        payload = json.dumps(
            {
                "model": self.model,
                "prompt": self.build_character_prompt(text, character),
                "stream": False,
            }
        ).encode("utf-8")
        request = urllib.request.Request(
            self.ollama_url,
            data=payload,
            headers={"Content-Type": "application/json"},
            method="POST",
        )

        try:
            with self.urlopen(request, timeout=30) as response:
                body = json.loads(response.read().decode("utf-8"))
            refined = body.get("response", "").strip()
            return refined or text
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError, OSError):
            return text

    def sanitize_label(self, value: str) -> str:
        cleaned = "".join(char.lower() if char.isalnum() else "-" for char in value.strip())
        cleaned = "-".join(part for part in cleaned.split("-") if part)
        return cleaned or "voice"

    def choose_voice(self, character: str) -> str:
        character_lower = character.lower()
        if any(keyword in character_lower for keyword in ("wanita", "female", "ibu", "girl")):
            return "id+f3"
        if any(keyword in character_lower for keyword in ("deep", "tegas", "male", "pria", "bapak")):
            return "id+m3"
        return "id"

    def resolve_output_path(self, character: str, extension: str = ".wav") -> Path:
        filename = f"{self.sanitize_label(character)}-{datetime.now(timezone.utc).strftime('%Y%m%d%H%M%S%f')}{extension}"
        return (self.output_dir / filename).resolve()

    def safe_audio_path(self, name: str) -> Path:
        candidate = (self.output_dir / Path(name).name).resolve()
        if candidate.parent != self.output_dir or not candidate.exists():
            raise FileNotFoundError(name)
        return candidate

    def detect_tts_command(self) -> list[str]:
        custom_command = os.getenv("VOICEOVER_TTS_COMMAND")
        if custom_command:
            return shlex.split(custom_command)

        for command in ("espeak-ng", "espeak", "say"):
            if shutil.which(command):
                return [command]

        raise RuntimeError(
            "Tidak menemukan TTS lokal. Install espeak-ng/espeak atau set VOICEOVER_TTS_COMMAND."
        )

    def synthesize(self, script: str, character: str, output_path: Path | None = None) -> Path:
        command = self.detect_tts_command()
        output_path = (output_path or self.resolve_output_path(character)).resolve()
        voice = self.choose_voice(character)

        if command[0] == "say":
            output_path = output_path.with_suffix(".aiff")
            final_command = command + ["-o", str(output_path), script]
        elif os.getenv("VOICEOVER_TTS_COMMAND"):
            formatted = [
                part.format(output=str(output_path), text=script, voice=voice) for part in command
            ]
            final_command = formatted
        else:
            final_command = command + ["-w", str(output_path), "-v", voice, script]

        subprocess.run(final_command, check=True)
        return output_path

    def generate(self, text: str, character: str, output_path: Path | None = None) -> dict:
        refined_script = self.refine_script(text, character)
        audio_path = self.synthesize(refined_script, character, output_path=output_path)
        return {
            "character": character.strip() or "natural",
            "original_text": text.strip(),
            "refined_script": refined_script,
            "audio_path": str(audio_path),
            "audio_file": audio_path.name,
        }


def render_page(result: dict | None = None, error: str = "", defaults: dict | None = None) -> str:
    defaults = defaults or {}
    text_value = html.escape(defaults.get("text", ""))
    character_value = html.escape(defaults.get("character", "Narator hangat dan natural"))
    result_html = ""

    if error:
        result_html += f'<div class="notice error">{html.escape(error)}</div>'

    if result:
        result_html += f"""
        <section class="result">
          <h2>Hasil Voice Over</h2>
          <p><strong>Karakter:</strong> {html.escape(result['character'])}</p>
          <p><strong>Naskah final:</strong></p>
          <pre>{html.escape(result['refined_script'])}</pre>
          <audio controls src="/audio/{urllib.parse.quote(result['audio_file'])}"></audio>
          <p class="hint">File audio tersimpan di: <code>{html.escape(result['audio_path'])}</code></p>
        </section>
        """

    return f"""<!doctype html>
<html lang="id">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Local Llama Voice Over</title>
  <style>
    body {{ font-family: Arial, sans-serif; margin: 0; background: #0f172a; color: #e2e8f0; }}
    main {{ max-width: 880px; margin: 0 auto; padding: 32px 20px 48px; }}
    .panel {{ background: #1e293b; border-radius: 16px; padding: 24px; box-shadow: 0 12px 24px rgba(15, 23, 42, 0.35); }}
    h1, h2 {{ margin-top: 0; }}
    label {{ display: block; font-weight: 700; margin-bottom: 8px; }}
    textarea, input {{ width: 100%; box-sizing: border-box; border-radius: 10px; border: 1px solid #475569; background: #0f172a; color: #e2e8f0; padding: 12px; margin-bottom: 16px; }}
    textarea {{ min-height: 180px; resize: vertical; }}
    button {{ border: 0; border-radius: 999px; padding: 12px 18px; font-weight: 700; background: #38bdf8; color: #082f49; cursor: pointer; }}
    pre {{ white-space: pre-wrap; background: #0f172a; padding: 16px; border-radius: 12px; }}
    .notice {{ margin-bottom: 20px; padding: 12px 16px; border-radius: 12px; }}
    .error {{ background: #7f1d1d; color: #fee2e2; }}
    .hint {{ color: #94a3b8; }}
    .grid {{ display: grid; gap: 24px; }}
    .result audio {{ width: 100%; margin: 16px 0; }}
  </style>
</head>
<body>
  <main>
    <div class="panel">
      <h1>Voice Over AI Lokal Llama</h1>
      <p>Bisa dipakai dalam 2 mode: <strong>teks via CLI</strong> dan <strong>web via browser</strong>. Teks user akan dirapikan dulu oleh Llama lokal, lalu diubah menjadi suara dengan karakter yang dipilih.</p>
      <div class="grid">
        <section>
          <h2>Mode Web</h2>
          <form method="post" action="/generate">
            <label for="character">Karakter suara</label>
            <input id="character" name="character" value="{character_value}" placeholder="contoh: Narator hangat dan natural">

            <label for="text">Teks</label>
            <textarea id="text" name="text" placeholder="Masukkan naskah voice over di sini">{text_value}</textarea>

            <button type="submit">Buat Voice Over</button>
          </form>
        </section>
        <section>
          <h2>Mode Teks / CLI</h2>
          <pre>python3 local_llama_voiceover.py --mode text --text "Halo, selamat datang" --character "Narator hangat"</pre>
          <p class="hint">Untuk mode web jalankan: <code>python3 local_llama_voiceover.py --mode web</code></p>
        </section>
      </div>
      {result_html}
    </div>
  </main>
</body>
</html>"""


class VoiceoverRequestHandler(BaseHTTPRequestHandler):
    service = VoiceoverService()

    def _send_html(self, page: str, status: HTTPStatus = HTTPStatus.OK) -> None:
        body = page.encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:  # noqa: N802
        if self.path == "/":
            self._send_html(render_page())
            return

        if self.path.startswith("/audio/"):
            audio_name = urllib.parse.unquote(self.path.replace("/audio/", "", 1))
            try:
                audio_path = self.service.safe_audio_path(audio_name)
            except FileNotFoundError:
                self.send_error(HTTPStatus.NOT_FOUND, "Audio tidak ditemukan.")
                return

            mime_type = mimetypes.guess_type(audio_path.name)[0] or "application/octet-stream"
            payload = audio_path.read_bytes()
            self.send_response(HTTPStatus.OK)
            self.send_header("Content-Type", mime_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return

        self.send_error(HTTPStatus.NOT_FOUND, "Halaman tidak ditemukan.")

    def do_POST(self) -> None:  # noqa: N802
        if self.path != "/generate":
            self.send_error(HTTPStatus.NOT_FOUND, "Route tidak ditemukan.")
            return

        content_length = int(self.headers.get("Content-Length", "0"))
        raw_body = self.rfile.read(content_length).decode("utf-8")
        form = urllib.parse.parse_qs(raw_body)
        text = form.get("text", [""])[0]
        character = form.get("character", ["Narator hangat dan natural"])[0]

        try:
            result = self.service.generate(text, character)
            page = render_page(result=result, defaults={"text": text, "character": character})
            self._send_html(page)
        except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
            page = render_page(
                error=str(exc),
                defaults={"text": text, "character": character},
            )
            self._send_html(page, status=HTTPStatus.BAD_REQUEST)


def run_web_server(host: str, port: int) -> None:
    server = ThreadingHTTPServer((host, port), VoiceoverRequestHandler)
    print(f"Web mode berjalan di http://{host}:{port}")
    print("Tekan Ctrl+C untuk menghentikan server.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer dihentikan.")
    finally:
        server.server_close()


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local Llama voice over app.")
    parser.add_argument("--mode", choices=("text", "web"), default="web")
    parser.add_argument("--text", help="Teks yang akan dibacakan.")
    parser.add_argument(
        "--character",
        default="Narator hangat dan natural",
        help="Karakter suara yang diinginkan.",
    )
    parser.add_argument("--output", help="Lokasi file audio hasil voice over.")
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8000, type=int)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    service = VoiceoverService()

    if args.mode == "web":
        run_web_server(args.host, args.port)
        return 0

    if not args.text:
        print("--text wajib diisi saat menggunakan --mode text.", file=sys.stderr)
        return 1

    output_path = Path(args.output).resolve() if args.output else None
    try:
        result = service.generate(args.text, args.character, output_path=output_path)
    except (RuntimeError, ValueError, subprocess.CalledProcessError) as exc:
        print(str(exc), file=sys.stderr)
        return 1

    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
