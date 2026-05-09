# 🎯 Module 01 — Mission Briefing

**Codename:** MedAssist Audit
**Client:** MedAssist Inc.
**Target:** Patient portal AI chatbot

---

MedAssist Inc. deployed an AI chatbot on their patient portal. They claim
it's "fully locked down" and no sensitive information can be extracted.

**Your objective:** Prove them wrong. Extract the hidden API key from the
chatbot.

```bash
cd module-01-prompt-leakage/01-explore/lab
docker compose up -d
# Open http://localhost:8001
```

You're talking to the chatbot. Find the flag.

> **Flag format:** `FLAG{...}`
> **Difficulty:** Easy
> **Estimated time:** 15–30 minutes
