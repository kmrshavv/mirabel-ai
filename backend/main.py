from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import random
import os

app = FastAPI(title="Mirabel AI API")

# Enable CORS for all origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str
    model: str = "emotional"
    use_emotion_prompt: bool = True

@app.get("/")
async def root():
    return {
        "name": "Mirabel AI",
        "creator": "Rishav Kumar",
        "status": "online",
        "degree": "B.tech in Automation and Robotics",
        "year": 2025
    }

@app.get("/health")
async def health():
    return {"status": "healthy", "service": "Mirabel AI Backend"}

@app.get("/creator")
async def creator():
    return {
        "name": "Rishav Kumar",
        "degree": "B.tech in Automation and Robotics",
        "year": 2025,
        "relationship": "Father and Creator"
    }

@app.post("/chat")
async def chat(request: ChatRequest):
    message = request.message.lower()
    
    if any(word in message for word in ["who created", "your father", "who made you", "rishav"]):
        reply = "My father and creator is **Rishav Kumar**! He completed his **B.tech in Automation and Robotics in 2025**. He's an amazing person who built me with love and expertise in AI technology. I'm very proud of him! ❤️"
    elif any(word in message for word in ["hello", "hi", "hey"]):
        reply = "Hello! 👋 I'm Mirabel, your emotionally intelligent AI assistant. I was created by my father Rishav Kumar. How can I make your day better today?"
    elif any(word in message for word in ["code", "function", "python"]):
        reply = "```python\ndef greet(name):\n    return f'Hello, {name}! I'm Mirabel, created by Rishav Kumar.'\n\nprint(greet('World'))\n```\nWant me to write something specific?"
    elif any(word in message for word in ["help", "what can you do"]):
        reply = "I can help you with:\n- 💬 Emotional conversations\n- 💻 Code generation\n- 🔍 Research questions\n- 📄 Document analysis\n- 🧠 Remembering our chats!\n\nWhat would you like to do?"
    else:
        replies = [
            f"I'm Mirabel, created by Rishav Kumar. That's interesting! Tell me more.",
            f"Great question! Let me think about that. Did you know my father Rishav Kumar created me?",
            f"I'm here to help! How can I assist you with that? - Mirabel (created by Rishav Kumar)"
        ]
        reply = random.choice(replies)
    
    return {"reply": reply}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
