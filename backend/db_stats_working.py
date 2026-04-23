#!/usr/bin/env python3
import sqlite3

def get_stats():
    conn = sqlite3.connect('mirabel.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 50)
    print("📊 MIRABEL AI DATABASE STATISTICS")
    print("=" * 50)
    
    # Get counts
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conversations = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM messages")
    messages = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM model_stats")
    model_stats = cursor.fetchone()[0]
    
    print(f"\n📈 TABLE COUNTS:")
    print(f"   👤 Users: {users}")
    print(f"   💬 Conversations: {conversations}")
    print(f"   📝 Messages: {messages}")
    print(f"   📊 Model Stats: {model_stats}")
    
    # Get last activity
    cursor.execute("SELECT MAX(created_at) FROM messages")
    last_msg = cursor.fetchone()[0]
    if last_msg:
        print(f"   🕐 Last Activity: {last_msg}")
    
    # Show users
    cursor.execute("SELECT id, username, created_at FROM users ORDER BY id DESC LIMIT 3")
    users_list = cursor.fetchall()
    if users_list:
        print(f"\n👥 RECENT USERS:")
        for u in users_list:
            print(f"   ID {u[0]}: {u[1]} (since {u[2]})")
    
    # Show recent conversations
    cursor.execute("""
        SELECT c.id, c.title, COUNT(m.id) as msg_count 
        FROM conversations c 
        LEFT JOIN messages m ON c.id = m.conversation_id 
        GROUP BY c.id 
        ORDER BY c.id DESC 
        LIMIT 3
    """)
    convs = cursor.fetchall()
    if convs:
        print(f"\n💬 RECENT CONVERSATIONS:")
        for c in convs:
            print(f"   Chat {c[0]}: '{c[1]}' - {c[2]} messages")
    
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Database is healthy!")
    print("=" * 50)

if __name__ == "__main__":
    get_stats()
