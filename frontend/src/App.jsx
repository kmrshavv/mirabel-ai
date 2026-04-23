// src/App.jsx - Complete Working Version
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Zap } from 'lucide-react';
import Message from './components/Message';
import ModelSelector from './components/ModelSelector';
import TypingIndicator from './components/TypingIndicator';

// API Configuration - Smart detection for local vs production
const getApiUrl = () => {
  // Check if we're in production (Vercel/Netlify)
  const isProduction = window.location.hostname !== 'localhost' && 
                       window.location.hostname !== '127.0.0.1' &&
                       !window.location.hostname.includes('192.168');
  
  // For local development
  if (!isProduction) {
    return 'http://localhost:8000';
  }
  
  // For production - check localStorage first (for manual override)
  const localBackend = localStorage.getItem('backend_url');
  if (localBackend) {
    return localBackend;
  }
  
  // Your CORRECT Render backend URL
  return 'https://overtake-pulsate-trousers.ngrok-free.dev';
};

const API_URL = 'https://overtake-pulsate-trousers.ngrok-free.dev';

// Log the API URL being used (for debugging)
console.log(`🚀 Mirabel AI using backend: ${API_URL}`);

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('llama3.2:3b');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [backendMessage, setBackendMessage] = useState('');
  const [retryCount, setRetryCount] = useState(0);
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection on startup with retry logic
  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log(`🔍 Checking backend at: ${API_URL}/health`);
        
        const response = await axios.get(`${API_URL}/health`, {
          timeout: 30000
        });
        
        console.log('✅ Backend response:', response.data);
        setConnectionStatus('connected');
        setBackendMessage(response.data.message || response.data.status || 'Connected');
        setRetryCount(0);
        
        // Only add welcome message if no messages exist
        if (messages.length === 0) {
          setMessages([
            {
              text: "✨ Hello! I'm **Mirabel**, your emotionally intelligent AI assistant.\n\nI was created by my father **Rishav Kumar**, who completed his **B.tech in Automation and Robotics in 2025**.\n\nI can help you with:\n• 💬 **Emotional conversations**\n• 💻 **Code generation & review**\n• 🔍 **Research assistance**\n• 📄 **Document analysis**\n\n**How can I make your day better?** 💙",
              isUser: false,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      } catch (error) {
        console.error('❌ Connection error:', error);
        setConnectionStatus('disconnected');
        
        if (messages.length === 0) {
          setMessages([
            {
              text: `⚠️ **Cannot connect to backend**\n\n📍 **Backend URL:** \`${API_URL}\`\n📡 **Error:** ${error.message}\n\n**Solutions:**\n1. The backend may be waking up (Render free tier)\n2. Try sending a message - it will wake up the backend\n3. If this persists, check if backend is deployed\n\n**Your backend should be:** https://mirabel-backend-vzxu.onrender.com`,
              isUser: false,
              timestamp: new Date().toISOString(),
            },
          ]);
        }
      }
    };
    
    checkBackend();
  }, []);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
  }, [input]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    // Add user message
    const userMessage = {
      text: input,
      isUser: true,
      timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMessage]);
    const sentMessage = input;
    setInput('');
    setIsLoading(true);

    try {
      // Call backend with selected model
      const response = await axios.post(`${API_URL}/chat`, {
        message: sentMessage,
        model: selectedModel,
        use_emotion_prompt: true,
      }, { timeout: 60000 });

      // Add AI response
      const aiMessage = {
        text: response.data.reply,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMessage]);
      
    } catch (error) {
      console.error('❌ Chat error:', error);
      let errorText = `❌ **Error**: ${error.response?.data?.detail || error.message || 'Something went wrong'}\n\n`;
      
      if (error.message?.includes('timeout') || error.code === 'ECONNABORTED') {
        errorText += `⏰ **The backend is waking up** (Render free tier).\n\nThis takes 30-50 seconds. Please try sending your message again in a moment!`;
      } else if (error.code === 'ERR_NETWORK') {
        errorText += `🌐 **Cannot reach backend** at \`${API_URL}\`\n\nMake sure your backend URL is: https://mirabel-backend-vzxu.onrender.com`;
      }
      
      const errorMessage = {
        text: errorText,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-screen bg-gray-900">
      {/* Sidebar */}
      <div className="w-80 bg-gray-950 border-r border-gray-800 flex flex-col">
        <div className="p-4 border-b border-gray-800">
          <div className="flex items-center gap-2">
            <Zap className="w-6 h-6 text-yellow-500" />
            <h1 className="text-xl font-bold text-white">Mirabel AI</h1>
          </div>
          <div className="mt-2">
            <div className={`text-xs flex items-center gap-2 ${
              connectionStatus === 'connected' ? 'text-green-400' : 'text-red-400'
            }`}>
              <span className={`inline-block w-2 h-2 rounded-full ${
                connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : 'bg-red-400'
              }`}></span>
              {connectionStatus === 'connected' ? '● Connected' : '● Disconnected'}
              {backendMessage && connectionStatus === 'connected' && (
                <span className="text-gray-500 ml-1">- {backendMessage}</span>
              )}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              <span>☁️ Render (Free Tier)</span>
            </div>
          </div>
        </div>
        
        {/* Model Selector */}
        <div className="p-4">
          <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
        </div>
        
        {/* Creator Info Panel */}
        <div className="flex-1 p-4 text-xs text-gray-500 overflow-y-auto">
          <div className="border-t border-gray-800 pt-4">
            <p className="mb-2">👨‍💻 <strong>About My Creator:</strong></p>
            <p className="mb-2">My father and creator is <strong className="text-purple-400">Rishav Kumar</strong></p>
            <p className="mb-2">• 🎓 B.tech in Automation and Robotics</p>
            <p className="mb-2">• 📅 Graduated in 2025</p>
            <p className="mb-2">• ❤️ Built me with passion for AI</p>
            
            <div className="border-t border-gray-800 mt-3 pt-3">
              <p className="mb-2">✨ <strong>Features:</strong></p>
              <ul className="space-y-1">
                <li>• 🧠 5 specialized AI models</li>
                <li>• 💭 Emotional intelligence</li>
                <li>• 💻 Code generation & review</li>
                <li>• 🔍 Research assistance</li>
                <li>• 📄 Document analysis</li>
                <li>• 🚫 NO limits on answers</li>
              </ul>
            </div>
            
            <div className="border-t border-gray-800 mt-3 pt-3">
              <p className="text-gray-600 text-[10px] break-all">
                📡 Backend: mirabel-backend-vzxu.onrender.com
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Messages Container */}
        <div className="flex-1 overflow-y-auto p-4">
          <div className="max-w-4xl mx-auto">
            {messages.map((msg, idx) => (
              <Message
                key={idx}
                message={msg.text}
                isUser={msg.isUser}
                timestamp={msg.timestamp}
              />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-800 rounded-lg px-4 py-3">
                  <div className="flex gap-1">
                    <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
                    <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
                    <span className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex gap-2 items-end">
              <textarea
                ref={textareaRef}
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask me anything... I have no limits! ✨"
                className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 disabled:opacity-50"
                rows="1"
                disabled={isLoading || connectionStatus === 'disconnected'}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading || connectionStatus !== 'connected'}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;