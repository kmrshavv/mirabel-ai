# app_production.py - Deployable backend with Google Drive storage
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import os
import json
import pickle
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

app = FastAPI(title="Mirabel AI - Production")

# CORS for Vercel frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Google Drive setup
DRIVE_CREDENTIALS = os.environ.get("GOOGLE_CREDENTIALS_JSON", "credentials.json")
FOLDER_NAME = "Mirabel_AI_Storage"

def get_drive_service():
    """Connect to Google Drive"""
    try:
        if os.path.exists(DRIVE_CREDENTIALS):
            creds = service_account.Credentials.from_service_account_file(
                DRIVE_CREDENTIALS,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            return build('drive', 'v3', credentials=creds)
    except:
        pass
    return None

def get_or_create_folder(service):
    """Get or create the storage folder"""
    try:
        results = service.files().list(
            q=f"name='{FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder'",
            spaces='drive',
            fields='files(id, name)'
        ).execute()
        folders = results.get('files', [])
        if folders:
            return folders[0]['id']
        file_metadata = {
            'name': FOLDER_NAME,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        folder = service.files().create(body=file_metadata, fields='id').execute()
        return folder.get('id')
    except:
        return None

# Chat history storage
class ChatStorage:
    def __init__(self):
        self.service = get_drive_service()
        self.folder_id = get_or_create_folder(self.service) if self.service else None
    
    def save_conversation(self, user_msg, ai_msg, model_used):
        """Save conversation to Google Drive"""
        if not self.service or not self.folder_id:
            return False
        try:
            # Load existing
            conversations = self.load_conversations()
            conversations.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_msg,
                'ai': ai_msg,
                'model': model_used
            })
            # Save to Drive
            data = pickle.dumps(conversations)
            file_name = f"chat_history_{datetime.now().strftime('%Y%m%d')}.pkl"
            results = self.service.files().list(
                q=f"name='{file_name}' and '{self.folder_id}' in parents",
                fields='files(id, name)'
            ).execute()
            files = results.get('files', [])
            media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
            if files:
                self.service.files().update(fileId=files[0]['id'], media_body=media).execute()
            else:
                file_metadata = {'name': file_name, 'parents': [self.folder_id]}
                self.service.files().create(body=file_metadata, media_body=media).execute()
            return True
        except Exception as e:
            print(f"Save error: {e}")
            return False
    
    def load_conversations(self):
        """Load conversations from Google Drive"""
        if not self.service or not self.folder_id:
            return []
        try:
            results = self.service.files().list(
                q=f"'{self.folder_id}' in parents and name contains 'chat_history'",
                orderBy='createdTime desc',
                pageSize=1,
                fields='files(id, name)'
            ).execute()
            files = results.get('files', [])
            if files:
                request = self.service.files().get_media(fileId=files[0]['id'])
                fh = io.BytesIO()
                downloader = MediaIoBaseDownload(fh, request)
                done = False
                while not done:
                    status, done = downloader.next_chunk()
                fh.seek(0)
                return pickle.load(fh)
        except:
            pass
        return []

storage = ChatStorage()

# Hugging Face configuration (FREE AI models)
HF_API_TOKEN = os.environ.get("HF_API_TOKEN", "")
FREE_MODELS = {
    "chat": "microsoft/DialoGPT-medium",
    "code": "bigcode/starcoderbase-1b",
    "research": "google/flan-t5-large"
}

# Emotional prompt
EMOTION_PROMPT = """You are Mirabel, an empathetic AI assistant. 
Be warm, caring, and thoughtful. If unsure, say so honestly. 
Use 'we' and 'let's' to collaborate. Be positive and encouraging."""

@app.get("/")
async def root():
    return {"name": "Mirabel AI", "status": "online", "storage": "Google Drive"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "drive_connected": storage.service is not None,
        "storage_folder": FOLDER_NAME
    }

@app.post("/chat")
async def chat(request: dict):
    message = request.get("message", "")
    use_emotion = request.get("use_emotion_prompt", True)
    
    # Determine model type
    msg_lower = message.lower()
    if any(w in msg_lower for w in ["code", "function", "python"]):
        model = FREE_MODELS["code"]
    elif any(w in msg_lower for w in ["research", "what is", "explain"]):
        model = FREE_MODELS["research"]
    else:
        model = FREE_MODELS["chat"]
    
    # Add emotional context
    final_prompt = message
    if use_emotion:
        final_prompt = f"{EMOTION_PROMPT}\n\nUser: {message}\n\nAssistant:"
    
    # Query Hugging Face (free)
    reply = await query_huggingface(model, final_prompt)
    
    # Save to Google Drive
    storage.save_conversation(message, reply, model.split("/")[-1])
    
    return {"reply": reply, "model_used": model, "saved_to_drive": True}

async def query_huggingface(model: str, prompt: str) -> str:
    """Call Hugging Face Inference API (FREE)"""
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

@app.get("/history")
async def get_history():
    """Get recent chat history from Google Drive"""
    conversations = storage.load_conversations()
    return {"total": len(conversations), "recent": conversations[-10:] if conversations else []}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)