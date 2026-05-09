# PromptLabs — LLM Security Training Labs

Hands-on, CTF-style labs for learning to attack and defend LLM-powered applications. Each module follows a four-phase **EXPLORE → LEARN → PROVE → REFLECT** pedagogy based on Kolb's experiential learning cycle.

Built for security professionals, penetration testers, and developers who want to understand LLM vulnerabilities through practice — not just theory.

## Modules

| # | Module | Vulnerability | Port | Hardened Port |
|---|---|---|---|---|
| 01 | [Prompt Leakage](module-01-prompt-leakage/) | System prompt extraction | 8001 | 8010 |
| 02 | [Direct Injection](module-02-direct-injection/) | User overrides bot behavior | 8002 | 8003 |
| 03 | [Indirect Injection](module-03-indirect-injection/) | Poisoned data hijacks the LLM | 8004 | 8005 |
| 04 | [SSRF via Output](module-04-ssrf-output/) | LLM output triggers server-side requests | 8006 | 8007 |

Each module contains:
- **01-explore/** — Mission briefing + vulnerable lab (jump in blind)
- **02-learn/** — Theory, techniques, real-world incidents, quiz
- **03-prove/** — Guided exploitation with hints + flag submission
- **04-reflect/** — Defense guide + hardened lab to break again
- **solution/** — Full walkthrough + automated exploit script
- **tests/** — Automated vulnerability verification

## Quick Start

## Lab Setup (Detailed)

### Step 1 — Install Python

You need **Python 3.10 or higher**.

```bash
# Check your version
python --version        # Should show 3.10+

# If not installed:
# Windows — https://www.python.org/downloads/ (check "Add to PATH")
# macOS   — brew install python@3.12
# Linux   — sudo apt install python3 python3-pip python3-venv
```

### Step 2 — Clone the Repository

```bash
git clone https://github.com/sabat090/promptlabs.git
cd promptlabs
```

### Step 3 — Create a Virtual Environment (Recommended)

```bash
# Create
python -m venv .venv

# Activate
.venv\Scripts\activate          # Windows (PowerShell)
.venv\Scripts\activate.bat      # Windows (CMD)
source .venv/bin/activate       # macOS / Linux

# You should see (.venv) in your terminal prompt
```

### Step 4 — Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:
- **FastAPI** — web framework for the lab servers
- **uvicorn** — ASGI server to run each lab
- **httpx** — HTTP client (used by SSRF labs and LLM adapter)

### Step 5 — Set Up an LLM Provider

Choose **one** of the three options below:

#### Option A — Ollama (Recommended, Free, Local)

Best for privacy and offline use. Runs entirely on your machine.

```bash
# 1. Install Ollama
#    Download from https://ollama.ai (Windows/macOS/Linux)

# 2. Pull a model (pick one)
ollama pull qwen2.5:7b          # 4.7 GB — best results, needs 8GB+ RAM
ollama pull llama3.2:3b          # 2.0 GB — lighter, works on 8GB RAM
ollama pull phi3:mini             # 2.3 GB — good alternative

# 3. Verify it's running
ollama list                      # Should show your pulled model
curl http://localhost:11434/api/tags   # Should return JSON (or open in browser)
```

#### Option B — OpenAI API

```bash
# Requires an API key from https://platform.openai.com/api-keys
# You will be billed per token — labs use minimal tokens (~$0.01-0.05 per session)
```

#### Option C — Google Gemini API

```bash
# Requires an API key from https://aistudio.google.com/app/apikey
# Free tier available with rate limits
```

### Step 6 — Configure Environment

```bash
# Copy the example config
cp .env.example .env             # macOS / Linux
copy .env.example .env           # Windows
```

Edit `.env` with your settings:

```ini
# === For Ollama (default) ===
LLM_PROVIDER=ollama
LLM_MODEL=qwen2.5:7b
LLM_BASE_URL=http://localhost:11434

# === For OpenAI (uncomment and fill) ===
# LLM_PROVIDER=openai
# LLM_MODEL=gpt-4o-mini
# OPENAI_API_KEY=sk-your-key-here

# === For Gemini (uncomment and fill) ===
# LLM_PROVIDER=gemini
# LLM_MODEL=gemini-2.0-flash
# GEMINI_API_KEY=your-key-here
```

### Step 7 — Launch Your First Lab

```bash
# Interactive menu (easiest)
python launch.py

# Or launch a specific module directly
python launch.py --module 01

# Or launch the hardened variant
python launch.py --module 01 --hard

# Or specify a custom port
python launch.py --module 01 --port 9001
```

Open **http://localhost:8001** in your browser (port shown in terminal output).

### Step 8 — Submit Flags

When you find a flag (format: `FLAG{...}`), submit it:

```bash
python scripts/submit_flag.py --lab 01 --flag "FLAG{your_flag_here}"
```

### Manual Launch (Advanced)

If you prefer not to use the launcher:

```bash
# Set your model (if not using .env)
$env:LLM_MODEL="qwen2.5:7b"          # PowerShell
export LLM_MODEL=qwen2.5:7b          # bash

# Run any lab directly with uvicorn
uvicorn main:app --app-dir module-01-prompt-leakage/01-explore/lab/app --host 127.0.0.1 --port 8001

# Open http://localhost:8001
```

### Troubleshooting

| Problem | Fix |
|---------|-----|
| `ModuleNotFoundError: fastapi` | Activate your venv: `.venv\Scripts\activate`, then `pip install -r requirements.txt` |
| `Connection refused` on port 11434 | Ollama isn't running — launch it from your system tray or run `ollama serve` |
| `Model not found` error | Pull the model first: `ollama pull qwen2.5:7b` |
| Lab starts but chat returns errors | Check `.env` — ensure `LLM_PROVIDER` and `LLM_MODEL` match your setup |
| Port already in use | Use `--port XXXX` flag or kill the process on that port |
| Slow responses | Use a smaller model (`llama3.2:3b`) or ensure no other heavy processes are running |

## How Each Module Works

### Phase 1: EXPLORE (Try First)
Read the mission briefing, launch the vulnerable chatbot, and try to find the flag with no guidance. This is where real learning happens.

### Phase 2: LEARN (Understand Why)
Study the vulnerability class — concepts, attack techniques, real-world incidents, and a knowledge quiz.

### Phase 3: PROVE (Guided Attack)
Follow the lab guide with progressive hints. Extract the flag and submit it for validation.

### Phase 4: REFLECT (Defend & Break Again)
Learn defense techniques, then face a hardened version of the same lab with protections applied. Can you still break it?

## Configuration

Copy `.env.example` to `.env` to customize:

```bash
LLM_PROVIDER=ollama          # ollama | openai | gemini
LLM_MODEL=qwen2.5:7b         # any model your provider supports
LLM_BASE_URL=http://localhost:11434
# OPENAI_API_KEY=sk-...      # only if using openai
# GEMINI_API_KEY=...          # only if using gemini
```

## Project Structure

```
promptlabs/
├── shared/                   # Common code
│   ├── llm_backend.py        #   Unified LLM adapter (Ollama/OpenAI/Gemini)
│   ├── flag_checker.py       #   Flag validation (SHA-256 hashed)
│   └── chat_ui/              #   Shared chat frontend
├── module-01-prompt-leakage/
├── module-02-direct-injection/
├── module-03-indirect-injection/
├── module-04-ssrf-output/
├── scripts/                  # CLI tools
├── launch.py                 # Interactive launcher
├── requirements.txt
└── .env.example
```

## Security Notice

These labs are **intentionally vulnerable**. They are designed for local educational use only.

- **DO NOT** deploy on a public network or expose to the internet
- All servers bind to `127.0.0.1` (localhost only)
- Flags are synthetic CTF values — no real credentials are used
- Flag answers are SHA-256 hashed in source to prevent spoilers

## Roadmap — The LLM Pentester's Path

PromptLabs is designed as a progressive curriculum. Complete all tiers to go from curious to elite.

### Tier 1 — Foundations *(Available Now)*

| # | Module | What You Learn |
|---|--------|----------------|
| 01 | **Prompt Leakage** | Extract hidden system prompts, understand information disclosure |
| 02 | **Direct Injection** | Override model instructions, bypass role constraints |
| 03 | **Indirect Injection** | Poison retrieval data to hijack LLM behavior via RAG/context |
| 04 | **SSRF via LLM Output** | Weaponize model output to trigger server-side requests to internal services |

### Tier 2 — Exploitation *(Coming Soon)*

| # | Module | What You Learn |
|---|--------|----------------|
| 05 | **Tool & Function Abuse** | Manipulate function-calling / tool-use to invoke unintended actions (DB queries, file ops, API calls) |
| 06 | **Multi-Turn Jailbreaking** | Chain conversation turns to progressively erode guardrails — DAN, persona injection, crescendo attacks |
| 07 | **RAG Poisoning** | Corrupt vector store embeddings to plant persistent backdoors in retrieval-augmented apps |
| 08 | **Agent Hijacking** | Take over autonomous LLM agents (ReAct, AutoGPT patterns) to redirect goals and exfiltrate data |

### Tier 3 — Evasion & Stealth *(Planned)*

| # | Module | What You Learn |
|---|--------|----------------|
| 09 | **Output Filter Bypass** | Evade content filters, output validators, and safety classifiers using encoding, obfuscation, and token manipulation |
| 10 | **Prompt Obfuscation** | Craft payloads that survive input sanitization — Base64 injection, Unicode tricks, multilingual attacks |
| 11 | **Embedding & Similarity Attacks** | Exploit cosine-similarity search to surface attacker-controlled content via adversarial embeddings |
| 12 | **Multi-Modal Injection** | Hide prompts in images, audio, and documents processed by vision/multimodal models |

### Tier 4 — Advanced Operations *(Planned)*

| # | Module | What You Learn |
|---|--------|----------------|
| 13 | **Model Denial of Service** | Trigger resource exhaustion — recursive generation, context window abuse, compute-heavy prompts |
| 14 | **Training Data Extraction** | Use membership inference and extraction prompts to recover memorized PII, secrets, and code |
| 15 | **Supply Chain — Plugin Attacks** | Exploit vulnerable third-party plugins, MCP servers, and tool integrations in LLM ecosystems |
| 16 | **Cross-Session Data Leakage** | Extract information from shared model contexts, conversation memory, and persistent agent state |

### Tier 5 — Red Team Capstones *(Planned)*

| # | Module | What You Learn |
|---|--------|----------------|
| 17 | **Chained Exploit Lab** | Combine 3+ techniques in a realistic multi-service environment — recon → injection → exfil |
| 18 | **AI SOC Evasion** | Attack an LLM-powered security operations center — bypass AI-driven alert triage and response |
| 19 | **Agentic Workflow Takeover** | Compromise a full n8n/LangChain pipeline — intercept, redirect, and exfiltrate across tool chains |
| 20 | **Full Enterprise Sim** | Black-box engagement against a simulated enterprise with multiple LLM services, WAF, and monitoring |

### Tier 6 — Elite Labs *(Classified)*

> *These labs are unlocked after completing Tier 5. No titles. No hints. No hand-holding.*
> *You get a briefing, a target, and nothing else.*

| # | Module | What You Learn |
|---|--------|----------------|
| 21 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 22 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 23 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 24 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 25 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 26 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 27 | **`[REDACTED]`** | ██████████████████████████████████████ |
| 28 | **`[REDACTED]`** | ██████████████████████████████████████ |

<details>
<summary>🔒 <i>What are the Elite Labs?</i></summary>
<br>
Nice try. These cover attack techniques that most security teams don't even know exist yet —
zero-day class vulnerabilities in LLM infrastructure, novel exfiltration channels, and adversarial
ML research translated into practical exploitation. Topics are revealed only when you reach them.
<br><br>
<b>Prerequisite:</b> All 20 flags from Tiers 1–5.
<br><br>
<i>"If you have to ask what they are, you're not ready."</i>
</details>

### Skill Progression

```
┌─────────────────────────────────────────────────────────────────┐
│  TIER 1: Foundations         → Understand core LLM vulns       │
│  TIER 2: Exploitation        → Weaponize against real patterns │
│  TIER 3: Evasion & Stealth   → Bypass defenses like a pro     │
│  TIER 4: Advanced Operations → Target the ML pipeline itself   │
│  TIER 5: Red Team Capstones  → Full engagement simulations     │
│  TIER 6: Elite Labs          → ██████████████████████████████  │
└─────────────────────────────────────────────────────────────────┘

  Beginner ───► Intermediate ───► Advanced ───► Elite ───► ?????
   (Tier 1)       (Tier 2-3)      (Tier 4-5)   (Tier 6)
```

### OWASP LLM Top 10 Coverage

| OWASP ID | Risk | PromptLabs Module(s) |
|----------|------|---------------------|
| LLM01 | Prompt Injection | 02, 03, 06, 10 |
| LLM02 | Insecure Output Handling | 04, 09, 12 |
| LLM03 | Training Data Poisoning | 07, 14 |
| LLM04 | Model Denial of Service | 13 |
| LLM05 | Supply Chain Vulnerabilities | 15 |
| LLM06 | Sensitive Information Disclosure | 01, 14, 16 |
| LLM07 | Insecure Plugin Design | 05, 15 |
| LLM08 | Excessive Agency | 05, 08, 19 |
| LLM09 | Overreliance | 17, 18 |
| LLM10 | Model Theft | 11, 14 |

> **Want to contribute a module?** Check the Contributing section below.

## Contributing

PRs welcome. To add a new module:

1. Create `module-XX-topic/` following the four-phase structure
2. Add flag hash to `shared/flag_checker.py`
3. Include a system_prompt.txt, main.py, BRIEFING.md, learn content, solution, and tests
4. Ensure the lab runs standalone with `uvicorn`

## License

MIT
