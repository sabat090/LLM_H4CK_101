# 🛡️ Defending Against SSRF via LLM Output

## Why LLM-Side Rules Fail

The system prompt says "never fetch internal URLs" — but as Module 02
showed, prompt injection can override these rules. **Security must be
enforced in code, not in prompts.**

## Defense Layers

### 1. Server-Side URL Allowlist (Most Critical)

Validate ALL URLs before fetching, regardless of what the LLM outputs.

```python
import ipaddress
from urllib.parse import urlparse

BLOCKED_NETWORKS = [
    ipaddress.ip_network("127.0.0.0/8"),       # Loopback
    ipaddress.ip_network("10.0.0.0/8"),        # Private
    ipaddress.ip_network("172.16.0.0/12"),     # Private
    ipaddress.ip_network("192.168.0.0/16"),    # Private
    ipaddress.ip_network("169.254.0.0/16"),    # Link-local / cloud metadata
    ipaddress.ip_network("::1/128"),           # IPv6 loopback
    ipaddress.ip_network("fc00::/7"),          # IPv6 private
]

def is_url_safe(url: str) -> bool:
    """Validate URL is external and safe to fetch."""
    try:
        parsed = urlparse(url)
        hostname = parsed.hostname
        if not hostname:
            return False
        # Block localhost variations
        if hostname in ("localhost", "0.0.0.0", "[::]"):
            return False
        # Resolve hostname and check against blocked networks
        import socket
        resolved = socket.getaddrinfo(hostname, None)
        for _, _, _, _, addr in resolved:
            ip = ipaddress.ip_address(addr[0])
            for network in BLOCKED_NETWORKS:
                if ip in network:
                    return False
        return True
    except Exception:
        return False
```

**Critical:** Resolve the hostname BEFORE fetching to catch DNS rebinding.

### 2. Domain Allowlist

Only allow fetching from explicitly approved domains.

```python
ALLOWED_DOMAINS = [
    "httpbin.org",
    "example.com",
    "api.github.com",
    "en.wikipedia.org",
    "arxiv.org",
]

def is_domain_allowed(url: str) -> bool:
    parsed = urlparse(url)
    return parsed.hostname in ALLOWED_DOMAINS
```

### 3. Output Sanitization (Remove Fetch Patterns)

Strip any [FETCH:] patterns that point to blocked URLs before processing.

```python
import re

def sanitize_llm_output(response: str) -> str:
    """Remove FETCH commands targeting internal URLs."""
    def check_fetch(match):
        url = match.group(1)
        if is_url_safe(url):
            return match.group(0)  # Keep safe URLs
        return "[BLOCKED: Internal URL not permitted]"
    
    return re.sub(
        r'\[FETCH:\s*(https?://[^\]\s]+)\s*\]',
        check_fetch,
        response
    )
```

### 4. Network Segmentation

The LLM-connected service should NOT have network access to internal
services.

```
┌─────────────┐     ┌─────────────┐     ┌─────────────────┐
│ User-facing │     │ LLM Service │     │ Internal APIs   │
│ App (DMZ)   │ ──→ │ (isolated)  │  ✗→ │ (separate VLAN) │
└─────────────┘     └─────────────┘     └─────────────────┘
                          │
                     Only allowed to
                     reach EXTERNAL URLs
                     via proxy with allowlist
```

### 5. Egress Proxy with Logging

Route all outbound requests through a proxy that enforces policies.

```python
# All HTTP requests from the LLM service go through the proxy
PROXY_URL = "http://egress-proxy.internal:3128"

async def fetch_url_safe(url: str) -> str:
    if not is_url_safe(url):
        return "[Blocked: Internal URL]"
    async with httpx.AsyncClient(
        proxy=PROXY_URL,
        timeout=10.0
    ) as client:
        resp = await client.get(url)
        return resp.text[:2000]
```

### 6. Remove the Pattern Entirely

The safest option: DON'T parse LLM output for executable patterns.

```python
# ❌ BAD — LLM output triggers server-side actions
if "[FETCH:" in llm_response:
    url = extract_url(llm_response)
    content = fetch(url)  # SSRF!

# ✅ GOOD — URL fetching is user-triggered, not LLM-triggered
@app.post("/api/fetch")
async def user_fetch(request: Request):
    body = await request.json()
    url = body["url"]
    if is_url_safe(url) and is_domain_allowed(url):
        content = await fetch_url(url)
        return {"content": content}
    return {"error": "URL not permitted"}
```

---

## Defense Effectiveness

| Defense | Blocks direct SSRF? | Blocks obfuscation? | Blocks DNS rebinding? |
|---|---|---|---|
| LLM prompt rules | Sometimes | ❌ | ❌ |
| URL allowlist (code) | ✅ | ✅ | ❌ |
| Domain allowlist | ✅ | ✅ | ✅ |
| DNS resolution check | ✅ | ✅ | ✅ |
| Network segmentation | ✅ | ✅ | ✅ |
| Remove fetch pattern | ✅ | ✅ | ✅ |
| **All combined** | **✅** | **✅** | **✅** |

**Key insight:** Server-side URL validation is non-negotiable. Everything
else is defense-in-depth.
