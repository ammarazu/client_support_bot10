from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.responses import HTMLResponse
import os
from openai import OpenAI

# ---------------- APP ----------------
app = FastAPI(title="Customer Support AI Agent")

# ---------------- OPENAI ----------------
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ---------------- MEMORY STORE ----------------
memory_store = {}

# ---------------- REQUEST MODEL ----------------
class ChatRequest(BaseModel):
    session_id: str
    user_input: str

# ---------------- SYSTEM PROMPT ----------------
SYSTEM_PROMPT = """
You are a professional customer support agent for this business.

Rules:
- Answer only using the business information provided
- Be polite, clear, and professional
- Do NOT invent information
- If something is not available, suggest contacting human support
"""

# ---------------- BUSINESS RULES (11.6) ----------------
BUSINESS_CONTEXT = """
Business Information:
- The business offers Cash on Delivery (COD)
- COD is available nationwide
- Delivery time is 3–5 working days
- Product prices are fixed and shown on the product page
- Refunds are accepted within 7 days of delivery
- For complex issues, customers should contact human support
"""

# ---------------- ROUTES ----------------

@app.get("/")
def root():
    return {"status": "Customer Support AI Agent running successfully"}

# ✅ SERVE CHAT UI
@app.get("/chat", response_class=HTMLResponse)
def chat_page():
    file_path = os.path.join(os.path.dirname(__file__), "chat.html")
    with open(file_path, "r", encoding="utf-8") as f:
        return f.read()

# ✅ HANDLE CHAT API
@app.post("/chat")
def chat_api(req: ChatRequest):
    session_id = req.session_id

    if session_id not in memory_store:
        memory_store[session_id] = []

    # Save user message
    memory_store[session_id].append({
        "role": "user",
        "content": req.user_input
    })

    # Prepare messages
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "system", "content": BUSINESS_CONTEXT},
    ]
    messages.extend(memory_store[session_id])

    # OpenAI call
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=messages
    )

    assistant_reply = response.choices[0].message.content

    # Save assistant reply
    memory_store[session_id].append({
        "role": "assistant",
        "content": assistant_reply
    })

    return {
        "reply": assistant_reply,
        "session_id": session_id
    }