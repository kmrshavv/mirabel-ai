cd ~/Desktop/mirabel-ai/backend

cat > show_data.py << 'EOF'
#!/usr/bin/env python3
import sqlite3

print("\n" + "=" * 60)
print("📊 MIRABEL AI DATABASE DATA")
print("=" * 60)

conn = sqlite3.connect('mirabel.db')
cursor = conn.cursor()

# Show all tables
print("\n📋 TABLES IN DATABASE:")
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
for table in tables:
    print(f"   ✅ {table[0]}")

# Show users
print("\n👤 USERS:")
users = cursor.execute("SELECT * FROM users").fetchall()
if users:
    for user in users:
        print(f"   ID: {user[0]}, Username: {user[1]}, Created: {user[2]}")
else:
    print("   No users found")

# Show conversations
print("\n💬 CONVERSATIONS:")
convs = cursor.execute("SELECT * FROM conversations").fetchall()
if convs:
    for conv in convs:
        print(f"   ID: {conv[0]}, User: {conv[1]}, Title: {conv[2]}, Created: {conv[3]}")
else:
    print("   No conversations found")

# Show messages (last 10)
print("\n📝 LAST 10 MESSAGES:")
msgs = cursor.execute("""
    SELECT m.id, c.title, m.role, substr(m.content, 1, 50), m.created_at 
    FROM messages m
    JOIN conversations c ON m.conversation_id = c.id
    ORDER BY m.id DESC LIMIT 10
""").fetchall()
if msgs:
    for msg in msgs:
        print(f"   [{msg[0]}] {msg[1]} | {msg[2]}: {msg[3]}...")
else:
    print("   No messages found")

# Statistics
print("\n📈 STATISTICS:")
stats = cursor.execute("""
    SELECT 
        (SELECT COUNT(*) FROM users) as users,
        (SELECT COUNT(*) FROM conversations) as conversations,
        (SELECT COUNT(*) FROM messages) as messages
""").fetchone()
print(f"   👤 Users: {stats[0]}")
print(f"   💬 Conversations: {stats[1]}")
print(f"   📝 Messages: {stats[2]}")

conn.close()
print("\n" + "=" * 60)
EOF

python3 show_data.py