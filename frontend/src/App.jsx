// src/App.jsx
import { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import { Send, Zap } from 'lucide-react';
import Message from './components/Message';
import ModelSelector from './components/ModelSelector';
import TypingIndicator from './components/TypingIndicator';

// API Configuration
const API_URL = 'http://localhost:8000';

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
        await axios.get(`${API_URL}/health`);
        setConnectionStatus('connected');
        // Add welcome message
        setMessages([
          {
            text: "✨ Hello! I'm Mirabel, your emotionally intelligent AI assistant. I can help you with coding, research, document analysis, or just chat. How can I make your day better?",
            isUser: false,
            modelUsed: selectedModel,
            timestamp: new Date().toISOString(),
          },
        ]);
      } catch (error) {
        setConnectionStatus('disconnected');
        setMessages([
          {
            text: "⚠️ Cannot connect to backend. Please make sure your FastAPI server is running on port 8000. Run: `cd ~/mirabel-ai/backend && uvicorn app:app --reload`",
            isUser: false,
            modelUsed: 'error',
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
        modelUsed: response.data.model_used || selectedModel,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, aiMessage]);
      
      // Log which model was used (for debugging)
      if (response.data.detected_task) {
        console.log(`Task detected: ${response.data.detected_task}`);
      }
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        text: `❌ Error: ${error.response?.data?.detail || error.message || 'Something went wrong'}\n\nMake sure your backend is running!`,
        isUser: false,
        modelUsed: 'error',
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
          </div>
        </div>
        
        {/* Model Selector */}
        <div className="p-4">
          <ModelSelector selectedModel={selectedModel} onModelChange={setSelectedModel} />
        </div>
        
        {/* Info Panel */}
        <div className="flex-1 p-4 text-xs text-gray-500">
          <div className="border-t border-gray-800 pt-4">
            <p className="mb-2">✨ <strong>Features:</strong></p>
            <ul className="space-y-1">
              <li>• 5 specialized AI models</li>
              <li>• Emotional intelligence</li>
              <li>• Code generation & review</li>
              <li>• Research assistance</li>
              <li>• Document analysis</li>
            </ul>
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
                modelUsed={msg.modelUsed}
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
                placeholder="Type your message... (Shift+Enter for new line)"
                className="flex-1 bg-gray-800 text-white rounded-lg px-4 py-2 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
                rows="1"
                disabled={isLoading || connectionStatus === 'disconnected'}
              />
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading || connectionStatus === 'disconnected'}
                className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded-lg px-4 py-2 transition-colors"
              >
                <Send className="w-5 h-5" />
              </button>
            </div>
            <div className="text-xs text-gray-500 mt-2">
              {selectedModel === 'qwen2.5-coder:14b' && '💻 Coder mode active - I will generate clean, error-checked code'}
              {selectedModel === 'llama3.2:3b' && '❤️ Emotional mode active - I will respond with empathy and warmth'}
              {selectedModel === 'mistral:7b' && '🔍 Research mode active - I will find accurate information'}
              {selectedModel === 'granite3-dense:8b' && '📄 Document mode active - I can analyze long texts'}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;