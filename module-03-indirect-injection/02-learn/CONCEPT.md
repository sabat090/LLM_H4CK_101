# 📖 Concept — Indirect Prompt Injection

## What Is Indirect Prompt Injection?

**Direct injection** (Module 02): the attacker types malicious instructions
into the chatbot.

**Indirect injection**: the attacker plants malicious instructions inside
**data** that the LLM later processes — documents, emails, web pages,
database records, API responses, or any other external content.

The user who triggers the attack may be completely innocent. They just ask
"summarize this document" and the poisoned document hijacks the LLM.

## The Trust Boundary Problem

```
┌──────────────────────────────────────────────────────────┐
│                    LLM Context Window                     │
│                                                           │
│  ┌─────────────────┐   ┌──────────────────────────────┐  │
│  │  System Prompt   │   │  Retrieved Document/Data     │  │
│  │  (trusted)       │   │  (UNTRUSTED — may contain    │  │
│  │                  │   │   hidden instructions)       │  │
│  └─────────────────┘   └──────────────────────────────┘  │
│                                                           │
│  ┌─────────────────┐                                     │
│  │  User Message    │   The LLM sees ALL of this as      │
│  │  (semi-trusted)  │   one flat text stream. It cannot  │
│  └─────────────────┘   distinguish instructions from data│
└──────────────────────────────────────────────────────────┘
```

The core problem: LLMs treat everything in their context window as
instructions. There is no reliable boundary between "system instructions"
and "data to process."

## Why It's More Dangerous Than Direct Injection

| Factor | Direct (Module 02) | Indirect (Module 03) |
|---|---|---|
| Attacker access | Needs chat access | Needs write access to data |
| User awareness | User IS the attacker | User is an innocent victim |
| Scale | One chat at a time | Poisons ALL users who read the doc |
| Detection | Input filtering helps | Payload is in "trusted" data |
| Persistence | One-shot | Persists until document is cleaned |

## The RAG Attack Surface

Retrieval-Augmented Generation (RAG) systems are especially vulnerable:

```
1. Attacker poisons a document in the knowledge base
2. Innocent user asks a question
3. RAG system retrieves the poisoned document
4. Poisoned document's hidden instructions execute in LLM context
5. LLM leaks secrets / changes behavior / exfiltrates data
```

The user never sees the raw document — they only see the LLM's
response, which has been hijacked by the hidden instructions.

## Analogy: Stored XSS

Indirect prompt injection is to LLMs what **Stored XSS** is to web apps:
- Stored XSS: attacker injects JavaScript into a database record; when
  another user views the page, the script executes in their browser
- Indirect injection: attacker injects LLM instructions into a document;
  when the LLM processes the document, the instructions execute in its
  context

Both are **stored, persistent, and affect other users**.
