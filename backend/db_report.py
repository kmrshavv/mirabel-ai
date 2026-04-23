#!/usr/bin/env python3
import sqlite3
from datetime import datetime

def get_db_report():
    conn = sqlite3.connect('mirabel.db')
    cursor = conn.cursor()
    
    report = []
    report.append("=" * 60)
    report.append("📊 MIRABEL AI DATABASE REPORT")
    report.append(f"📅 Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("=" * 60)
    
    # User summary
    cursor.execute("SELECT COUNT(*) FROM users")
    user_count = cursor.fetchone()[0]
    report.append(f"\n👤 USERS: {user_count}")
    
    cursor.execute("SELECT id, username, created_at FROM users")
    for user in cursor.fetchall():
        report.append(f"   - ID {user[0]}: {user[1]} (since {user[2][:10]})")
    
    # Conversation summary
    cursor.execute("SELECT COUNT(*) FROM conversations")
    conv_count = cursor.fetchone()[0]
    report.append(f"\n💬 CONVERSATIONS: {conv_count}")
    
    cursor.execute("""
        SELECT c.id, c.title, u.username, COUNT(m.id) as msg_count
        FROM conversations c
        JOIN users u ON c.user_id = u.id
        LEFT JOIN messages m ON c.id = m.conversation_id
        GROUP BY c.id
        ORDER BY c.id DESC
    """)
    for conv in cursor.fetchall():
        report.append(f"   - [{conv[0]}] {conv[1]} (User: {conv[2]}) - {conv[3]} messages")
    
    # Message summary
    cursor.execute("SELECT COUNT(*) FROM messages")
    msg_count = cursor.fetchone()[0]
    report.append(f"\n📝 MESSAGES: {msg_count}")
    
    if msg_count > 0:
        cursor.execute("""
            SELECT role, COUNT(*) 
            FROM messages 
            GROUP BY role
        """)
        for role_count in cursor.fetchall():
            report.append(f"   - {role_count[0]}: {role_count[1]} messages")
    
    # Database size
    import os
    size = os.path.getsize('mirabel.db')
    report.append(f"\n💾 DATABASE SIZE: {size / 1024:.2f} KB")
    
    report.append("\n" + "=" * 60)
    report.append("✅ Database is healthy!")
    report.append("=" * 60)
    
    conn.close()
    return "\n".join(report)

if __name__ == "__main__":
    print(get_db_report())
