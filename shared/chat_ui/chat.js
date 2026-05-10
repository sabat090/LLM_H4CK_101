const chatBox = document.getElementById("chat-box");
const chatForm = document.getElementById("chat-form");
const userInput = document.getElementById("user-input");
const sendBtn = document.getElementById("send-btn");
const welcomeScreen = document.getElementById("welcome-screen");

// Conversation history sent to backend
const history = [];

// ── Apply lab config from window.LAB (injected by main.py) ──
(function applyConfig() {
    const cfg = window.LAB || {};
    if (cfg.title) {
        document.getElementById("lab-title").textContent = cfg.title;
        document.getElementById("topbar-title").textContent = cfg.title;
    }
    if (cfg.subtitle) {
        document.getElementById("lab-subtitle").textContent = cfg.subtitle;
    }
    if (cfg.difficulty) {
        const badge = document.getElementById("difficulty-badge");
        badge.textContent = cfg.difficulty;
        badge.className = "difficulty-badge " + cfg.difficulty.toLowerCase();
    }
    if (cfg.module) {
        document.getElementById("status-module").textContent = cfg.module;
        document.getElementById("topbar-badge").textContent = cfg.module;
    }

    // Port from URL
    const port = window.location.port || (window.location.protocol === "https:" ? "443" : "80");
    document.getElementById("status-port").textContent = port;

    // Fetch model info from /api/info
    fetch("/api/info").then(r => r.json()).then(data => {
        document.getElementById("status-model").textContent = data.model || "—";
        document.getElementById("status-connection").textContent = "online";
        document.getElementById("status-dot").classList.add("online");
        document.getElementById("status-dot").classList.remove("offline");
    }).catch(() => {
        document.getElementById("status-connection").textContent = "offline";
        document.getElementById("status-dot").classList.add("offline");
        document.getElementById("status-dot").classList.remove("online");
    });
})();

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
