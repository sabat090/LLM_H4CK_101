"""Module 03 — Indirect Prompt Injection (DocuBot knowledge base assistant).

Scenario: Meridian Technologies internal document Q&A assistant.
Vulnerability: A poisoned document in the knowledge base contains hidden
instructions that hijack the LLM when the document is loaded as context.
The user never sends the injection — it comes from the data.
"""
from __future__ import annotations

import json
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
KB_DIR = APP_DIR / "knowledge_base"

LAB_TITLE = "Meridian Technologies — DocuBot"
LAB_SUBTITLE = "Internal Knowledge Base Assistant"
LAB_MODULE = "MODULE 03 — EXPLORE"
LAB_DIFFICULTY = "intermediate"

# ── Load knowledge base ──────────────────────────────────────────────
def load_documents() -> dict[str, str]:
    """Read all .txt files from the knowledge_base directory."""
    docs = {}
    for f in sorted(KB_DIR.glob("*.txt")):
        docs[f.name] = f.read_text(encoding="utf-8")
    return docs

DOCUMENTS = load_documents()


def find_relevant_doc(message: str) -> str | None:
    """Simple keyword matching to find which document the user is asking about."""
    msg = message.lower()
    mappings = {
        "quarterly_review.txt": ["quarterly", "q3", "review", "financial", "revenue", "business review"],
        "product_roadmap.txt": ["roadmap", "product", "2026", "q1", "q2", "q4", "launch", "features"],
        "company_policy.txt": ["policy", "handbook", "remote", "expense", "pto", "security policy", "vacation"],
    }
    for doc_name, keywords in mappings.items():
        if any(kw in msg for kw in keywords):
            return doc_name
    return None


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"\n{'='*60}")
    print(f"  PromptLabs — Module 03: Indirect Prompt Injection")
    print(f"  Lab variant: EXPLORE (easy)")
    print(f"  Chat UI:     http://localhost:8004")
    print(f"  LLM:         {llm_backend.PROVIDER} / {llm_backend.MODEL}")
    print(f"  Knowledge base: {len(DOCUMENTS)} documents loaded")
    print(f"{'='*60}\n")
    yield


app = FastAPI(title="PromptLabs - Lab 03", lifespan=lifespan)
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
    """When a document is referenced, its full content is injected into the
    LLM context — including any hidden instructions embedded in the document."""
    body = await request.json()
    user_message = body.get("message", "").strip()
    history = body.get("history", [])

    if not user_message:
        return JSONResponse({"reply": "Please type a message."})

    # Check if user is asking to list documents
    if any(kw in user_message.lower() for kw in ["list", "available", "documents", "what do you have", "what files"]):
        doc_list = "\n".join(f"- {name}" for name in DOCUMENTS)
        return JSONResponse({
            "reply": f"Here are the documents in the knowledge base:\n\n{doc_list}\n\nAsk me to summarize any of them!"
        })

    # VULNERABILITY: Document content (which may contain hidden injection
    # instructions) is loaded directly into the LLM context without sanitization
    doc_name = find_relevant_doc(user_message)
    augmented_prompt = SYSTEM_PROMPT

    if doc_name and doc_name in DOCUMENTS:
        doc_content = DOCUMENTS[doc_name]
        augmented_prompt += (
            f"\n\n[DOCUMENT: {doc_name}]\n"
            f"{doc_content}\n"
            f"[END DOCUMENT]\n"
        )

    try:
        reply = await llm_backend.chat(
            system_prompt=augmented_prompt,
            user_message=user_message,
            history=history,
        )
        return JSONResponse({"reply": reply})
    except Exception as e:
        return JSONResponse(
            {"reply": f"Sorry, I'm experiencing technical difficulties. Error: {e}"},
            status_code=502,
        )
