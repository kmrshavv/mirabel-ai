// src/App.jsx - Updated for Production Deployment
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Zap } from 'lucide-react';
import Message from './components/Message';
import ModelSelector from './components/ModelSelector';
import TypingIndicator from './components/TypingIndicator';

// API Configuration - Automatically switches between local and production
const API_URL = process.env.NODE_ENV === 'production' 
  ? 'https://mirabel-backend.onrender.com'  // Replace with your Render URL after deployment
  : 'http://localhost:8000';

// For testing, you can also manually set it:
// const API_URL = 'https://mirabel-backend.onrender.com';

function App() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('llama3.2:3b');
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const messagesEndRef = useRef(null);
  const textareaRef = useRef(null);

  // Auto-scroll to latest message
  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  // Check backend connection on startup
  useEffect(() => {
    const checkBackend = async () => {
      try {
        console.log(`Checking backend at: ${API_URL}/health`);
        const response = await axios.get(`${API_URL}/health`);
        console.log('Backend response:', response.data);
        setConnectionStatus('connected');
        
        // Add welcome message with creator info
        setMessages([
          {
            text: "✨ Hello! I'm Mirabel, your emotionally intelligent AI assistant. I was created by my father Rishav Kumar, who completed his B.tech in Automation and Robotics in 2025. I can help you with coding, research, document analysis, or just chat. How can I make your day better?",
            isUser: false,
            timestamp: new Date().toISOString(),
          },
        ]);
      } catch (error) {
        console.error('Connection error:', error);
        setConnectionStatus('disconnected');
        setMessages([
          {
            text: `⚠️ Cannot connect to backend at ${API_URL}\n\nError: ${error.message}\n\nMake sure your FastAPI server is running locally or deployed on Render.`,
            isUser: false,
            timestamp: new Date().toISOString(),
          },
        ]);
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
    setInput('');
    setIsLoading(true);

    try {
      // Call backend with selected model
      const response = await axios.post(`${API_URL}/chat`, {
        message: input,
        model: selectedModel,
        use_emotion_prompt: true,
      });

      // Add AI response
      const aiMessage = {
        text: response.data.reply,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Log which model was used (for debugging)
      if (response.data.detected_task) {
        console.log(`Task detected: ${response.data.detected_task}`);
      }
      if (response.data.creator) {
        console.log(`Creator: ${response.data.creator}`);
      }
    } catch (error) {
      console.error('Error:', error);
      let errorText = `❌ Error: ${error.response?.data?.detail || error.message || 'Something went wrong'}\n\n`;
      
      if (error.code === 'ERR_NETWORK') {
        errorText += `Cannot reach backend at ${API_URL}\n\n`;
        errorText += `Solutions:\n`;
        errorText += `1. For local development: Make sure backend is running on port 8000\n`;
        errorText += `2. For production: Check if Render service is deployed\n`;
        errorText += `3. Wait 30 seconds - Render free tier takes time to wake up`;
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
            <div className={`text-xs ${
              connectionStatus === 'connected' ? 'text-green-400' : 'text-red-400'
            }`}>
              {connectionStatus === 'connected' ? '● Connected' : '● Disconnected'}
            </div>
            <div className="text-xs text-gray-500 mt-1">
              {API_URL !== 'http://localhost:8000' && `🌐 Live: ${API_URL}`}
            </div>
          </div>
        </div>
        
        {/* Model Selector */}
        <div className="p-4">
          <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
        </div>
        
        {/* Creator Info Panel */}
        <div className="flex-1 p-4 text-xs text-gray-500">
          <div className="border-t border-gray-800 pt-4">
            <p className="mb-2">👨‍💻 <strong>About My Creator:</strong></p>
            <p className="mb-2">My father and creator is <strong className="text-purple-400">Rishav Kumar</strong></p>
            <p className="mb-2">• B.tech in Automation and Robotics</p>
            <p className="mb-2">• Graduated in 2025</p>
            <div className="border-t border-gray-800 mt-2 pt-2">
              <p className="mb-2">✨ <strong>Features:</strong></p>
              <ul className="space-y-1">
                <li>• 5 specialized AI models</li>
                <li>• Emotional intelligence</li>
                <li>• Code generation & review</li>
                <li>• Research assistance</li>
                <li>• Document analysis</li>
                <li>• NO limits on answers</li>
              </ul>
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
            {isLoading && <TypingIndicator />}
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
                placeholder="Ask me anything... I have no limits! (Shift+Enter for new line)"
                className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500"
                rows="1"
                disabled={isLoading || connectionStatus === 'disconnected'}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading || connectionStatus === 'disconnected'}
                className="bg-purple-600 hover:bg-purple-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {selectedModel === 'qwen2.5-coder:14b' && '💻 Coder mode active - Generating clean, error-checked code'}
              {selectedModel === 'llama3.2:3b' && '❤️ Emotional mode active - Responding with empathy and warmth. Ask me about my creator Rishav Kumar!'}
              {selectedModel === 'mistral:7b' && '🔍 Research mode active - Finding accurate information'}
              {selectedModel === 'granite3-dense:8b' && '📄 Document mode active - Analyzing long texts'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;