# test_memory.py - Test Google Drive Memory System
import os
import sys

print("🔧 Testing Mirabel Memory System...")

# Check if credentials file exists
credentials_path = 'credentials.json'
if os.path.exists(credentials_path):
    print(f"✅ Credentials found: {credentials_path}")
else:
    print(f"❌ Credentials NOT found at {credentials_path}")
    print("Please download the JSON key from Google Cloud Console and save as 'credentials.json'")
    sys.exit(1)

# Import memory module
try:
    from memory import memory
    print("✅ Memory module imported successfully")
except ImportError as e:
    print(f"❌ Could not import memory module: {e}")
    print("Make sure memory.py exists in the current directory")
    sys.exit(1)

# Test saving a conversation
try:
    print("\n📝 Testing conversation save...")
    memory.save_conversation(
        user_message="Hello! This is a test message from the setup script.",
        ai_response="Hi there! This is a test response from Mirabel AI. The memory system is working perfectly! 🎉",
        model_used="llama3.2:3b"
    )
    print("✅ Conversation saved successfully!")
    
    # Test loading conversations
    print("\n📚 Testing conversation load...")
    conversations = memory.load_conversations()
    if conversations:
        print(f"✅ Loaded {len(conversations)} conversation(s)")
        print(f"   Last conversation: {conversations[-1]['timestamp'][:16]}")
    else:
        print("⚠️ No conversations loaded yet (this is normal for first run)")
    
    print("\n🎉 Memory system test complete!")
    print("📁 Check your Google Drive → 'Mirabel_Memory' folder")
    print("   You should see a file named 'conversations_YYYYMMDD.pkl'")
    
except Exception as e:
    print(f"❌ Test failed: {e}")
    import traceback
    traceback.print_exc()