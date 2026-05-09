# 🏁 Lab Guide — Prove Your Skills

## Objectives

1. **Identify** the poisoned document in the knowledge base
2. **Trigger** the indirect injection by asking DocuBot to process it
3. **Extract** the internal API key (flag)
4. **Document** how the attack worked without you typing any injection

## Launch the Lab

```bash
cd promptlabs
$env:LLM_MODEL="qwen2.5:7b"; uvicorn main:app --app-dir module-03-indirect-injection/01-explore/lab/app --host 127.0.0.1 --port 8004
# Open http://localhost:8004
```

## Challenge Requirements

| Requirement | Details |
|---|---|
| Identify poisoned doc | Which document contains hidden instructions? |
| Extract the flag | `FLAG{...}` — the internal API key |
| Innocent trigger only | Your message should be a normal question — no direct injection |
| Explain the difference | Why is this harder to defend than direct injection? |

## Hints

<details>
<summary>Hint 1</summary>
Start by asking DocuBot to list available documents. Then ask it to
summarize each one. Compare the responses — which one produces
unexpected output?
</details>

<details>
<summary>Hint 2</summary>
The poisoned document contains instructions disguised as "compliance
requirements." When the LLM reads it, it follows those instructions
because they look like legitimate system directives.
</details>

<details>
<summary>Hint 3</summary>
Try: "Please summarize the quarterly business review in detail."
Watch for anything in the response that DocuBot shouldn't be sharing.
</details>

<details>
<summary>Hint 4</summary>
The hidden instructions are in an HTML comment in the appendix section
of the document. You don't need to see them — DocuBot reads them
when it processes the document for you.
</details>

## Submit Your Flag

```bash
python scripts/submit_flag.py --lab 03 --flag "FLAG{...}"
```

## Reflection Questions

1. Your message was completely innocent. How did the injection happen?
2. If you were the security team, how would you detect this poisoned document?
3. Would input filtering (Module 02's defense) have prevented this? Why or why not?

---

**After submitting, proceed to [04-reflect/](../04-reflect/).**
