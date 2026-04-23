#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('mirabel.db')
cursor = conn.cursor()

print("\n" + "=" * 60)
print("📝 MIRABEL AI - CONVERSATION HISTORY")
print("=" * 60)

# Get all conversations
cursor.execute("""
    SELECT c.id, c.title, u.username, COUNT(m.id) as msg_count
    FROM conversations c
    JOIN users u ON c.user_id = u.id
    LEFT JOIN messages m ON c.id = m.conversation_id
    GROUP BY c.id
    ORDER BY c.id
""")

conversations = cursor.fetchall()

for conv in conversations:
    conv_id, title, username, msg_count = conv
    print(f"\n💬 Conversation {conv_id}: {title}")
    print(f"   User: {username} | Messages: {msg_count}")
    print("   " + "-" * 50)
    
    # Get messages for this conversation
    cursor.execute("""
        SELECT role, content, created_at
        FROM messages
        WHERE conversation_id = ?
        ORDER BY id
    """, (conv_id,))
    
    messages = cursor.fetchall()
    for role, content, timestamp in messages:
        icon = "👤" if role == "user" else "🤖"
        # Truncate long messages
        if len(content) > 80:
            content = content[:77] + "..."
        print(f"   {icon} {role.capitalize()}: {content}")
        # Handle None timestamp
        if timestamp:
            print(f"      📅 {timestamp[:16]}")
        else:
            print(f"      📅 Unknown time")
    print()

conn.close()
print("=" * 60)
