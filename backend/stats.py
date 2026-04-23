from database_simple import db

stats = db.get_stats()
print(f"👤 Users: {stats['users']}")
print(f"💬 Conversations: {stats['conversations']}")
print(f"📝 Messages: {stats['messages']}")
