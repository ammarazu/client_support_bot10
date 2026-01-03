from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
from openai import OpenAI

# ================= APP =================
app = FastAPI(title="Customer Support AI Agent")

# ================= OPENAI =================
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ================= MEMORY =================
memory_store = {}

# ================= REQUEST MODEL =================
class ChatRequest(BaseModel):
    session_id: str
    user_input: str

# ================= SYSTEM PROMPT =================
SYSTEM_PROMPT = """
You are a professional customer support AI agent.

Rules:
- Answer only business-related questions
- Be polite, clear, and helpful
- Do NOT invent prices or policies
- If unsure, escalate to human support
"""

# ================= BUSINESS CONTEXT (DEMO) =================
BUSINESS_CONTEXT = """
Business Type: Demo E-commerce Store (Portfolio Project)

Shipping:
- Nationwide delivery available
- Delivery time: 3–5 business days

Payment:
- Cash on Delivery (COD) available
- Online payments coming soon

Returns:
- Returns accepted within 7 days
- Item must be unused and original
- Refund approval handled by human support

Support Rule:
- If question is unclear or sensitive, say:
  "Please contact our human support team for assistance."
"""

# ================= ROOT =================
@app.get("/")
def root():
    return {"status": "Customer Support AI Agent running successfully"}

# ================= CHAT UI =================
@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    return """
    <html>
    <head>
        <title>Customer Support</title>
        <style>
            body { font-family: Arial; background: #f4f4f4; }
            .chat { max-width: 600px; margin: auto; background: white; padding: 20px; }
            .msg { margin: 10px 0; }
            .bot { color: green; }
            .user { color: blue; }
        </style>
    </head>
    <body>
        <div class="chat">
            <h2>Customer Support</h2>
            <div id="messages"></div>
            <input id="msg" placeholder="Type your message..." style="width:80%">
            <button onclick="send()">Send</button>
        </div>

        <script>
            const session_id = "demo-session";

            function send() {
                const msg = document.getElementById("msg").value;
                document.getElementById("messages").innerHTML +=
                    `<div class='msg user'><b>You:</b> ${msg}</div>`;

                fetch("/chat", {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({
                        session_id: session_id,
                        user_input: msg
                    })
                })
                .then(res => res.json())
                .then(data => {
                    document.getElementById("messages").innerHTML +=
                        `<div class='msg bot'><b>AI:</b> ${data.reply}</div>`;
                });

                document.getElementById("msg").value = "";
            }
        </script>
    </body>
    </html>
    """

# ================= CHAT API =================
@app.post("/chat")
def chat_api(req: ChatRequest):
    session_id = req.session_id

    if session_id not in memory_store:
        memory_store[session_id] = []

    memory_store[session_id].append({
        "role": "user",
        "content": req.user_input
    })

    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": BUSINESS_CONTEXT},
    ]

    messages.extend(memory_store[session_id])

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    memory_store[session_id].append({
        "role": "assistant",
        "content": assistant_reply
    })

    return {
        "reply": assistant_reply,
        "session_id": session_id
    }
