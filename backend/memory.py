# memory.py - Completely Fixed Google Drive Memory System
import os
import pickle
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

class MirabelMemory:
    def __init__(self, credentials_file='credentials.json', folder_name='Mirabel_Memory'):
        self.credentials_file = credentials_file
        self.folder_name = folder_name
        self.service = None
        self.memory_folder_id = None
        self.conversations = []
        
        if os.path.exists(credentials_file):
            self.connect_drive()
        else:
            print(f"⚠️ Credentials file not found: {credentials_file}")
            print("Memory will work locally but not sync to Google Drive")
    
    def connect_drive(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive.file']
            )
            self.service = build('drive', 'v3', credentials=creds)
            self.get_or_create_memory_folder()
            print("✅ Google Drive connected!")
            return True
        except Exception as e:
            print(f"❌ Drive connection failed: {e}")
            return False
    
    def get_or_create_memory_folder(self):
        try:
            results = self.service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder'",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.memory_folder_id = folders[0]['id']
                print(f"📁 Found existing folder: {self.folder_name}")
            else:
                file_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                self.memory_folder_id = folder.get('id')
                print(f"📁 Created new folder: {self.folder_name}")
        except Exception as e:
            print(f"⚠️ Folder error: {e}")
    
    def save_conversation(self, user_message, ai_response, model_used):
        timestamp = datetime.now().isoformat()
        
        conversation_entry = {
            'timestamp': timestamp,
            'user': user_message,
            'ai': ai_response,
            'model': model_used
        }
        
        self.load_conversations()
        self.conversations.append(conversation_entry)
        
        if self.service and self.memory_folder_id:
            try:
                data = pickle.dumps(self.conversations)
                file_name = f"conversations_{datetime.now().strftime('%Y%m%d')}.pkl"
                
                results = self.service.files().list(
                    q=f"name='{file_name}' and '{self.memory_folder_id}' in parents",
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                
                if files:
                    file_id = files[0]['id']
                    media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
                    self.service.files().update(fileId=file_id, media_body=media).execute()
                    print(f"💾 Updated existing file: {file_name}")
                else:
                    file_metadata = {
                        'name': file_name,
                        'parents': [self.memory_folder_id]
                    }
                    media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
                    self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f"💾 Created new file: {file_name}")
                return True
            except Exception as e:
                print(f"❌ Failed to save to Drive: {e}")
                # Fallback to local save
                self.save_local()
                return False
        else:
            # Local save only
            self.save_local()
            return True
    
    def save_local(self):
        """Save locally as fallback"""
        try:
            with open('conversations_local.pkl', 'wb') as f:
                pickle.dump(self.conversations, f)
            print(f"💾 Saved locally (Drive not available)")
        except Exception as e:
            print(f"❌ Local save failed: {e}")
    
    def load_conversations(self):
        """Load conversations from Drive or local"""
        # Try Drive first
        if self.service and self.memory_folder_id:
            try:
                results = self.service.files().list(
                    q=f"'{self.memory_folder_id}' in parents and name contains 'conversations'",
                    spaces='drive',
                    fields='files(id, name, createdTime)',
                    orderBy='createdTime desc'
                ).execute()
                
                files = results.get('files', [])
                
                if files:
                    file_id = files[0]['id']
                    request = self.service.files().get_media(fileId=file_id)
                    fh = io.BytesIO()
                    downloader = MediaIoBaseDownload(fh, request)
                    done = False
                    while not done:
                        status, done = downloader.next_chunk()
                    
                    fh.seek(0)
                    self.conversations = pickle.load(fh)
                    print(f"📚 Loaded {len(self.conversations)} conversations from Drive")
                    return self.conversations
            except Exception as e:
                print(f"⚠️ Could not load from Drive: {e}")
        
        # Try local file
        if os.path.exists('conversations_local.pkl'):
            try:
                with open('conversations_local.pkl', 'rb') as f:
                    self.conversations = pickle.load(f)
                print(f"📚 Loaded {len(self.conversations)} conversations locally")
            except Exception as e:
                print(f"⚠️ Could not load local file: {e}")
                self.conversations = []
        else:
            self.conversations = []
        
        return self.conversations
    
    def get_context_for_prompt(self, limit=5):
        """Get recent conversations as context for AI prompts"""
        self.load_conversations()
        if not self.conversations:
            return ""
        
        recent = self.conversations[-limit:]
        context = "\n\n📝 Previous conversation history (for context):\n"
        for conv in recent:
            context += f"[{conv['timestamp'][:16]}] "
            context += f"User asked: {conv['user'][:100]}\n"
            context += f"  → I responded: {conv['ai'][:100]}\n\n"
        
        return context

# Create global instance
memory = MirabelMemory()

print("🧠 Memory system initialized")
if os.path.exists('credentials.json'):
    print("   Google Drive credentials found - will sync to cloud")
else:
    print("   No credentials.json found - working in local-only mode")