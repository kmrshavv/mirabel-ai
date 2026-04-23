#!/usr/bin/env python3
"""
Simple web server to view your database
Run: python3 web_viewer.py
Then open: http://localhost:5000
"""

import sqlite3
import json

# Try to import Flask
try:
    from flask import Flask, jsonify
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False
    print("⚠️ Flask not installed. Run: pip install flask")
    exit(1)

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect('mirabel.db')
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Mirabel AI - Database Viewer</title>
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Arial, sans-serif;
                background: linear-gradient(135deg, #0f0f1a 0%, #1a1a2e 100%);
                color: #eee;
                padding: 20px;
                min-height: 100vh;
            }
            .container { max-width: 1200px; margin: 0 auto; }
            h1 { 
                color: #8b5cf6; 
                font-size: 2.5rem;
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }
            .stat-card {
                background: rgba(30, 30, 50, 0.8);
                border-radius: 12px;
                padding: 20px;
                text-align: center;
                backdrop-filter: blur(10px);
                border: 1px solid rgba(139, 92, 246, 0.3);
            }
            .stat-number {
                font-size: 2.5rem;
                font-weight: bold;
                color: #8b5cf6;
            }
            .stat-label {
                color: #888;
                margin-top: 5px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                background: rgba(20, 20, 35, 0.9);
                border-radius: 12px;
                overflow: hidden;
                margin-top: 20px;
            }
            th, td {
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #333;
            }
            th {
                background: #8b5cf6;
                color: white;
                font-weight: 600;
            }
            tr:hover {
                background: rgba(139, 92, 246, 0.1);
            }
            .user-message { color: #3b82f6; }
            .assistant-message { color: #10b981; }
            .refresh-btn {
                background: #8b5cf6;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                color: white;
                cursor: pointer;
                margin: 20px 0;
                font-size: 16px;
            }
            .refresh-btn:hover { background: #7c3aed; }
            .footer {
                text-align: center;
                margin-top: 40px;
                padding: 20px;
                color: #666;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>
                <span>🤖</span>
                Mirabel AI - Database Viewer
            </h1>
            <p>View all conversations and messages stored in your database</p>
            
            <div class="stats" id="stats">
                <div class="stat-card">
                    <div class="stat-number" id="userCount">-</div>
                    <div class="stat-label">Users</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="convCount">-</div>
                    <div class="stat-label">Conversations</div>
                </div>
                <div class="stat-card">
                    <div class="stat-number" id="msgCount">-</div>
                    <div class="stat-label">Messages</div>
                </div>
            </div>
            
            <button class="refresh-btn" onclick="loadData()">🔄 Refresh</button>
            
            <h2>📝 Recent Messages</h2>
            <div id="messages">Loading...</div>
        </div>
        
        <div class="footer">
            Mirabel AI | Database Viewer | Powered by SQLite
        </div>
        
        <script>
            async function loadData() {
                try {
                    // Load stats
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();
                    document.getElementById('userCount').textContent = stats.users;
                    document.getElementById('convCount').textContent = stats.conversations;
                    document.getElementById('msgCount').textContent = stats.messages;
                    
                    // Load messages
                    const msgsRes = await fetch('/api/messages');
                    const messages = await msgsRes.json();
                    
                    let html = '<table><thead><tr><th>ID</th><th>Conversation</th><th>Role</th><th>Message</th><th>Time</th></tr></thead><tbody>';
                    
                    messages.forEach(msg => {
                        let roleClass = msg.role === 'user' ? 'user-message' : 'assistant-message';
                        let roleIcon = msg.role === 'user' ? '👤' : '🤖';
                        let preview = msg.content.length > 100 ? msg.content.substring(0, 100) + '...' : msg.content;
                        html += `<tr>
                            <td>${msg.id}</td>
                            <td>${msg.conversation_title || 'N/A'}</td>
                            <td class="${roleClass}">${roleIcon} ${msg.role}</td>
                            <td>${escapeHtml(preview)}</td>
                            <td>${msg.created_at ? msg.created_at.substring(0, 16) : 'Unknown'}</td>
                        </tr>`;
                    });
                    html += '</tbody></table>';
                    document.getElementById('messages').innerHTML = html;
                    
                } catch(e) {
                    document.getElementById('messages').innerHTML = '<p>Error loading data: ' + e.message + '</p>';
                }
            }
            
            function escapeHtml(text) {
                const div = document.createElement('div');
                div.textContent = text;
                return div.innerHTML();
            }
            
            loadData();
            setInterval(loadData, 10000);
        </script>
    </body>
    </html>
    """

@app.route('/api/messages')
def api_messages():
    conn = get_db()
    messages = conn.execute('''
        SELECT m.*, c.title as conversation_title 
        FROM messages m
        JOIN conversations c ON m.conversation_id = c.id
        ORDER BY m.id DESC 
        LIMIT 50
    ''').fetchall()
    conn.close()
    return jsonify([dict(m) for m in messages])

@app.route('/api/stats')
def api_stats():
    conn = get_db()
    users = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0]
    convs = conn.execute('SELECT COUNT(*) FROM conversations').fetchone()[0]
    msgs = conn.execute('SELECT COUNT(*) FROM messages').fetchone()[0]
    conn.close()
    return jsonify({'users': users, 'conversations': convs, 'messages': msgs})

@app.route('/api/users')
def api_users():
    conn = get_db()
    users = conn.execute('SELECT id, username, created_at FROM users').fetchall()
    conn.close()
    return jsonify([dict(u) for u in users])

if __name__ == '__main__':
    print("\n" + "=" * 50)
    print("🚀 Mirabel AI Database Viewer")
    print("=" * 50)
    print(f"📍 Open in browser: http://localhost:5000")
    print(f"📊 API endpoints:")
    print(f"   - http://localhost:5000/api/stats")
    print(f"   - http://localhost:5000/api/messages")
    print(f"   - http://localhost:5000/api/users")
    print("=" * 50)
    print("\nPress Ctrl+C to stop\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
