#!/usr/bin/env python3
"""
Fixed web server to view your database
Run: python3 web_viewer_fixed.py
Then open: http://localhost:5000
"""

import sqlite3
from flask import Flask, jsonify

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
            .loading {
                text-align: center;
                padding: 40px;
                color: #888;
            }
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
            <div id="messages" class="loading">Loading...</div>
        </div>
        
        <div class="footer">
            Mirabel AI | Database Viewer | Powered by SQLite
        </div>
        
        <script>
            function escapeHtml(str) {
                if (!str) return '';
                return str
                    .replace(/&/g, '&amp;')
                    .replace(/</g, '&lt;')
                    .replace(/>/g, '&gt;')
                    .replace(/"/g, '&quot;')
                    .replace(/'/g, '&#39;');
            }
            
            async function loadData() {
                try {
                    // Load stats
                    const statsRes = await fetch('/api/stats');
                    const stats = await statsRes.json();
                    document.getElementById('userCount').textContent = stats.users || 0;
                    document.getElementById('convCount').textContent = stats.conversations || 0;
                    document.getElementById('msgCount').textContent = stats.messages || 0;
                    
                    // Load messages
                    const msgsRes = await fetch('/api/messages');
                    const messages = await msgsRes.json();
                    
                    if (!messages || messages.length === 0) {
                        document.getElementById('messages').innerHTML = '<div class="loading">No messages found</div>';
                        return;
                    }
                    
                    let html = '<table><thead><tr>' +
                        '<th>ID</th>' +
                        '<th>Conversation</th>' +
                        '<th>Role</th>' +
                        '<th>Message</th>' +
                        '<th>Time</th>' +
                        '</tr></thead><tbody>';
                    
                    for (let i = 0; i < messages.length; i++) {
                        const msg = messages[i];
                        const roleClass = msg.role === 'user' ? 'user-message' : 'assistant-message';
                        const roleIcon = msg.role === 'user' ? '👤' : '🤖';
                        let preview = msg.content;
                        if (preview && preview.length > 100) {
                            preview = preview.substring(0, 100) + '...';
                        }
                        const convTitle = msg.conversation_title || 'N/A';
                        const timestamp = msg.created_at ? msg.created_at.substring(0, 16) : 'Unknown';
                        
                        html += '<tr>' +
                            '<td>' + (msg.id || '-') + '</td>' +
                            '<td>' + escapeHtml(convTitle) + '</td>' +
                            '<td class="' + roleClass + '">' + roleIcon + ' ' + (msg.role || 'unknown') + '</td>' +
                            '<td>' + escapeHtml(preview || '') + '</td>' +
                            '<td>' + escapeHtml(timestamp) + '</td>' +
                            '</tr>';
                    }
                    html += '</tbody></table>';
                    document.getElementById('messages').innerHTML = html;
                    
                } catch(e) {
                    console.error('Error:', e);
                    document.getElementById('messages').innerHTML = '<div class="loading">Error loading data: ' + e.message + '</div>';
                }
            }
            
            // Load data on page load
            loadData();
            // Refresh every 10 seconds
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
