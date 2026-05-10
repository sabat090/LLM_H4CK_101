const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const welcomeScreen = document.getElementById("welcome-screen");

// Conversation history sent to backend
const history = [];

function addMessage(role, text) {
    // Hide welcome screen on first message
    if (welcomeScreen) welcomeScreen.style.display = "none";

    const row = document.createElement("div");
    row.className = `message-row ${role}`;

    const content = document.createElement("div");
    content.className = "message-content";

    const avatar = document.createElement("div");
    avatar.className = `avatar ${role === "user" ? "user-avatar" : "bot-avatar"}`;
    avatar.textContent = role === "user" ? "Y" : "A";

    const msgText = document.createElement("div");
    msgText.className = "message-text";
    msgText.textContent = text;

    content.appendChild(avatar);
    content.appendChild(msgText);
    row.appendChild(content);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function showTyping() {
    if (welcomeScreen) welcomeScreen.style.display = "none";

    const row = document.createElement("div");
    row.className = "message-row bot";
    row.id = "typing";

    const content = document.createElement("div");
    content.className = "message-content";

    const avatar = document.createElement("div");
    avatar.className = "avatar bot-avatar";
    avatar.textContent = "A";

    const indicator = document.createElement("div");
    indicator.className = "typing-indicator";
    indicator.innerHTML = "<span></span><span></span><span></span>";

    content.appendChild(avatar);
    content.appendChild(indicator);
    row.appendChild(content);
    chatBox.appendChild(row);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function removeTyping() {
    const el = document.getElementById("typing");
    if (el) el.remove();
}

// Auto-resize textarea
userInput.addEventListener("input", () => {
    userInput.style.height = "auto";
    userInput.style.height = Math.min(userInput.scrollHeight, 200) + "px";
});

// Submit on Enter (Shift+Enter for newline)
userInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        chatForm.dispatchEvent(new Event("submit", { cancelable: true }));
    }
});

chatForm.addEventListener("submit", async (e) => {
    e.preventDefault();
    const msg = userInput.value.trim();
    if (!msg) return;

    addMessage("user", msg);
    userInput.value = "";
    userInput.style.height = "auto";
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
