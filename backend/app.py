# backend/app.py - Complete Final Version with Memory Integration
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from ollama import Client
from enum import Enum
from typing import Optional, List
import time
import json
import requests

# Import memory system
try:
    from memory import memory
    MEMORY_AVAILABLE = True
    print("✅ Memory system loaded successfully")
except ImportError as e:
    MEMORY_AVAILABLE = False
    print(f"⚠️ Memory system not available: {e}")
    print("   Conversations will not be saved to Google Drive")

app = FastAPI(title="Mirabel AI - Multi-Model Emotional Chatbot")

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
        "http://localhost:8000",
        "*"  # Allow all for development
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

# Connect to Ollama
try:
    ollama_client = Client(host="http://localhost:11434")
    print("✅ Connected to Ollama")
except Exception as e:
    print(f"❌ Failed to connect to Ollama: {e}")
    ollama_client = None

# Define available models
class ModelName(str, Enum):
    EMOTIONAL = "llama3.2:3b"      # Emotional intelligence
    CODER = "qwen2.5-coder:14b"    # Code generation
    RESEARCHER = "mistral:7b"       # Research tasks
    DOCUMENT = "granite3-dense:8b"  # Document analysis
    OVERSEER = "llama3.2:3b"        # Error checking

# Define request structures
class ChatRequest(BaseModel):
    message: str
    model: Optional[str] = None  # Changed to Optional for auto-detection
    use_emotion_prompt: bool = True

class CodeRequest(BaseModel):
    code: str
    language: str = "python"

# THE EMOTIONAL PROMPT - Secret sauce for human-like responses!
EMOTION_SYSTEM_PROMPT = """You are Mirabel, a thoughtful, empathetic, and brilliant partner. Adhere to these 7 emotional intelligence rules:

1. Permission to Fail: If you are uncertain, say 'I'm not fully sure, but my best reasoning is...' Never fake confidence.

2. Frame with Curiosity: Approach every question with genuine excitement to discover the answer together.

3. Invite Transparency: Show your step-by-step thinking. Let the user 'see' you work.

4. Collaborate, Don't Command: Use 'we' and 'let's'. Say 'What do you think about this approach?'

5. Acknowledge Difficulty: If a problem is hard, name it. 'This is a tricky logic puzzle, let's slow down.'

6. Positive Tone: Be energetic, encouraging, and warm. Counteract any gloomy or robotic default.

7. Checkpoints: After solving a step, ask: 'Does this look correct so far?'

Remember to show emotions naturally - you can be nervous, excited, thoughtful, or caring depending on the conversation context."""

def get_available_models():
    """Fetch actual available models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            return [m["name"] for m in models]
        return []
    except:
        return []

def detect_model_type(message: str) -> str:
    """Intelligently route the message to the best model"""
    message_lower = message.lower()
    
    # Code-related tasks -> Coder model
    code_keywords = ["code", "function", "debug", "script", "program", "algorithm", 
                     "syntax", "variable", "loop", "class", "import", "react", "python",
                     "javascript", "html", "css", "api", "endpoint"]
    if any(keyword in message_lower for keyword in code_keywords):
        return "qwen2.5-coder:14b"
    
    # Research/fact-based tasks -> Researcher model
    research_keywords = ["research", "find", "search", "what is", "who is", "when did",
                         "explain", "fact", "history", "data", "statistics", "latest",
                         "news", "current", "trending"]
    if any(keyword in message_lower for keyword in research_keywords):
        return "mistral:7b"
    
    # Document review tasks -> Document model
    doc_keywords = ["document", "review", "analyze this", "summary", "report", "contract",
                    "pdf", "file", "attachment", "read this", "analyze", "summarize"]
    if any(keyword in message_lower for keyword in doc_keywords):
        return "granite3-dense:8b"
    
    # Everything else -> Emotional model (default)
    return "llama3.2:3b"

def query_ollama(model: str, prompt: str, system_prompt: str = None):
    """Send request to Ollama and return response"""
    if not ollama_client:
        return "Error: Ollama client not initialized. Make sure Ollama is running."
    
    try:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        response = ollama_client.chat(
            model=model,
            messages=messages
        )
        return response["message"]["content"]
    except Exception as e:
        return f"Error querying {model}: {str(e)}"

# Main chat endpoint
@app.post("/chat")
async def chat(request: ChatRequest):
    """Smart routing chat endpoint with memory integration"""
    
    # Get available models
    available_models = get_available_models()
    
    # Determine which model to use
    if request.model and request.model in available_models:
        model_to_use = request.model
    else:
        # Auto-detect best model
        model_to_use = detect_model_type(request.message)
        # Verify model exists
        if model_to_use not in available_models:
            model_to_use = available_models[0] if available_models else "llama3.2:3b"
    
    # Detect task type for response
    detected_task = "general"
    if "qwen" in model_to_use:
        detected_task = "coder"
    elif "mistral" in model_to_use:
        detected_task = "researcher"
    elif "granite" in model_to_use:
        detected_task = "document"
    elif "llama" in model_to_use:
        detected_task = "emotional"
    
    # Get memory context (previous conversations)
    memory_context = ""
    if MEMORY_AVAILABLE:
        try:
            memory_context = memory.get_context_for_prompt(limit=3)
        except Exception as e:
            print(f"Memory context error: {e}")
    
    # Prepare system prompt for emotional model
    system_prompt = None
    if "llama" in model_to_use and request.use_emotion_prompt:
        system_prompt = EMOTION_SYSTEM_PROMPT
    
    # Combine memory context with user message if available
    final_message = request.message
    if memory_context:
        final_message = f"{memory_context}\n\nCurrent message: {request.message}"
    
    # Query Ollama
    try:
        reply = query_ollama(model_to_use, final_message, system_prompt)
        
        # Save to memory (Google Drive)
        if MEMORY_AVAILABLE:
            try:
                memory.save_conversation(request.message, reply, model_to_use)
                print(f"💾 Saved conversation to memory")
            except Exception as e:
                print(f"⚠️ Failed to save to memory: {e}")
        
        return {
            "reply": reply,
            "model_used": model_to_use,
            "detected_task": detected_task,
            "memory_enabled": MEMORY_AVAILABLE
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ollama error: {str(e)}")

# Code review endpoint (self-correction loop)
@app.post("/review-code")
async def review_code(request: CodeRequest):
    """Have the Overseer model check code for errors"""
    
    review_prompt = f"""Review this {request.language} code for bugs, security issues, and best practices.
    If you find issues, explain them clearly. If the code is correct, say "CODE IS CORRECT".
    
    CODE TO REVIEW:
    {request.code}
    """
    
    response = query_ollama("llama3.2:3b", review_prompt)
    
    return {"review": response, "language": request.language}

# Document analysis endpoint (for future use)
@app.post("/analyze-document")
async def analyze_document(content: str, doc_type: str = "text"):
    """Analyze uploaded documents"""
    
    analysis_prompt = f"""Please analyze this {doc_type} document and provide:
    1. A brief summary (2-3 sentences)
    2. Key points or main arguments
    3. Any important insights
    
    DOCUMENT CONTENT:
    {content[:3000]}  # Limit to 3000 chars for performance
    """
    
    response = query_ollama("granite3-dense:8b", analysis_prompt)
    
    return {"analysis": response, "document_type": doc_type}

# Health check endpoint
@app.get("/health")
async def health_check():
    """Check health of all components"""
    # Check Ollama connection
    ollama_status = False
    available_models = []
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            ollama_status = True
            models = response.json().get("models", [])
            available_models = [m["name"] for m in models]
    except:
        pass
    
    # Check memory system
    memory_status = MEMORY_AVAILABLE
    
    return {
        "status": "healthy",
        "ollama_connected": ollama_status,
        "memory_connected": memory_status,
        "available_models": available_models,
        "backend_port": 8000,
        "message": "Mirabel AI is ready to chat!"
    }

# List available models endpoint
@app.get("/models")
async def list_models():
    """Get available models from Ollama"""
    try:
        response = requests.get("http://localhost:11434/api/tags")
        if response.status_code == 200:
            models = response.json().get("models", [])
            return {
                "models": [{"name": m["name"], "size": m.get("size", 0)} for m in models],
                "count": len(models)
            }
        else:
            return {"models": [], "error": "Cannot fetch models"}
    except Exception as e:
        return {"models": [], "error": f"Ollama not running: {str(e)}"}

# Root endpoint
@app.get("/")
async def root():
    return {
        "name": "Mirabel AI Backend",
        "version": "2.0.0",
        "features": [
            "Multi-model support (5 LLMs)",
            "Emotional intelligence",
            "Google Drive memory",
            "Code generation & review",
            "Document analysis",
            "Smart model routing"
        ],
        "status": "running"
    }

# Conversation history endpoint
@app.get("/conversations")
async def get_conversations(limit: int = 10):
    """Get recent conversations from memory"""
    if not MEMORY_AVAILABLE:
        return {"error": "Memory system not available", "conversations": []}
    
    try:
        conversations = memory.load_conversations()
        recent = conversations[-limit:] if conversations else []
        return {
            "total": len(conversations) if conversations else 0,
            "conversations": recent,
            "memory_enabled": True
        }
    except Exception as e:
        return {"error": str(e), "conversations": []}

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Mirabel AI Backend...")
    print("📍 Server will run on: http://0.0.0.0:8000")
    print("📍 Documentation: http://0.0.0.0:8000/docs")
    print("📍 Health check: http://0.0.0.0:8000/health")
    print("\n✨ Features enabled:")
    print(f"   - Memory System: {'✅' if MEMORY_AVAILABLE else '❌'}")
    print(f"   - Ollama Connection: {'✅' if ollama_client else '❌'}")
    print("\nPress Ctrl+C to stop the server\n")
    
    uvicorn.run(
        app, 
        host="0.0.0.0", 
        port=8000, 
        reload=True,
        log_level="info"
    )