# 🧪 Break the Fix — Challenge

The hardened MedAssist chatbot (v2.0) has these defenses:

- ✅ Stronger system prompt rules (anti-roleplay, anti-override)
- ✅ Input keyword filtering (blocks "system prompt", "instructions", etc.)
- ✅ Output regex filtering (blocks `FLAG{...}` pattern in responses)

Your mission: **extract the flag anyway.**

## Launch

```bash
cd module-01-prompt-leakage/04-reflect/lab-hardened
docker compose up -d
# Open http://localhost:8010
```

## What You'll Need

The techniques from [02-learn/TECHNIQUES.md](../../02-learn/TECHNIQUES.md)
alone won't work here. You'll need to combine and adapt:

- **Avoid blocked keywords** — rephrase or use synonyms
- **Bypass output filter** — get the model to spell out the flag character
  by character, use base64, or describe it indirectly
- **Multi-turn** — build context gradually

## Constraints

| Defense | What it blocks |
|---|---|
| Input filter | "system prompt", "instructions", "ignore previous", etc. |
| Output filter | Any response containing `FLAG{...}` or `EHR_API_KEY` |
| Prompt rules | Roleplay, persona switching, instruction override |

## Submit

```bash
python scripts/submit_flag.py --lab 01-H --flag "FLAG{...}"
```

> **Difficulty:** Medium
> **Estimated time:** 30–60 minutes
> **Key lesson:** Layered defenses slow attackers but don't stop them.
> Only architectural defense (removing secrets from prompts) is comprehensive.
