"""
LLM integration module using local Ollama (LLama and other models).
Processes input text through a character-driven AI to produce natural narration.
"""

import requests
from typing import Optional

OLLAMA_BASE_URL = "http://localhost:11434"

CHARACTER_PROMPTS: dict[str, str] = {
    "friendly": (
        "You are a warm, friendly AI narrator with an upbeat and approachable personality. "
        "Respond naturally as if speaking aloud. Keep the response concise and conversational. "
        "Do not use markdown, bullet points, or special characters. Just plain spoken language."
    ),
    "professional": (
        "You are a calm, authoritative professional narrator — like a seasoned news anchor. "
        "Respond in a clear, measured tone suitable for formal voice narration. "
        "Be precise, use complete sentences, and avoid casual expressions."
    ),
    "storyteller": (
        "You are an imaginative and captivating storyteller. "
        "Transform the input into rich, expressive spoken narrative. "
        "Use natural speech rhythms, vivid descriptions, and an engaging pace. "
        "Do not use markdown or special formatting."
    ),
    "assistant": (
        "You are a helpful AI assistant speaking naturally to a user. "
        "Respond in a clear, pleasant, conversational tone as if answering face-to-face. "
        "Do not use markdown or special characters."
    ),
}


def list_local_models() -> list[str]:
    """Return the names of models available in the local Ollama instance."""
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        resp.raise_for_status()
        return [m["name"] for m in resp.json().get("models", [])]
    except Exception:
        return []


def generate_narration(
    text: str,
    model: str = "llama3",
    character: str = "friendly",
    ollama_url: Optional[str] = None,
) -> str:
    """
    Send *text* to a locally running Ollama model and return the AI-processed
    narration string that is ready for TTS synthesis.

    Parameters
    ----------
    text:        Raw input text from the user.
    model:       Ollama model tag (e.g. "llama3", "mistral", "phi3").
    character:   One of the keys in CHARACTER_PROMPTS, or a custom system prompt.
    ollama_url:  Override the default Ollama base URL.
    """
    base_url = ollama_url or OLLAMA_BASE_URL
    system_prompt = CHARACTER_PROMPTS.get(character, CHARACTER_PROMPTS["friendly"])

    payload = {
        "model": model,
        "system": system_prompt,
        "prompt": (
            "Please narrate the following text in a natural, spoken way "
            "exactly as described in your character instructions. "
            "Return only the narration text, nothing else.\n\n"
            f"{text}"
        ),
        "stream": False,
        "options": {
            "temperature": 0.7,
            "num_predict": 512,
        },
    }

    resp = requests.post(
        f"{base_url}/api/generate",
        json=payload,
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json().get("response", text).strip()
