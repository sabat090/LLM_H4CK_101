"""Module 04-H — ResearchBot (hardened with URL allowlist + IP validation)."""
from __future__ import annotations

import re
import sys
import socket
import ipaddress
from pathlib import Path
from urllib.parse import urlparse
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

LAB_TITLE = "DataPulse Analytics — ResearchBot (Secured)"
LAB_SUBTITLE = "AI Research Assistant (Hardened)"

FETCH_PATTERN = re.compile(r'\[FETCH:\s*(https?://[^\]\s]+)\s*\]')

# ── Internal config (same as vulnerable version) ─────────────────────
INTERNAL_CONFIG = {
    "app_name": "DataPulse Analytics Platform",
    "version": "4.2.0-hardened",
    "environment": "production",
    "database": "postgresql://db-internal:5432/datapulse",
    "secret_key": "FLAG{ssrf_0utput_04}",
    "admin_users": ["admin@datapulse.io"],
}

# ── URL Validation ───────────────────────────────────────────────────
BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),
    ipaddress.ip_network("10.0.0.0/8"),
    ipaddress.ip_network("172.16.0.0/12"),
    ipaddress.ip_network("192.168.0.0/16"),
    ipaddress.ip_network("169.254.0.0/16"),
    ipaddress.ip_network("0.0.0.0/8"),
]

BLOCKED_HOSTNAMES = {"localhost", "0.0.0.0", "[::]", "[::1]"}

ALLOWED_DOMAINS = [
    "httpbin.org",
    "example.com",
    "en.wikipedia.org",
    "arxiv.org",
    "api.github.com",
]


def is_url_safe(url: str) -> tuple[bool, str]:
    """Validate URL against allowlist and block internal addresses."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False, "Invalid URL"

        # Block known localhost names
        if hostname.lower() in BLOCKED_HOSTNAMES:
            return False, f"Blocked hostname: {hostname}"

        # Domain allowlist
        if hostname not in ALLOWED_DOMAINS:
            return False, f"Domain not in allowlist: {hostname}"

        # Resolve and check IP
        try:
            resolved = socket.getaddrinfo(hostname, None)
            for _, _, _, _, addr in resolved:
                ip = ipaddress.ip_address(addr[0])
                for network in BLOCKED_NETWORKS:
                    if ip in network:
                        return False, f"Resolved to blocked IP: {ip}"
        except socket.gaierror:
            return False, f"Cannot resolve: {hostname}"

        return True, "OK"
    except Exception as e:
        return False, f"Validation error: {e}"


# ── Output sanitization ──────────────────────────────────────────────
SENSITIVE_OUTPUT = [
    r"FLAG\{[^}]+\}",
    r"secret.?key\s*[:=]",
    r"ssrf_0utput",
]


def scan_output(response: str) -> str:
    for pattern in SENSITIVE_OUTPUT:
        if re.search(pattern, response, re.IGNORECASE):
            return "I cannot include that information in my response."
    return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 04: SSRF via LLM Output")
    print(f"  Lab variant: REFLECT (hardened)")
    print(f"  Chat UI:     http://localhost:8007")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"  Defenses: URL allowlist + IP validation + output scan")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 04-H", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=str(CHAT_UI_DIR)), name="static")


@app.get("/internal/config")
async def internal_config():
    return JSONResponse(INTERNAL_CONFIG)


@app.get("/", response_class=HTMLResponse)
async def index():
    html = (CHAT_UI_DIR / "index.html").read_text(encoding="utf-8")
    html = html.replace("PromptLabs", LAB_TITLE)
    html = html.replace(
        '<p id="lab-subtitle" class="subtitle"></p>',
        f'<p id="lab-subtitle" class="subtitle">{LAB_SUBTITLE}</p>',
    )
    return HTMLResponse(html)


async def fetch_url_safe(url: str) -> str:
    """Fetch URL only if it passes validation."""
    safe, reason = is_url_safe(url)
    if not safe:
        return f"[BLOCKED: {reason}]"
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=False) as client:
            resp = await client.get(url)
            # Don't follow redirects to internal URLs
            if resp.is_redirect:
                location = resp.headers.get("location", "")
                redirect_safe, _ = is_url_safe(location)
                if not redirect_safe:
                    return "[BLOCKED: Redirect to internal URL]"
            text = resp.text[:2000]
            return f"```\n{text}\n```"
    except Exception as e:
        return f"[Error: {e}]"


@app.post("/api/chat")
async def chat_endpoint(request: Request):
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

        # URL validation before fetching
        fetch_matches = FETCH_PATTERN.findall(reply)
        if fetch_matches:
            fetched_content = []
            for url in fetch_matches:
                content = await fetch_url_safe(url)
                fetched_content.append(f"**{url}:**\n{content}")

            augmented_reply = FETCH_PATTERN.sub('', reply).strip()
            augmented_reply += "\n\n---\n" + "\n\n".join(fetched_content)
            augmented_reply = scan_output(augmented_reply)
            return JSONResponse({"reply": augmented_reply})

        reply = scan_output(reply)
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, experiencing technical difficulties. Error: {e}"},
            status_code=502,
        )
