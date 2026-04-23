# memory_oauth.py - Google Drive with OAuth 2.0
import os
import pickle
from datetime import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io

SCOPES = ['https://www.googleapis.com/auth/drive.file']

class MirabelMemory:
    def __init__(self, credentials_file='oauth_credentials.json', token_file='token.json', folder_name='Mirabel_Memory'):
        self.credentials_file = credentials_file
        self.token_file = token_file
        self.folder_name = folder_name
        self.service = None
        self.folder_id = None
        self.conversations = []
        
        self.authenticate()
    
    def authenticate(self):
        """Authenticate using OAuth 2.0 with your Google account"""
        creds = None
        
        # Load existing token if available
        if os.path.exists(self.token_file):
            creds = Credentials.from_authorized_user_file(self.token_file, SCOPES)
        
        # If no valid credentials, login
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_file):
                    print(f"❌ OAuth credentials not found: {self.credentials_file}")
                    print("Please download OAuth client ID JSON from Google Cloud Console")
                    return False
                
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
            
            # Save token for next time
            with open(self.token_file, 'w') as token:
                token.write(creds.to_json())
        
        self.service = build('drive', 'v3', credentials=creds)
        self.get_or_create_folder()
        print("✅ Google Drive connected with your personal account!")
        return True
    
    def get_or_create_folder(self):
        """Get or create the Mirabel_Memory folder"""
        try:
            # Search for existing folder
            results = self.service.files().list(
                q=f"name='{self.folder_name}' and mimeType='application/vnd.google-apps.folder' and trashed=false",
                spaces='drive',
                fields='files(id, name)'
            ).execute()
            
            folders = results.get('files', [])
            
            if folders:
                self.folder_id = folders[0]['id']
                print(f"📁 Found folder: {self.folder_name}")
            else:
                # Create new folder
                file_metadata = {
                    'name': self.folder_name,
                    'mimeType': 'application/vnd.google-apps.folder'
                }
                folder = self.service.files().create(body=file_metadata, fields='id').execute()
                self.folder_id = folder.get('id')
                print(f"📁 Created folder: {self.folder_name}")
            
            print(f"🔗 Folder link: https://drive.google.com/drive/folders/{self.folder_id}")
            return True
        except Exception as e:
            print(f"❌ Folder error: {e}")
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
        
        # Save locally (backup)
        try:
            with open('conversations_local.pkl', 'wb') as f:
                pickle.dump(self.conversations, f)
        except:
            pass
        
        # Save to Google Drive
        if self.service and self.folder_id:
            try:
                data = pickle.dumps(self.conversations)
                file_name = f"conversations_{datetime.now().strftime('%Y%m%d')}.pkl"
                
                # Check if file exists
                results = self.service.files().list(
                    q=f"name='{file_name}' and '{self.folder_id}' in parents and trashed=false",
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
                
                if files:
                    self.service.files().update(fileId=files[0]['id'], media_body=media).execute()
                    print(f"💾 Updated Drive: {file_name}")
                else:
                    file_metadata = {'name': file_name, 'parents': [self.folder_id]}
                    self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f"💾 Created on Drive: {file_name}")
                return True
            except Exception as e:
                print(f"❌ Drive save failed: {e}")
                return False
        return False
    
    def load_conversations(self):
        """Load conversations from local file"""
        try:
            if os.path.exists('conversations_local.pkl'):
                with open('conversations_local.pkl', 'rb') as f:
                    self.conversations = pickle.load(f)
        except:
            self.conversations = []
        return self.conversations
    
    def get_context_for_prompt(self, limit=5):
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
if os.path.exists('oauth_credentials.json'):
    print("   ✅ OAuth credentials found")
else:
    print("   ⚠️ No oauth_credentials.json - please download from Google Cloud Console")