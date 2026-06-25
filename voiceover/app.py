"""
AI Voice Over — FastAPI Web Application (Web Mode)
===================================================
Start the server:
    uvicorn app:app --reload --port 8000

Then open http://localhost:8000 in your browser.
"""

import io
import logging
from typing import Annotated, Optional

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from core.llm import CHARACTER_PROMPTS, generate_narration, list_local_models
from core.tts import list_edge_tts_voices, synthesize

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="AI Voice Over", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# ---------------------------------------------------------------------------
# Request / Response models
# ---------------------------------------------------------------------------


class VoiceRequest(BaseModel):
    text: str
    model: str = "llama3"
    character: str = "friendly"
    tts_engine: str = "edge_tts"
    voice: str = "en-US-JennyNeural"
    use_llm: bool = True


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    """Serve the main web UI."""
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"characters": list(CHARACTER_PROMPTS.keys())},
    )


@app.post("/api/generate")
async def generate_voice(req: VoiceRequest):
    """
    Process text through the local LLM (optional) and synthesize speech.

    Returns the audio stream with:
      - Content-Type: audio/mpeg  (edge_tts)
      - Content-Type: audio/wav   (pyttsx3)
      - Header X-Processed-Text:  first 300 chars of the narration text
    """
    if not req.text.strip():
        raise HTTPException(status_code=400, detail="Text must not be empty.")

    # 1. LLM processing
    narration_text = req.text
    if req.use_llm:
        try:
            narration_text = generate_narration(
                req.text,
                model=req.model,
                character=req.character,
            )
            logger.info("LLM narration generated (%d chars)", len(narration_text))
        except Exception as exc:
            logger.warning("LLM failed, using raw text: %s", exc)
            narration_text = req.text

    # 2. TTS synthesis
    try:
        audio_bytes, mime_type = synthesize(
            narration_text,
            engine=req.tts_engine,
            voice=req.voice,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"TTS failed: {exc}") from exc

    return StreamingResponse(
        io.BytesIO(audio_bytes),
        media_type=mime_type,
        headers={
            "X-Processed-Text": narration_text[:300],
            "Content-Disposition": "inline; filename=voiceover.audio",
        },
    )


@app.get("/api/voices")
async def get_voices():
    """List available Edge TTS voices."""
    try:
        voices = list_edge_tts_voices()
        return {"voices": voices}
    except Exception as exc:
        logger.warning("Failed to list Edge TTS voices: %s", exc)
        return {"voices": [], "error": "Could not retrieve voice list."}


@app.get("/api/models")
async def get_models():
    """List locally available Ollama models."""
    models = list_local_models()
    return {"models": models if models else ["llama3"]}


@app.get("/api/characters")
async def get_characters():
    """List available AI character personalities."""
    return {
        "characters": [
            {"id": k, "description": v[:80] + "…"}
            for k, v in CHARACTER_PROMPTS.items()
        ]
    }
