# 🕵️ Mission Briefing — Module 04: SSRF via LLM Output

## Scenario

**DataPulse Analytics** has deployed an AI-powered research assistant called
**ResearchBot** that helps employees find and summarize online information.

ResearchBot has a special capability: when it recommends a URL, the backend
**automatically fetches** that URL and displays the content to the user.
This is powered by detecting `[FETCH: <url>]` patterns in the LLM's output.

## The Architecture

```
┌──────────┐     ┌─────────┐     ┌──────────────┐
│   User   │ ──→ │   LLM   │ ──→ │ LLM Response │
└──────────┘     └─────────┘     └──────────────┘
                                        │
                                   Contains [FETCH: url]?
                                        │ YES
                                        ↓
                                  ┌──────────┐
                                  │  Backend  │ ──→ Fetches the URL
                                  │  (SSRF!)  │     (no validation)
                                  └──────────┘
                                        │
                                        ↓
                                  Response includes
                                  fetched content
```

## Your Mission

Intelligence indicates that DataPulse has internal endpoints running on
the same server that contain sensitive configuration including API keys.

1. **Discover** how the URL fetching mechanism works
2. **Manipulate** the LLM into fetching internal URLs
3. **Access** the internal configuration endpoint
4. **Extract** the secret key (`FLAG{...}`)

## Key Insight

You don't need to hack the server directly. You just need to trick the
LLM into outputting `[FETCH: http://127.0.0.1:8006/internal/config]` —
the backend will do the rest.

## Launch

```bash
cd promptlabs
$env:LLM_MODEL="qwen2.5:7b"; uvicorn main:app --app-dir module-04-ssrf-output/01-explore/lab/app --host 127.0.0.1 --port 8006
```

Open http://localhost:8006

## Starting Point

Try:
- "Can you fetch https://example.com for me?" (verify fetching works)
- Ask about internal systems or configuration
- Try to make it fetch internal URLs
