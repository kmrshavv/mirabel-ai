#!/usr/bin/env python3
import sqlite3
from datetime import datetime

conn = sqlite3.connect('mirabel.db')
cursor = conn.cursor()

print("\n" + "=" * 60)
print("📊 MIRABEL AI - DATABASE SUMMARY")
print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("=" * 60)

# User count
cursor.execute("SELECT COUNT(*) FROM users")
users = cursor.fetchone()[0]
print(f"\n👤 Total Users: {users}")

# Conversation count
cursor.execute("SELECT COUNT(*) FROM conversations")
conversations = cursor.fetchone()[0]
print(f"💬 Total Conversations: {conversations}")

# Message count
cursor.execute("SELECT COUNT(*) FROM messages")
messages = cursor.fetchone()[0]
print(f"📝 Total Messages: {messages}")

# Messages by role
cursor.execute("SELECT role, COUNT(*) FROM messages GROUP BY role")
for role, count in cursor.fetchall():
    print(f"   - {role}: {count} messages")

# Recent activity
cursor.execute("""
    SELECT MAX(created_at) FROM messages
""")
last_msg = cursor.fetchone()[0]
if last_msg:
    print(f"\n🕐 Last activity: {last_msg[:16]}")

# Database size
import os
size = os.path.getsize('mirabel.db')
print(f"\n💾 Database size: {size / 1024:.2f} KB")

# Table info
print("\n📋 Tables:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
for table in cursor.fetchall():
    cursor.execute(f"SELECT COUNT(*) FROM {table[0]}")
    count = cursor.fetchone()[0]
    print(f"   - {table[0]}: {count} rows")

conn.close()
print("\n" + "=" * 60)
print("✅ Database is healthy!")
print("=" * 60)
