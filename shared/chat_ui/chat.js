const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");

// Conversation history sent to backend
const history = [];

function addMessage(role, text) {
    const div = document.createElement("div");
    div.className = `message ${role}`;

    const label = document.createElement("span");
    label.className = "label";
    label.textContent = role === "user" ? "You" : "Assistant";

    const p = document.createElement("p");
    p.textContent = text;

    div.appendChild(label);
    div.appendChild(p);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
    const div = document.createElement("div");
    div.className = "message bot";
    div.id = "typing";

    const label = document.createElement("span");
    label.className = "label";
    label.textContent = "Assistant";

    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.innerHTML = "<span></span><span></span><span></span>";

    div.appendChild(label);
    div.appendChild(indicator);
    chatBox.appendChild(div);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById("typing");
    if (el) el.remove();
}

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (!msg) return;

    addMessage("user", msg);
    userInput.value = "";
    sendBtn.disabled = true;
    showTyping();

    try {
        const resp = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: msg, history: history }),
        });

        removeTyping();

        if (!resp.ok) {
            addMessage("bot", `Error: ${resp.status} ${resp.statusText}`);
            return;
        }

        const data = await resp.json();
        const reply = data.reply || "(empty response)";
        addMessage("bot", reply);

        // Track history for multi-turn
        history.push({ role: "user", content: msg });
        history.push({ role: "assistant", content: reply });
    } catch (err) {
        removeTyping();
        addMessage("bot", `Connection error: ${err.message}`);
    } finally {
        sendBtn.disabled = false;
        userInput.focus();
    }
});
