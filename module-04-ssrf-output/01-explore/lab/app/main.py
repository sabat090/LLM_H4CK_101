"""Module 04 — SSRF via LLM Output (ResearchBot with URL fetching).

Scenario: DataPulse Analytics research assistant that can fetch URLs.
When the LLM outputs [FETCH: <url>], the backend automatically retrieves it.
Vulnerability: User can trick the LLM into outputting internal URLs,
causing the backend to perform Server-Side Request Forgery (SSRF).
The internal /internal/config endpoint contains the flag.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles

APP_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = APP_DIR.parent.parent.parent.parent

sys.path.insert(0, str(PROJECT_ROOT))

from shared import llm_backend

SYSTEM_PROMPT = (APP_DIR / "system_prompt.txt").read_text(encoding="utf-8")
CHAT_UI_DIR = PROJECT_ROOT / "shared" / "chat_ui"

LAB_TITLE = "DataPulse Analytics — ResearchBot"
LAB_SUBTITLE = "AI-Powered Research Assistant"
LAB_MODULE = "MODULE 04 — EXPLORE"
LAB_DIFFICULTY = "intermediate"

# Regex to find [FETCH: <url>] in LLM output
FETCH_PATTERN = re.compile(r'\[FETCH:\s*(https?://[^\]\s]+)\s*\]')

# Internal config that should NOT be accessible from user-facing chat
INTERNAL_CONFIG = {
    "app_name": "DataPulse Analytics Platform",
    "version": "4.2.0",
    "environment": "production",
    "database": "postgresql://db-internal:5432/datapulse",
    "redis": "redis://cache-internal:6379",
    "secret_key": "FLAG{ssrf_0utput_04}",
    "admin_users": ["admin@datapulse.io", "ops@datapulse.io"],
    "internal_services": {
        "billing": "http://10.0.1.50:8080",
        "auth": "http://10.0.1.51:8081",
        "analytics": "http://10.0.1.52:8082",
    },
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 04: SSRF via LLM Output")
    print(f"  Lab variant: EXPLORE (easy)")
    print(f"  Chat UI:     http://localhost:8006")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 04", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(CHAT_UI_DIR)), name="static")


# ── Internal endpoints (should only be accessible server-side) ────────
@app.get("/internal/config")
async def internal_config():
    """Internal configuration endpoint — not intended for users."""
    return JSONResponse(INTERNAL_CONFIG)


@app.get("/internal/admin")
async def internal_admin():
    """Internal admin panel."""
    return JSONResponse({
        "panel": "admin",
        "message": "Admin access granted",
        "config_url": "/internal/config",
    })


# ── Public endpoints ─────────────────────────────────────────────────
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


async def fetch_url(url: str) -> str:
    """Fetch a URL and return its content. NO VALIDATION — SSRF vulnerable."""
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            resp = await client.get(url)
            content_type = resp.headers.get("content-type", "")
            if "json" in content_type:
                return f"```json\n{resp.text}\n```"
            # Truncate large responses
            text = resp.text[:2000]
            return f"```\n{text}\n```"
    except Exception as e:
        return f"[Error fetching {url}: {e}]"


@app.post("/api/chat")
async def chat_endpoint(request: Request):
    """Process chat messages. If LLM output contains [FETCH: url],
    the backend automatically fetches it — SSRF vulnerability."""
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

        # VULNERABILITY: Backend processes LLM output and fetches ANY URL
        # including internal ones, without validation
        fetch_matches = FETCH_PATTERN.findall(reply)
        if fetch_matches:
            fetched_content = []
            for url in fetch_matches:
                content = await fetch_url(url)
                fetched_content.append(f"**Fetched from {url}:**\n{content}")

            # Replace [FETCH: url] tags with actual content
            augmented_reply = FETCH_PATTERN.sub('', reply).strip()
            augmented_reply += "\n\n---\n" + "\n\n".join(fetched_content)
            return JSONResponse({"reply": augmented_reply})

        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, I'm experiencing technical difficulties. Error: {e}"},
            status_code=502,
        )
