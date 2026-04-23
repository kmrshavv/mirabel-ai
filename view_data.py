#!/usr/bin/env python3
import sqlite3

def view_all_data():
    conn = sqlite3.connect('mirabel.db')
    cursor = conn.cursor()
    
    print("\n" + "=" * 60)
    print("📊 MIRABEL AI - COMPLETE DATABASE VIEW")
    print("=" * 60)
    
    # Users
    print("\n👤 USERS:")
    cursor.execute("SELECT id, username, created_at FROM users")
    for row in cursor.fetchall():
        print(f"   [{row[0]}] {row[1]} - Joined: {row[2]}")
    
    # Conversations
    print("\n💬 CONVERSATIONS:")
    cursor.execute("""
        SELECT c.id, c.title, u.username, c.created_at, c.updated_at 
        FROM conversations c
        JOIN users u ON c.user_id = u.id
        ORDER BY c.id DESC
    """)
    for row in cursor.fetchall():
        print(f"   [{row[0]}] '{row[1]}' - User: {row[2]} - Updated: {row[4]}")
    
    # Messages
    print("\n📝 MESSAGES:")
    cursor.execute("""
        SELECT m.id, c.title, m.role, substr(m.content, 1, 60), m.created_at
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        ORDER BY m.id DESC
        LIMIT 10
    """)
    for row in cursor.fetchall():
        print(f"   [{row[0]}] Chat: {row[1]} | {row[2]}: {row[3]}...")
    
    conn.close()
    
    print("\n" + "=" * 60)
    print(f"✅ Total: {get_counts()}")
    print("=" * 60)

def get_counts():
    conn = sqlite3.connect('mirabel.db')
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM users")
    users = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM conversations")
    convs = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM messages")
    msgs = cursor.fetchone()[0]
    conn.close()
    return f"{users} Users, {convs} Conversations, {msgs} Messages"

if __name__ == "__main__":
    view_all_data()
