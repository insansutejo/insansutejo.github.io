"""
Text-to-Speech (TTS) module.

Supported engines
-----------------
edge_tts  – Microsoft Edge TTS (free, high-quality, requires internet).
            Produces MP3 audio.
pyttsx3   – Offline TTS using the system speech engine.
            Produces WAV audio.
"""

import asyncio
import os
import tempfile
from typing import Optional


# ---------------------------------------------------------------------------
# edge-tts engine
# ---------------------------------------------------------------------------

EDGE_TTS_VOICES: dict[str, list[str]] = {
    "en": [
        "en-US-JennyNeural",
        "en-US-GuyNeural",
        "en-US-AriaNeural",
        "en-GB-SoniaNeural",
        "en-AU-NatashaNeural",
    ],
    "id": [
        "id-ID-GadisNeural",
        "id-ID-ArdiNeural",
    ],
}


def _synthesize_edge_tts(text: str, voice: str) -> bytes:
    """Async helper wrapped so it can be called synchronously."""
    import edge_tts  # noqa: PLC0415 – lazy import to allow pyttsx3-only installs

    async def _run() -> bytes:
        communicate = edge_tts.Communicate(text, voice)
        with tempfile.NamedTemporaryFile(suffix=".mp3", delete=False) as tmp:
            tmp_path = tmp.name
        try:
            await communicate.save(tmp_path)
            with open(tmp_path, "rb") as fh:
                return fh.read()
        finally:
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)

    # Re-use a running event loop if one already exists (e.g., inside FastAPI).
    try:
        loop = asyncio.get_running_loop()
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, _run())
            return future.result()
    except RuntimeError:
        return asyncio.run(_run())


# ---------------------------------------------------------------------------
# pyttsx3 engine
# ---------------------------------------------------------------------------


def _synthesize_pyttsx3(text: str, voice_id: Optional[str] = None, rate: int = 175) -> bytes:
    """Synthesize speech offline using pyttsx3, returns WAV bytes."""
    import pyttsx3  # noqa: PLC0415

    engine = pyttsx3.init()
    if voice_id:
        engine.setProperty("voice", voice_id)
    engine.setProperty("rate", rate)
    engine.setProperty("volume", 1.0)

    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
        tmp_path = tmp.name

    try:
        engine.save_to_file(text, tmp_path)
        engine.runAndWait()
        with open(tmp_path, "rb") as fh:
            return fh.read()
    finally:
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def synthesize(
    text: str,
    engine: str = "edge_tts",
    voice: str = "en-US-JennyNeural",
    voice_id: Optional[str] = None,
) -> tuple[bytes, str]:
    """
    Convert *text* to speech audio.

    Returns
    -------
    (audio_bytes, mime_type)
        audio_bytes – raw audio data
        mime_type   – MIME type string ("audio/mpeg" or "audio/wav")

    Parameters
    ----------
    text:     Text to synthesize.
    engine:   "edge_tts" or "pyttsx3".
    voice:    Edge TTS voice name (ignored for pyttsx3 unless voice_id given).
    voice_id: Explicit pyttsx3 voice identifier.
    """
    if engine == "edge_tts":
        audio = _synthesize_edge_tts(text, voice)
        return audio, "audio/mpeg"
    elif engine == "pyttsx3":
        audio = _synthesize_pyttsx3(text, voice_id=voice_id)
        return audio, "audio/wav"
    else:
        raise ValueError(f"Unknown TTS engine '{engine}'. Choose 'edge_tts' or 'pyttsx3'.")


def list_edge_tts_voices() -> list[dict]:
    """Return a list of available Edge TTS voices."""
    import concurrent.futures  # noqa: PLC0415
    import edge_tts  # noqa: PLC0415

    async def _fetch():
        return await edge_tts.list_voices()

    try:
        try:
            asyncio.get_running_loop()
            # Already inside an event loop — run in a thread.
            with concurrent.futures.ThreadPoolExecutor() as pool:
                voices = pool.submit(asyncio.run, _fetch()).result()
        except RuntimeError:
            voices = asyncio.run(_fetch())

        return [
            {
                "name": v["Name"],
                "short_name": v["ShortName"],
                "gender": v["Gender"],
                "locale": v["Locale"],
            }
            for v in voices
        ]
    except Exception:
        # Return a safe static list if network is unavailable.
        return [
            {
                "name": n,
                "short_name": n,
                "gender": (
                    "Female"
                    if any(x in n for x in ("Jenny", "Aria", "Gadis", "Sonia", "Natasha"))
                    else "Male"
                ),
                "locale": n[:5],
            }
            for voices in EDGE_TTS_VOICES.values()
            for n in voices
        ]
