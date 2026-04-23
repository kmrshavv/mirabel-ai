# memory.py - Direct Google Drive Folder Access
import os
import pickle
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

class MirabelMemory:
    def __init__(self, credentials_file='credentials.json'):
        self.credentials_file = credentials_file
        self.service = None
        self.folder_id = "1Rhyz35B8oZc4w7FQaYgF4ZwmAeLBk76n"  # Your folder ID
        self.conversations = []
        
        if os.path.exists(credentials_file):
            self.connect_drive()
        else:
            print(f"⚠️ Credentials file not found: {credentials_file}")
    
    def connect_drive(self):
        try:
            creds = service_account.Credentials.from_service_account_file(
                self.credentials_file,
                scopes=['https://www.googleapis.com/auth/drive']
            )
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive connected!")
            print(f"📁 Using folder ID: {self.folder_id}")
            return True
        except Exception as e:
            print(f"❌ Drive connection failed: {e}")
            return False
    
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
        
        # Save locally first (always works)
        try:
            with open('conversations_local.pkl', 'wb') as f:
                pickle.dump(self.conversations, f)
            print(f"💾 Saved locally ({len(self.conversations)} conversations)")
        except Exception as e:
            print(f"❌ Local save failed: {e}")
        
        # Save to Google Drive
        if self.service:
            try:
                data = pickle.dumps(self.conversations)
                file_name = f"conversations_{datetime.now().strftime('%Y%m%d')}.pkl"
                
                # Check if file already exists in the folder
                results = self.service.files().list(
                    q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
                
                if files:
                    # Update existing file
                    file_id = files[0]['id']
                    self.service.files().update(fileId=file_id, media_body=media).execute()
                    print(f"💾 Updated file on Drive: {file_name}")
                else:
                    # Create new file
                    file_metadata = {
                        'name': file_name,
                        'parents': [self.folder_id]
                    }
                    self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f"💾 Created new file on Drive: {file_name}")
                return True
            except Exception as e:
                print(f"❌ Failed to save to Drive: {e}")
        else:
            print("⚠️ Drive not connected - saving locally only")
        
        return False
    
    def load_conversations(self):
        """Load conversations from local file"""
        try:
            if os.path.exists('conversations_local.pkl'):
                with open('conversations_local.pkl', 'rb') as f:
                    self.conversations = pickle.load(f)
                print(f"📚 Loaded {len(self.conversations)} conversations locally")
            else:
                self.conversations = []
                print("📭 No existing conversations found")
        except Exception as e:
            print(f"⚠️ Could not load: {e}")
            self.conversations = []
        
        # Also try to load from Drive (for continuity)
        if self.service:
            try:
                file_name = f"conversations_{datetime.now().strftime('%Y%m%d')}.pkl"
                results = self.service.files().list(
                    q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                    spaces='drive',
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
                    drive_conversations = pickle.load(fh)
                    if len(drive_conversations) > len(self.conversations):
                        self.conversations = drive_conversations
                        print(f"📚 Loaded {len(self.conversations)} conversations from Drive")
            except Exception as e:
                pass
        
        return self.conversations
    
    def get_context_for_prompt(self, limit=5):
        """Get recent conversations as context for AI prompts"""
        self.load_conversations()
        if not self.conversations:
            return ""
        
        recent = self.conversations[-limit:]
        context = "\n\n📝 Previous conversation history:\n"
        for conv in recent:
            context += f"[{conv['timestamp'][:16]}] User: {conv['user'][:100]}\n"
            context += f"  → Me: {conv['ai'][:100]}\n\n"
        
        return context

# Create global instance
memory = MirabelMemory()

print("\n🧠 Memory System Status:")
if os.path.exists('credentials.json'):
    print("   ✅ Google Drive credentials found")
    print(f"   📁 Target folder: https://drive.google.com/drive/folders/{memory.folder_id}")
else:
    print("   ⚠️ No credentials.json - working in local-only mode")