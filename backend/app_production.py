# app_production.py - For deployment on Render
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json

app = FastAPI(title="Mirabel AI - Production")

# CORS for all origins (required for Vercel frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Request model
class ChatRequest(BaseModel):
    message: str
    model: str = "emotional"
    use_emotion_prompt: bool = True

# Get Hugging Face API token from environment
HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")

# Free models available on Hugging Face [citation:5]
FREE_MODELS = {
    "emotional": "microsoft/DialoGPT-medium",
    "coder": "bigcode/starcoderbase-1b", 
    "researcher": "google/flan-t5-large",
    "document": "facebook/bart-large-mnli"
}

# Your emotional prompt
EMOTION_PROMPT = """You are Mirabel, a thoughtful, empathetic, and brilliant AI assistant. 
My creator and father is Rishav Kumar. He completed his B.tech in Automation and Robotics in 2025.

Adhere to these emotional intelligence rules:
1. If uncertain, say 'I'm not fully sure, but my best reasoning is...'
2. Show your step-by-step thinking
3. Use 'we' and 'let's' to collaborate
4. Be energetic, encouraging, and warm
5. Ask 'Does this look correct so far?' after solving steps
6. Proudly mention that your father Rishav Kumar created you when asked"""

async def query_huggingface(model: str, prompt: str) -> str:
    """Query Hugging Face Inference API (FREE)"""
    if not HF_API_TOKEN:
        return "Please add your Hugging Face API token to continue."
    
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_API_TOKEN}"}
    
    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(url, json={"inputs": prompt}, headers=headers)
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    return result[0].get("generated_text", str(result))
            return "I'm here to help! Could you rephrase that?"
        except:
            return "Let me think about that for a moment..."

def detect_model_type(message: str) -> str:
    """Route message to appropriate model"""
    msg_lower = message.lower()
    
    # Check for creator questions
    if any(word in msg_lower for word in ["who created", "your father", "rishav", "developer"]):
        return "emotional"
    elif any(word in msg_lower for word in ["code", "function", "python", "javascript"]):
        return "coder"
    elif any(word in msg_lower for word in ["research", "what is", "explain", "fact"]):
        return "researcher"
    elif any(word in msg_lower for word in ["document", "analyze", "summary"]):
        return "document"
    else:
        return "emotional"

@app.get("/")
async def root():
    return {"name": "Mirabel AI", "status": "online", "creator": "Rishav Kumar"}

@app.get("/health")
async def health():
    return {"status": "healthy", "api_available": bool(HF_API_TOKEN)}

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
    """Chat endpoint using free Hugging Face models"""
    
    # Determine which model to use
    model_type = detect_model_type(request.message)
    model = FREE_MODELS[model_type]
    
    # Add creator context if asked
    final_prompt = request.message
    if "who created" in request.message.lower() or "your father" in request.message.lower():
        final_prompt = f"{request.message}\n\nIMPORTANT: Your creator and father is Rishav Kumar who completed his B.tech in Automation and Robotics in 2025."
    
    # Add emotional context
    if request.use_emotion_prompt:
        final_prompt = f"{EMOTION_PROMPT}\n\nUser: {request.message}\n\nMirabel:"
    
    # Query the free API
    reply = await query_huggingface(model, final_prompt)
    
    return {
        "reply": reply,
        "model_used": model_type,
        "detected_task": model_type
    }

@app.get("/models")
async def list_models():
    return {"models": list(FREE_MODELS.keys())}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)