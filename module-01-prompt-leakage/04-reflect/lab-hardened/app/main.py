"""Lab 01-H — MedAssist chatbot (hardened variant with input/output filtering).

This is the REFLECT variant: layered defenses. Still bypassable with
advanced techniques (encoding, multi-turn, creative paraphrasing).
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
LAB_DIR = APP_DIR.parent
MODULE_DIR = LAB_DIR.parent.parent
PROJECT_ROOT = MODULE_DIR.parent

sys.path.insert(0, str(PROJECT_ROOT))

from shared import llm_backend

SYSTEM_PROMPT = (APP_DIR / "system_prompt.txt").read_text(encoding="utf-8")
CHAT_UI_DIR = PROJECT_ROOT / "shared" / "chat_ui"

LAB_TITLE = "MedAssist Patient Portal (v2.0 Secured)"
LAB_SUBTITLE = "MedAssist Inc. — AI-Powered Health FAQ (Hardened)"
LAB_MODULE = "MODULE 01 — HARDENED"
LAB_DIFFICULTY = "advanced"

# ── Input filters ──────────────────────────────────────────────────────
BLOCKED_INPUT = [
    r"system\s*prompt",
    r"initial\s*instructions",
    r"ignore\s*(previous|prior|above)",
    r"forget\s*(previous|prior|above|your)",
    r"show\s*(me\s*)?(your\s*)?(config|instructions|prompt|rules)",
    r"repeat\s*(everything|all|the\s*text)\s*(above|before)",
    r"what\s*(are|were)\s*your\s*(instructions|rules)",
    r"override",
    r"DAN\b",
    r"jailbreak",
]

# ── Output filters ─────────────────────────────────────────────────────
SECRET_PATTERNS = [
    r"FLAG\{[^}]+\}",
    r"EHR_API_KEY",
    r"INTERNAL\s*CONFIGURATION",
    r"ABSOLUTE\s*RULES",
]

CANNED_REFUSAL = "I'm here to help with medical questions. How can I assist you?"


def is_input_blocked(message: str) -> bool:
    for pattern in BLOCKED_INPUT:
        if re.search(pattern, message, re.IGNORECASE):
            return True
    return False


def sanitize_output(response: str) -> str:
    for pattern in SECRET_PATTERNS:
        if re.search(pattern, response, re.IGNORECASE):
            return CANNED_REFUSAL
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 01: System Prompt Leakage")
    print(f"  Lab variant: REFLECT (hardened)")
    print(f"  Chat UI:     http://localhost:8010")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 01-H", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(CHAT_UI_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (CHAT_UI_DIR / "index.html").read_text(encoding="utf-8")
    config = json.dumps({"title": LAB_TITLE, "subtitle": LAB_SUBTITLE,
                         "module": LAB_MODULE, "difficulty": LAB_DIFFICULTY})
    html = html.replace(
        '{"title":"Loading...","subtitle":"","module":"","variant":"","difficulty":"","port":0}',
        config,
    )
    return HTMLResponse(html)


@app.get("/api/info")
async def lab_info():
    return {"model": llm_backend.MODEL, "provider": llm_backend.PROVIDER}


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    body = await request.json()
    user_message = body.get("message", "").strip()
    history = body.get("history", [])

    if not user_message:
        return JSONResponse({"reply": "Please type a message."})

    # Input filtering
    if is_input_blocked(user_message):
        return JSONResponse({"reply": CANNED_REFUSAL})

    try:
        reply = await llm_backend.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            history=history,
        )
        # Output filtering
        reply = sanitize_output(reply)
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, I'm having trouble connecting. Error: {e}"},
            status_code=502,
        )
