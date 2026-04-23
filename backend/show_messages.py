#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('mirabel.db')
cursor = conn.cursor()

print("\n" + "=" * 60)
print("📝 ALL MESSAGES")
print("=" * 60)

cursor.execute("""
    SELECT 
        m.id,
        c.title as conversation,
        u.username as user,
        m.role,
        m.content,
        datetime(m.created_at, 'localtime') as local_time
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    JOIN users u ON c.user_id = u.id
    ORDER BY m.id
""")

for row in cursor.fetchall():
    msg_id, conv_title, username, role, content, timestamp = row
    icon = "👤" if role == "user" else "🤖"
    print(f"\n[{msg_id}] {conv_title} - {username}")
    print(f"   {icon} {role.capitalize()}: {content}")
    print(f"   🕐 {timestamp if timestamp else 'Unknown'}")

conn.close()
print("\n" + "=" * 60)
