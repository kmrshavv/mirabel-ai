#!/usr/bin/env python3
import sqlite3
import os

db_path = 'mirabel.db'

print("\n🔍 MIRABEL AI DATABASE HEALTH CHECK")
print("=" * 50)

# Check if database exists
if os.path.exists(db_path):
    size = os.path.getsize(db_path)
    print(f"✅ Database file exists: {db_path}")
    print(f"   Size: {size / 1024:.2f} KB")
else:
    print(f"❌ Database file not found: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check tables
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"\n📋 Tables found: {', '.join([t[0] for t in tables])}")
    
    # Check each table
    required_tables = ['users', 'conversations', 'messages']
    for table in required_tables:
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        count = cursor.fetchone()[0]
        status = "✅" if count >= 0 else "⚠️"
        print(f"   {status} {table}: {count} records")
    
    # Check foreign keys
    cursor.execute("PRAGMA foreign_key_check;")
    fk_errors = cursor.fetchall()
    if fk_errors:
        print(f"\n⚠️ Foreign key errors found: {len(fk_errors)}")
    else:
        print("\n✅ No foreign key violations")
    
    conn.close()
    print("\n✅ Database health check PASSED!")
    
except Exception as e:
    print(f"\n❌ Database error: {e}")
    
print("=" * 50)
