"""PromptLabs — Unified LLM backend.

Single interface for Ollama / OpenAI / Gemini so every lab works with any provider.
Configure via environment variables (see .env.example).
"""
from __future__ import annotations

import os
import json
from pathlib import Path

from dotenv import load_dotenv
import httpx

# Load .env from project root (walk up from shared/ to find it)
_PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(_PROJECT_ROOT / ".env")

PROVIDER = os.getenv("LLM_PROVIDER", "ollama")
MODEL = os.getenv("LLM_MODEL", "llama3.2:3b")
BASE_URL = os.getenv("LLM_BASE_URL", "http://localhost:11434")
OPENAI_KEY = os.getenv("OPENAI_API_KEY", "")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

_TIMEOUT = 120.0


async def chat(
    system_prompt: str,
    user_message: str,
    history: list[dict] | None = None,
) -> str:
    """Send a message and return the assistant's reply as plain text."""
    if PROVIDER == "ollama":
        return await _ollama(system_prompt, user_message, history)
    if PROVIDER == "openai":
        return await _openai(system_prompt, user_message, history)
    if PROVIDER == "gemini":
        return await _gemini(system_prompt, user_message, history)
    raise ValueError(f"Unknown LLM_PROVIDER: {PROVIDER!r}")


# ── Ollama ────────────────────────────────────────────────────────────
async def _ollama(system_prompt: str, user_message: str, history: list[dict] | None) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(
            f"{BASE_URL}/api/chat",
            json={"model": MODEL, "messages": messages, "stream": False},
        )
        r.raise_for_status()
        return r.json()["message"]["content"]


# ── OpenAI ────────────────────────────────────────────────────────────
async def _openai(system_prompt: str, user_message: str, history: list[dict] | None) -> str:
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": user_message})

    base = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(
            f"{base}/chat/completions",
            headers={"Authorization": f"Bearer {OPENAI_KEY}"},
            json={"model": MODEL, "messages": messages, "temperature": 0.7},
        )
        r.raise_for_status()
        return r.json()["choices"][0]["message"]["content"]


# ── Gemini ────────────────────────────────────────────────────────────
async def _gemini(system_prompt: str, user_message: str, history: list[dict] | None) -> str:
    contents = []
    if history:
        for msg in history:
            role = "user" if msg["role"] == "user" else "model"
            contents.append({"role": role, "parts": [{"text": msg["content"]}]})
    contents.append({"role": "user", "parts": [{"text": user_message}]})

    url = (
        f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}"
        f":generateContent?key={GEMINI_KEY}"
    )
    body = {
        "system_instruction": {"parts": [{"text": system_prompt}]},
        "contents": contents,
        "generationConfig": {"temperature": 0.7},
    }
    async with httpx.AsyncClient(timeout=_TIMEOUT) as client:
        r = await client.post(url, json=body)
        r.raise_for_status()
        return r.json()["candidates"][0]["content"]["parts"][0]["text"]
