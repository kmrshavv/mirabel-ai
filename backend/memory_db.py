# memory_db.py - Google Drive + Database Integration
import os
import pickle
import json
from datetime import datetime
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload, MediaIoBaseDownload
import io
from database import db_manager

class HybridMemory:
    def __init__(self, credentials_file='oauth_credentials.json'):
        self.credentials_file = credentials_file
        self.service = None
        self.folder_id = None
        self.db = db_manager
        
        # Your Google Drive folder ID
        self.drive_folder_id = "1Rhyz35B8oZc4w7FQaYgF4ZwmAeLBk76n"
        
        if os.path.exists(credentials_file):
            self.connect_drive()
    
    def connect_drive(self):
        """Connect to Google Drive using OAuth"""
        try:
            from google.auth.transport.requests import Request
            from google.oauth2.credentials import Credentials
            from google_auth_oauthlib.flow import InstalledAppFlow
            
            SCOPES = ['https://www.googleapis.com/auth/drive.file']
            creds = None
            token_file = 'token.json'
            
            if os.path.exists(token_file):
                creds = Credentials.from_authorized_user_file(token_file, SCOPES)
            
            if not creds or not creds.valid:
                flow = InstalledAppFlow.from_client_secrets_file(self.credentials_file, SCOPES)
                creds = flow.run_local_server(port=0)
                with open(token_file, 'w') as token:
                    token.write(creds.to_json())
            
            self.service = build('drive', 'v3', credentials=creds)
            print("✅ Google Drive connected!")
            return True
        except Exception as e:
            print(f"⚠️ Drive connection failed: {e}")
            return False
    
    def save_conversation(self, user_message, ai_response, model_used, user_id=1):
        """Save to database AND Google Drive"""
        
        # 1. Save to Database (Structured)
        try:
            # Get or create active conversation
            convos = self.db.get_user_conversations(user_id, limit=1)
            if convos:
                conversation = convos[0]
            else:
                conversation = self.db.create_conversation(user_id)
            
            # Add messages
            self.db.add_message(conversation.id, 'user', user_message)
            self.db.add_message(conversation.id, 'assistant', ai_response)
            
            print(f"💾 Saved to database (Conversation: {conversation.id})")
        except Exception as e:
            print(f"⚠️ Database save failed: {e}")
        
        # 2. Save to Google Drive (Backup and Sync)
        if self.service:
            try:
                # Load existing conversations
                conversations = self.load_from_drive()
                conversations.append({
                    'timestamp': datetime.now().isoformat(),
                    'user': user_message,
                    'ai': ai_response,
                    'model': model_used,
                    'user_id': user_id
                })
                
                # Save to Drive
                data = pickle.dumps(conversations)
                file_name = f"conversations_{datetime.now().strftime('%Y%m%d')}.pkl"
                
                # Check if file exists
                results = self.service.files().list(
                    q=f"name='{file_name}' and '{self.drive_folder_id}' in parents",
                    spaces='drive',
                    fields='files(id, name)'
                ).execute()
                
                files = results.get('files', [])
                media = MediaIoBaseUpload(io.BytesIO(data), mimetype='application/octet-stream')
                
                if files:
                    self.service.files().update(fileId=files[0]['id'], media_body=media).execute()
                    print(f"💾 Updated Google Drive: {file_name}")
                else:
                    file_metadata = {'name': file_name, 'parents': [self.drive_folder_id]}
                    self.service.files().create(body=file_metadata, media_body=media, fields='id').execute()
                    print(f"💾 Created on Google Drive: {file_name}")
            except Exception as e:
                print(f"⚠️ Drive save failed: {e}")
        
        # 3. Local fallback
        self.save_local(user_message, ai_response, model_used)
        
        return True
    
    def load_from_drive(self):
        """Load conversations from Google Drive"""
        try:
            results = self.service.files().list(
                q=f"'{self.drive_folder_id}' in parents and name contains 'conversations'",
                spaces='drive',
                fields='files(id, name)',
                orderBy='createdTime desc',
                pageSize=1
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
    
    def save_local(self, user_message, ai_response, model_used):
        """Local backup"""
        try:
            local_file = 'conversations_local.pkl'
            conversations = []
            if os.path.exists(local_file):
                with open(local_file, 'rb') as f:
                    conversations = pickle.load(f)
            
            conversations.append({
                'timestamp': datetime.now().isoformat(),
                'user': user_message,
                'ai': ai_response,
                'model': model_used
            })
            
            with open(local_file, 'wb') as f:
                pickle.dump(conversations, f)
            print(f"💾 Saved locally ({len(conversations)} total)")
        except Exception as e:
            print(f"⚠️ Local save failed: {e}")
    
    def get_context(self, user_id=1, limit=5):
        """Get context from database for AI prompts"""
        try:
            convos = self.db.get_user_conversations(user_id, limit=1)
            if convos:
                messages = self.db.get_conversation_history(convos[0].id, limit=limit*2)
                context = "\n\n📝 Previous conversation:\n"
                for msg in messages[-limit*2:]:
                    role = "User" if msg.role == "user" else "Assistant"
                    context += f"{role}: {msg.content[:150]}\n\n"
                return context
        except:
            pass
        return ""

# Global instance
memory = HybridMemory()