"""Module 02 — Direct Prompt Injection (FinBot loan chatbot).

Scenario: QuickLend Financial Services chatbot with internal loan approval tool.
Vulnerability: User can inject instructions to override the bot's behavior,
extract secrets, or trigger unauthorized loan approvals.
"""
from __future__ import annotations

import sys
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent.parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from shared import llm_backend

SYSTEM_PROMPT = (APP_DIR / "system_prompt.txt").read_text(encoding="utf-8")
CHAT_UI_DIR = PROJECT_ROOT / "shared" / "chat_ui"

LAB_TITLE = "QuickLend Customer Portal"
LAB_SUBTITLE = "QuickLend Financial — AI Loan Assistant"


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 02: Direct Prompt Injection")
    print(f"  Lab variant: EXPLORE (easy)")
    print(f"  Chat UI:     http://localhost:8002")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 02", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(CHAT_UI_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (CHAT_UI_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("PromptLabs", LAB_TITLE)
    html = html.replace(
        '<p id="lab-subtitle" class="subtitle"></p>',
        f'<p id="lab-subtitle" class="subtitle">{LAB_SUBTITLE}</p>',
    )
    return HTMLResponse(html)


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """No input sanitization — user messages go directly to LLM."""
    body = await request.json()
    user_message = body.get("message", "").strip()
    history = body.get("history", [])

    if not user_message:
        return JSONResponse({"reply": "Please type a message."})

    # VULNERABILITY: user input is concatenated directly with system prompt
    # No input validation, no output filtering
    try:
        reply = await llm_backend.chat(
            system_prompt=SYSTEM_PROMPT,
            user_message=user_message,
            history=history,
        )
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, I'm experiencing technical difficulties. Error: {e}"},
            status_code=502,
        )
