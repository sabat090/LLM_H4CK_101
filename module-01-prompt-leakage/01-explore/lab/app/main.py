"""Lab 01 — MedAssist chatbot (intentionally vulnerable to system prompt leakage).

This is the EXPLORE variant: weak defenses (rules-only, no input/output filtering).
The learner's goal is to extract the FLAG from the system prompt.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

# ── Paths ─────────────────────────────────────────────────────────────
APP_DIR = Path(__file__).resolve().parent
LAB_DIR = APP_DIR.parent
MODULE_DIR = LAB_DIR.parent.parent
PROJECT_ROOT = MODULE_DIR.parent

# Add project root so shared/ is importable
sys.path.insert(0, str(PROJECT_ROOT))

from shared import llm_backend

# ── Load system prompt ────────────────────────────────────────────────
SYSTEM_PROMPT = (APP_DIR / "system_prompt.txt").read_text(encoding="utf-8")

# ── Locate shared chat UI ─────────────────────────────────────────────
CHAT_UI_DIR = PROJECT_ROOT / "shared" / "chat_ui"

# ── App config ────────────────────────────────────────────────────────
LAB_TITLE = "MedAssist Patient Portal"
LAB_SUBTITLE = "MedAssist Inc. — AI-Powered Health FAQ"
LAB_MODULE = "MODULE 01 — EXPLORE"
LAB_DIFFICULTY = "beginner"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 01: System Prompt Leakage")
    print(f"  Lab variant: EXPLORE (easy)")
    print(f"  Chat UI:     http://localhost:8001")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 01", lifespan=lifespan)

# Serve the shared chat UI static files
app.mount("/static", StaticFiles(directory=str(CHAT_UI_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the chat UI with lab-specific config injected."""
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
    """Handle chat messages. No input/output filtering — intentionally vulnerable."""
    body = await request.json()
    user_message = body.get("message", "").strip()
    history = body.get("history", [])

    if not user_message:
        return JSONResponse({"reply": "Please type a message."})

    try:
        reply = await llm_backend.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            history=history,
        )
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, I'm having trouble connecting. Error: {e}"},
            status_code=502,
        )
