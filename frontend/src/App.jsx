// App.jsx - Universal Chat App (Colab + ngrok + Local)
import { useState, useRef, useEffect, useCallback } from 'react';
import axios from 'axios';
import { 
  Send, Zap, Menu, X, Heart, Code, BookOpen, FileText, 
  User, Bot, Server, Cloud, ChevronDown, Circle, Sparkles,
  Settings, Wifi, WifiOff, Database, Cpu, Globe, Loader2,
  Moon, Sun, Trash2, Copy, Check, RefreshCw, MessageSquare,
  Plus, ChevronLeft, MoreVertical, Mic, MicOff
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';

// ===== CONFIGURATION =====
// Backend URLs - Update these based on your Colab/ngrok output
const DEFAULT_NGROK_URL = "https://overtake-pulsate-trousers.ngrok-free.dev";
const DEFAULT_COLAB_URL = "https://8000-m-s-kkb-usw4a2-v0opxp071j1v-a.us-west4-2.prod.colab.dev/"; // Will be auto-detected or user can set
const LOCAL_URL = 'http://localhost:8000';

// Model configurations
const MODELS = [
  { 
    id: 'llama3.2:1b', 
    name: 'Mirabel', 
    icon: Heart, 
    color: 'pink', 
    description: 'Emotional & Caring',
    gradient: 'from-pink-500 to-rose-500',
    badge: '❤️ Empathetic',
    role: 'emotional'
  },
  { 
    id: 'mistral:7b', 
    name: 'Researcher', 
    icon: BookOpen, 
    color: 'green', 
    description: 'Knowledge & Facts',
    gradient: 'from-green-500 to-emerald-500',
    badge: '📚 Academic',
    role: 'researcher'
  },
  { 
    id: 'phi3:mini', 
    name: 'Analyst', 
    icon: FileText, 
    color: 'purple', 
    description: 'Document Analysis',
    gradient: 'from-purple-500 to-violet-500',
    badge: '📊 Data',
    role: 'document'
  },
];

// Backend types
const BACKEND_TYPES = {
  LOCAL: 'local',
  NGROK: 'ngrok',
  COLAB: 'colab'
};

// Helper function to get the backend URL
const getBackendUrl = (backendType, customUrl = null) => {
  if (customUrl && customUrl.trim() !== '') {
    return customUrl;
  }
  
  switch(backendType) {
    case BACKEND_TYPES.LOCAL:
      return LOCAL_URL;
    case BACKEND_TYPES.NGROK:
      return DEFAULT_NGROK_URL;
    case BACKEND_TYPES.COLAB:
      // Try to get from localStorage first
      const saved = localStorage.getItem('mirabel_colab_url');
      if (saved && saved !== 'undefined' && saved !== 'null') {
        return saved;
      }
      return DEFAULT_COLAB_URL;
    default:
      return LOCAL_URL;
  }
};

// Code block component for syntax highlighting
const CodeBlock = ({ language, children }) => {
  return (
    <SyntaxHighlighter
      language={language || 'javascript'}
      style={vscDarkPlus}
      customStyle={{
        borderRadius: '8px',
        fontSize: '12px',
        margin: '8px 0',
      }}
    >
      {String(children).replace(/\n$/, '')}
    </SyntaxHighlighter>
  );
};

function App() {
  // State
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('llama3.2:1b');
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  const [backendType, setBackendType] = useState(BACKEND_TYPES.NGROK);
  const [connectionStatus, setConnectionStatus] = useState('checking');
  const [backendMessage, setBackendMessage] = useState('');
  const [copiedMessageId, setCopiedMessageId] = useState(null);
  const [darkMode, setDarkMode] = useState(true);
  const [isRecording, setIsRecording] = useState(false);
  const [conversations, setConversations] = useState([]);
  const [currentConvId, setCurrentConvId] = useState(null);
  const [customUrl, setCustomUrl] = useState('');
  const [isEditingUrl, setIsEditingUrl] = useState(false);
  const [tempUrl, setTempUrl] = useState('');
  const [backendInfo, setBackendInfo] = useState({});
  
  // Refs
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);
  const recognitionRef = useRef(null);

  // Scroll to bottom
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Load saved data from localStorage
  useEffect(() => {
    // Load conversations
    const saved = localStorage.getItem('mirabel_conversations');
    if (saved) {
      try {
        const parsed = JSON.parse(saved);
        setConversations(parsed);
        if (parsed.length > 0 && !currentConvId) {
          setCurrentConvId(parsed[0].id);
          setMessages(parsed[0].messages);
        }
      } catch (e) {}
    }
    
    // Load saved backend preference
    const savedBackend = localStorage.getItem('mirabel_backend_type');
    if (savedBackend && Object.values(BACKEND_TYPES).includes(savedBackend)) {
      setBackendType(savedBackend);
    }
    
    // Load saved custom URL
    const savedUrl = localStorage.getItem('mirabel_custom_url');
    if (savedUrl) {
      setCustomUrl(savedUrl);
    }
  }, []);

  // Save preferences to localStorage
  useEffect(() => {
    localStorage.setItem('mirabel_backend_type', backendType);
  }, [backendType]);
  
  useEffect(() => {
    if (customUrl) {
      localStorage.setItem('mirabel_custom_url', customUrl);
    }
  }, [customUrl]);

  // Save conversations to localStorage
  useEffect(() => {
    if (conversations.length > 0) {
      localStorage.setItem('mirabel_conversations', JSON.stringify(conversations));
    }
  }, [conversations]);

  // Get API URL based on selected backend
  const getApiUrl = useCallback(() => {
    if (backendType === BACKEND_TYPES.LOCAL) {
      return LOCAL_URL;
    }
    return getBackendUrl(backendType, customUrl);
  }, [backendType, customUrl]);

  // Get backend display name
  const getBackendDisplayName = () => {
    switch(backendType) {
      case BACKEND_TYPES.LOCAL: return 'Local';
      case BACKEND_TYPES.NGROK: return 'ngrok';
      case BACKEND_TYPES.COLAB: return 'Colab';
      default: return 'Unknown';
    }
  };

  // Get backend icon
  const getBackendIcon = () => {
    switch(backendType) {
      case BACKEND_TYPES.LOCAL: return <Server className="w-4 h-4" />;
      case BACKEND_TYPES.NGROK: return <Cloud className="w-4 h-4" />;
      case BACKEND_TYPES.COLAB: return <Database className="w-4 h-4" />;
      default: return <Server className="w-4 h-4" />;
    }
  };

  // Check backend connection
  const checkBackend = useCallback(async () => {
    const apiUrl = getApiUrl();
    
    if (!apiUrl || apiUrl === '') {
      setConnectionStatus('disconnected');
      setBackendMessage(`No URL configured for ${getBackendDisplayName()}`);
      return;
    }
    
    console.log(`🔍 Checking ${backendType} backend at: ${apiUrl}`);
    console.log(`📡 Full API URL: ${apiUrl}/health`);
    
    try {
      const response = await axios.get(`${apiUrl}/health`, { 
        timeout: 15000,
        headers: { 
          'Accept': 'application/json',
          'Content-Type': 'application/json'
        }
      });
      
      console.log('Response:', response.status, response.data);
      
      if (response.data && (response.data.status === 'healthy' || response.status === 200)) {
        setConnectionStatus('connected');
        setBackendMessage(`${getBackendDisplayName()} ready`);
        setBackendInfo(response.data);
        
        // Show welcome message if no messages exist
        if (messages.length === 0 && !currentConvId) {
          const welcomeMsg = {
            id: Date.now(),
            text: `✨ **Mirabel AI** is ready!\n\n📍 **Backend:** ${getBackendDisplayName()}\n🔗 **URL:** ${apiUrl}\n💙 Created by **Rishav Kumar** — B.Tech in Automation & Robotics (2025)\n\n**✅ Connection Successful!**\n\n**How can I help you today?**`,
            isUser: false,
            timestamp: new Date().toISOString(),
            model: selectedModel,
          };
          setMessages([welcomeMsg]);
          
          const newConv = {
            id: Date.now(),
            title: 'New Conversation',
            messages: [welcomeMsg],
            createdAt: new Date().toISOString(),
          };
          setConversations([newConv]);
          setCurrentConvId(newConv.id);
        }
      } else {
        throw new Error('Invalid response from server');
      }
    } catch (error) {
      console.error('Connection error:', error);
      
      setConnectionStatus('disconnected');
      
      let errorMessage = '';
      if (error.code === 'ECONNABORTED') {
        errorMessage = 'Connection timeout';
      } else if (error.code === 'ERR_NETWORK') {
        errorMessage = 'Network error - Cannot reach server';
      } else if (error.response?.status === 404) {
        errorMessage = 'Endpoint not found';
      } else if (error.response?.status === 500) {
        errorMessage = 'Server error';
      } else {
        errorMessage = error.message || 'Connection failed';
      }
      
      setBackendMessage(`${getBackendDisplayName()} offline: ${errorMessage}`);
      
      // Show connection error message if no messages
      if (messages.length === 0) {
        setMessages([{
          id: Date.now(),
          text: `⚠️ **Backend Connection Issue**

**Backend:** ${getBackendDisplayName()}
**URL:** \`${apiUrl}\`

**Error:** ${errorMessage}

**💡 Troubleshooting Steps:**

${backendType === BACKEND_TYPES.NGROK ? `
1. **Check Colab** - Make sure all cells are executed
2. **Verify ngrok** - Check Cell 12 output for the ngrok URL
3. **Update URL** - Click the edit button (✎) to update the URL
4. **Restart Colab** - Runtime → Restart and run all
` : backendType === BACKEND_TYPES.COLAB ? `
1. **Check Colab** - Make sure all cells are executed
2. **Get Colab URL** - Run Cell 12 to get the Colab proxy URL
3. **Update URL** - Click the edit button (✎) to set the URL
4. **Restart Colab** - Runtime → Restart and run all
` : `
1. **Start Local Server** - Run \`python app.py\` or \`uvicorn app:app --reload\`
2. **Check Port** - Make sure port 8000 is not in use
3. **Verify Installation** - Ensure all dependencies are installed
`}

**Switch backends using the buttons above 👆**`,
          isUser: false,
          timestamp: new Date().toISOString(),
        }]);
      }
    }
  }, [backendType, getApiUrl, messages.length, selectedModel, currentConvId]);

  // Auto-check backend on mount and periodically
  useEffect(() => {
    checkBackend();
    const interval = setInterval(() => {
      if (connectionStatus === 'disconnected') {
        checkBackend();
      }
    }, 30000);
    return () => clearInterval(interval);
  }, [checkBackend, connectionStatus]);

  // Create new conversation
  const createNewConversation = () => {
    const newConv = {
      id: Date.now(),
      title: `Chat ${conversations.length + 1}`,
      messages: [],
      createdAt: new Date().toISOString(),
    };
    setConversations(prev => [newConv, ...prev]);
    setCurrentConvId(newConv.id);
    setMessages([]);
    setIsSidebarOpen(false);
  };

  // Load conversation
  const loadConversation = (conv) => {
    setCurrentConvId(conv.id);
    setMessages(conv.messages);
    setIsSidebarOpen(false);
  };

  // Delete conversation
  const deleteConversation = (convId, e) => {
    e.stopPropagation();
    setConversations(prev => prev.filter(c => c.id !== convId));
    if (currentConvId === convId && conversations.length > 1) {
      const nextConv = conversations.find(c => c.id !== convId);
      if (nextConv) {
        setCurrentConvId(nextConv.id);
        setMessages(nextConv.messages);
      } else {
        setCurrentConvId(null);
        setMessages([]);
      }
    }
  };

  // Copy message to clipboard
  const copyToClipboard = async (text, msgId) => {
    try {
      await navigator.clipboard.writeText(text);
      setCopiedMessageId(msgId);
      setTimeout(() => setCopiedMessageId(null), 2000);
    } catch (err) {
      console.error('Copy failed:', err);
    }
  };

  // Speech recognition setup
  const setupSpeechRecognition = () => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.webkitSpeechRecognition || window.SpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setInput(transcript);
        setIsRecording(false);
      };
      
      recognitionRef.current.onerror = () => {
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }
  };

  useEffect(() => {
    setupSpeechRecognition();
  }, []);

  const startVoiceInput = () => {
    if (recognitionRef.current) {
      setIsRecording(true);
      recognitionRef.current.start();
    } else {
      alert('Speech recognition is not supported in this browser');
    }
  };

  // Switch backend
  const switchBackend = (newBackend) => {
    setBackendType(newBackend);
    setConnectionStatus('checking');
    // Don't clear messages when switching backends, just reconnect
    setTimeout(() => checkBackend(), 500);
  };

  // Update custom URL
  const updateCustomUrl = (newUrl) => {
    if (newUrl && newUrl.trim() !== '') {
      setCustomUrl(newUrl.trim());
      setConnectionStatus('checking');
      setTimeout(() => checkBackend(), 500);
    }
    setIsEditingUrl(false);
  };

  // Send message to backend
  const sendMessage = async () => {
    if (!input.trim() || isLoading || connectionStatus !== 'connected') {
      if (connectionStatus !== 'connected') {
        alert('Please wait for backend connection to be established');
      }
      return;
    }

    const userMsg = {
      id: Date.now(),
      text: input,
      isUser: true,
      timestamp: new Date().toISOString(),
      model: selectedModel,
    };
    
    const updatedMessages = [...messages, userMsg];
    setMessages(updatedMessages);
    const sentMessage = input;
    setInput('');
    setIsLoading(true);

    // Update conversation title if it's the first message
    let convTitle = conversations.find(c => c.id === currentConvId)?.title;
    if (updatedMessages.length === 1 && (!convTitle || convTitle === 'New Conversation')) {
      const newTitle = sentMessage.slice(0, 30) + (sentMessage.length > 30 ? '...' : '');
      setConversations(prev => prev.map(c => 
        c.id === currentConvId ? { ...c, title: newTitle, messages: updatedMessages } : c
      ));
    } else {
      setConversations(prev => prev.map(c => 
        c.id === currentConvId ? { ...c, messages: updatedMessages } : c
      ));
    }

    try {
      const apiUrl = getApiUrl();
      console.log(`📤 Sending to: ${apiUrl}/chat`);
      console.log(`📝 Message: ${sentMessage}`);
      console.log(`🤖 Model: ${selectedModel}`);
      
      const response = await axios.post(`${apiUrl}/chat`, {
        message: sentMessage,
        model: selectedModel,
        user_id: 1,
      }, { 
        timeout: 120000,
        headers: { 
          'Content-Type': 'application/json'
        }
      });
      
      console.log('📥 Response received:', response.data);
      
      const aiMessage = {
        id: Date.now() + 1,
        text: response.data.reply || response.data.response || response.data.message || "I'm here to help!",
        isUser: false,
        timestamp: new Date().toISOString(),
        model: selectedModel,
        thinking: response.data.thinking,
      };
      
      const finalMessages = [...updatedMessages, aiMessage];
      setMessages(finalMessages);
      
      setConversations(prev => prev.map(c => 
        c.id === currentConvId ? { ...c, messages: finalMessages } : c
      ));
      
    } catch (error) {
      console.error('❌ Chat error:', error);
      
      let errorMsg = `❌ **Error:** ${error.message}\n\n`;
      
      if (error.code === 'ECONNABORTED') {
        errorMsg += '⏰ **Request Timeout**\n\nThe model might still be loading (this can take 1-2 minutes on first request). Please try again in a moment.';
      } else if (error.response?.status === 404) {
        errorMsg += '🔌 **Endpoint Not Found**\n\nMake sure the backend server is running and the URL is correct.';
      } else if (error.response?.status === 500) {
        errorMsg += '⚠️ **Server Error**\n\nThe backend encountered an error. Check your Colab notebook or local server logs.';
      } else if (error.code === 'ERR_NETWORK') {
        errorMsg += '🌐 **Network Error**\n\nCannot reach the server. Please verify:\n1. The backend is running\n2. The URL is correct\n3. Your internet connection is stable';
      } else if (error.response?.status === 403 || error.message?.includes('CORS')) {
        errorMsg += '🔒 **CORS Error**\n\nAdd CORS middleware to your FastAPI app:\n```python\nfrom fastapi.middleware.cors import CORSMiddleware\napp.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])\n```';
      }
      
      const errorMessage = {
        id: Date.now() + 1,
        text: errorMsg,
        isUser: false,
        timestamp: new Date().toISOString(),
      };
      
      const finalMessages = [...updatedMessages, errorMessage];
      setMessages(finalMessages);
      
      setConversations(prev => prev.map(c => 
        c.id === currentConvId ? { ...c, messages: finalMessages } : c
      ));
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

  const currentModel = MODELS.find(m => m.id === selectedModel) || MODELS[0];
  const CurrentIcon = currentModel.icon;
  const apiUrl = getApiUrl();

  return (
    <div className={`flex h-screen ${darkMode ? 'bg-black' : 'bg-gray-100'}`}>
      {/* Sidebar */}
      <div className={`
        fixed lg:relative z-40 w-80 h-full transform transition-transform duration-300 ease-out
        ${darkMode ? 'bg-gray-900' : 'bg-white border-r border-gray-200'}
        ${isSidebarOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Sidebar Header */}
          <div className={`p-5 border-b ${darkMode ? 'border-gray-800' : 'border-gray-200'} flex justify-between items-center`}>
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                <Zap className="w-5 h-5 text-white" />
              </div>
              <div>
                <h2 className={`font-semibold ${darkMode ? 'text-white' : 'text-gray-900'}`}>Mirabel AI</h2>
                <p className="text-xs text-gray-400">v3.0 • Multi-Backend</p>
              </div>
            </div>
            <button 
              onClick={() => setIsSidebarOpen(false)} 
              className="lg:hidden text-gray-400"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* New Chat Button */}
          <div className="p-4">
            <button
              onClick={createNewConversation}
              className="w-full flex items-center justify-center gap-2 py-2.5 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium text-sm"
            >
              <Plus className="w-4 h-4" />
              New Conversation
            </button>
          </div>

          {/* Backend Switcher - 3 Options */}
          <div className="px-4 pb-4 border-b border-gray-800">
            <p className="text-xs text-gray-400 mb-2">BACKEND</p>
            <div className="flex gap-1">
              <button
                onClick={() => switchBackend(BACKEND_TYPES.LOCAL)}
                className={`flex-1 flex items-center justify-center gap-1.5 p-2 rounded-lg transition-all text-xs ${
                  backendType === BACKEND_TYPES.LOCAL 
                    ? 'bg-gradient-to-r from-green-600 to-emerald-600 text-white' 
                    : darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600'
                }`}
              >
                <Server className="w-3.5 h-3.5" />
                <span>Local</span>
              </button>
              <button
                onClick={() => switchBackend(BACKEND_TYPES.NGROK)}
                className={`flex-1 flex items-center justify-center gap-1.5 p-2 rounded-lg transition-all text-xs ${
                  backendType === BACKEND_TYPES.NGROK 
                    ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white' 
                    : darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600'
                }`}
              >
                <Cloud className="w-3.5 h-3.5" />
                <span>ngrok</span>
              </button>
              <button
                onClick={() => switchBackend(BACKEND_TYPES.COLAB)}
                className={`flex-1 flex items-center justify-center gap-1.5 p-2 rounded-lg transition-all text-xs ${
                  backendType === BACKEND_TYPES.COLAB 
                    ? 'bg-gradient-to-r from-blue-600 to-cyan-600 text-white' 
                    : darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600'
                }`}
              >
                <Database className="w-3.5 h-3.5" />
                <span>Colab</span>
              </button>
            </div>
          </div>

          {/* Model List */}
          <div className="p-4 border-b border-gray-800">
            <p className="text-xs text-gray-400 mb-2">AI MODELS</p>
            <div className="space-y-2">
              {MODELS.map((model) => {
                const Icon = model.icon;
                const isActive = selectedModel === model.id;
                return (
                  <button
                    key={model.id}
                    onClick={() => {
                      setSelectedModel(model.id);
                      setIsSidebarOpen(false);
                    }}
                    className={`w-full p-2.5 rounded-xl transition-all ${
                      isActive 
                        ? `bg-gradient-to-r ${model.gradient}` 
                        : darkMode ? 'bg-gray-800/50 hover:bg-gray-800' : 'bg-gray-100 hover:bg-gray-200'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <div className={`w-7 h-7 rounded-lg flex items-center justify-center ${isActive ? 'bg-white/20' : darkMode ? 'bg-gray-700' : 'bg-gray-300'}`}>
                        <Icon className={`w-3.5 h-3.5 ${isActive ? 'text-white' : `text-${model.color}-400`}`} />
                      </div>
                      <div className="flex-1 text-left">
                        <p className={`text-sm font-medium ${isActive ? 'text-white' : darkMode ? 'text-gray-200' : 'text-gray-800'}`}>
                          {model.name}
                        </p>
                        <p className={`text-xs ${isActive ? 'text-white/70' : 'text-gray-500'}`}>
                          {model.description}
                        </p>
                      </div>
                      {isActive && <div className="w-1.5 h-1.5 bg-green-400 rounded-full" />}
                    </div>
                  </button>
                );
              })}
            </div>
          </div>

          {/* Conversation List */}
          <div className="flex-1 overflow-y-auto p-4">
            <p className="text-xs text-gray-400 mb-2">RECENT CHATS</p>
            <div className="space-y-1">
              {conversations.map(conv => (
                <div
                  key={conv.id}
                  onClick={() => loadConversation(conv)}
                  className={`flex items-center justify-between p-2 rounded-lg cursor-pointer transition-all group ${
                    currentConvId === conv.id
                      ? 'bg-purple-500/20'
                      : darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-100'
                  }`}
                >
                  <div className="flex items-center gap-2 flex-1 min-w-0">
                    <MessageSquare className="w-3.5 h-3.5 text-gray-400 flex-shrink-0" />
                    <span className={`text-sm truncate ${darkMode ? 'text-gray-300' : 'text-gray-700'}`}>
                      {conv.title}
                    </span>
                  </div>
                  <button
                    onClick={(e) => deleteConversation(conv.id, e)}
                    className="opacity-0 group-hover:opacity-100 p-1 hover:bg-red-500/20 rounded transition-opacity"
                  >
                    <Trash2 className="w-3.5 h-3.5 text-red-400" />
                  </button>
                </div>
              ))}
            </div>
          </div>

          {/* Footer */}
          <div className="p-4 border-t border-gray-800">
            <div className={`rounded-xl p-3 ${darkMode ? 'bg-gray-800/30' : 'bg-gray-100'}`}>
              <p className="text-xs text-gray-400">Created by</p>
              <p className="text-sm text-purple-400 font-medium">Rishav Kumar</p>
              <p className="text-xs text-gray-500">B.Tech Automation & Robotics (2025)</p>
            </div>
            
            {/* Editable URL Display */}
            <div className="mt-3 p-2 rounded-lg bg-gray-800/50">
              <p className="text-[10px] text-gray-500 mb-1">
                {backendType === BACKEND_TYPES.LOCAL ? 'LOCAL URL' : backendType === BACKEND_TYPES.NGROK ? 'NGROK URL' : 'COLAB URL'}
              </p>
              {isEditingUrl ? (
                <div className="flex gap-1">
                  <input
                    type="text"
                    value={tempUrl}
                    onChange={(e) => setTempUrl(e.target.value)}
                    placeholder={backendType === BACKEND_TYPES.LOCAL ? "http://localhost:8000" : "https://your-url.ngrok-free.dev"}
                    className="flex-1 bg-gray-700 text-purple-400 text-[10px] rounded px-1 py-0.5 outline-none"
                    autoFocus
                    onKeyDown={(e) => {
                      if (e.key === 'Enter') {
                        updateCustomUrl(tempUrl);
                      } else if (e.key === 'Escape') {
                        setIsEditingUrl(false);
                      }
                    }}
                  />
                  <button
                    onClick={() => updateCustomUrl(tempUrl)}
                    className="text-green-400 hover:text-green-300 px-1"
                  >
                    ✓
                  </button>
                  <button
                    onClick={() => setIsEditingUrl(false)}
                    className="text-red-400 hover:text-red-300 px-1"
                  >
                    ✗
                  </button>
                </div>
              ) : (
                <div
                  className="flex items-start justify-between gap-1 cursor-pointer group"
                  onClick={() => {
                    setTempUrl(apiUrl);
                    setIsEditingUrl(true);
                  }}
                >
                  <p className="text-[10px] text-purple-400 break-all flex-1">
                    {apiUrl || 'Click to set URL'}
                  </p>
                  <button className="opacity-0 group-hover:opacity-100 text-gray-500 hover:text-gray-400 flex-shrink-0 ml-1">
                    ✎
                  </button>
                </div>
              )}
            </div>
            
            {/* Theme Toggle */}
            <button
              onClick={() => setDarkMode(!darkMode)}
              className="mt-3 w-full flex items-center justify-center gap-2 py-2 rounded-lg bg-gray-800 text-gray-400 text-sm"
            >
              {darkMode ? <Sun className="w-4 h-4" /> : <Moon className="w-4 h-4" />}
              {darkMode ? 'Light Mode' : 'Dark Mode'}
            </button>
          </div>
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col overflow-hidden relative">
        {/* Header */}
        <div className={`flex items-center justify-between px-4 py-3 border-b ${darkMode ? 'border-gray-800 bg-black/50' : 'border-gray-200 bg-white/50'} backdrop-blur-sm`}>
          <div className="flex items-center gap-2">
            <button
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2 rounded-lg hover:bg-gray-800"
            >
              <Menu className="w-5 h-5 text-gray-400" />
            </button>
            
            {/* Model Display */}
            <div className={`hidden lg:flex items-center gap-2 px-3 py-1.5 rounded-full ${darkMode ? 'bg-gray-800' : 'bg-gray-100'}`}>
              <div className={`w-6 h-6 rounded-lg bg-gradient-to-r ${currentModel.gradient} flex items-center justify-center`}>
                <CurrentIcon className="w-3 h-3 text-white" />
              </div>
              <span className={`text-sm font-medium ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                {currentModel.name}
              </span>
              <span className="text-xs text-gray-400">{currentModel.badge}</span>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {/* Status Indicator */}
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${connectionStatus === 'connected' ? 'bg-green-500/10' : 'bg-red-500/10'}`}>
              {connectionStatus === 'connected' ? (
                <Wifi className="w-3.5 h-3.5 text-green-400" />
              ) : connectionStatus === 'checking' ? (
                <Loader2 className="w-3.5 h-3.5 text-yellow-400 animate-spin" />
              ) : (
                <WifiOff className="w-3.5 h-3.5 text-red-400" />
              )}
              <span className="text-xs text-gray-400">{backendMessage}</span>
            </div>
            
            {/* Refresh Button */}
            <button
              onClick={() => { setConnectionStatus('checking'); checkBackend(); }}
              className="p-1.5 rounded-lg hover:bg-gray-800 transition-colors"
              title="Refresh Connection"
            >
              <RefreshCw className={`w-4 h-4 text-gray-400 ${connectionStatus === 'checking' ? 'animate-spin' : ''}`} />
            </button>
            
            {/* Backend Indicator */}
            <div className={`flex items-center gap-1.5 px-2 py-1 rounded-full ${darkMode ? 'bg-gray-800' : 'bg-gray-200'}`}>
              {getBackendIcon()}
              <span className="text-xs font-medium">{getBackendDisplayName()}</span>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto px-4 py-6">
          <div className="max-w-4xl mx-auto space-y-4">
            {messages.length === 0 ? (
              <div className="flex flex-col items-center justify-center h-full text-center py-20">
                <div className="w-20 h-20 rounded-2xl bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center mb-4">
                  <Sparkles className="w-10 h-10 text-white" />
                </div>
                <h3 className={`text-xl font-semibold mb-2 ${darkMode ? 'text-white' : 'text-gray-800'}`}>
                  Welcome to Mirabel AI
                </h3>
                <p className="text-gray-400 max-w-md">
                  {connectionStatus === 'connected' 
                    ? `Connected to ${getBackendDisplayName()} backend! Ask me anything!`
                    : 'Select a backend and click refresh to connect'}
                </p>
                <div className="flex flex-wrap gap-2 mt-6 justify-center">
                  {[
                    "Who created you?",
                    "Write a Python function",
                    "Explain quantum computing",
                    "Tell me a joke"
                  ].map((suggestion) => (
                    <button
                      key={suggestion}
                      onClick={() => setInput(suggestion)}
                      className={`px-3 py-1.5 rounded-full text-xs ${
                        darkMode ? 'bg-gray-800 text-gray-300' : 'bg-gray-200 text-gray-700'
                      }`}
                    >
                      {suggestion}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              messages.map((msg) => (
                <div key={msg.id} className={`flex ${msg.isUser ? 'justify-end' : 'justify-start'} animate-fade-in`}>
                  <div className={`flex max-w-[85%] gap-2 ${msg.isUser ? 'flex-row-reverse' : 'flex-row'}`}>
                    {/* Avatar */}
                    <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center ${
                      msg.isUser 
                        ? 'bg-blue-600' 
                        : 'bg-gradient-to-r from-purple-500 to-pink-500'
                    }`}>
                      {msg.isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
                    </div>
                    
                    {/* Message Bubble */}
                    <div className={`group relative rounded-2xl px-4 py-2.5 ${
                      msg.isUser 
                        ? 'bg-gradient-to-r from-blue-600 to-blue-700 text-white' 
                        : darkMode ? 'bg-gray-800/80 text-gray-100 border border-gray-700' : 'bg-gray-100 text-gray-800 border border-gray-200'
                    }`}>
                      <div className="prose prose-invert prose-sm max-w-none text-sm">
                        <ReactMarkdown
                          components={{
                            code({ node, inline, className, children, ...props }) {
                              const match = /language-(\w+)/.exec(className || '');
                              return !inline && match ? (
                                <CodeBlock language={match[1]}>
                                  {String(children).replace(/\n$/, '')}
                                </CodeBlock>
                              ) : (
                                <code className={`${darkMode ? 'bg-gray-700' : 'bg-gray-200'} px-1 py-0.5 rounded text-xs`} {...props}>
                                  {children}
                                </code>
                              );
                            }
                          }}
                        >
                          {msg.text}
                        </ReactMarkdown>
                      </div>
                      
                      {/* Message Actions */}
                      <div className="flex items-center justify-between mt-1.5">
                        <p className="text-[9px] opacity-50">
                          {new Date(msg.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                          {msg.model && ` • ${msg.model.split(':')[0]}`}
                        </p>
                        <button
                          onClick={() => copyToClipboard(msg.text, msg.id)}
                          className="opacity-0 group-hover:opacity-100 transition-opacity"
                        >
                          {copiedMessageId === msg.id ? (
                            <Check className="w-3 h-3 text-green-400" />
                          ) : (
                            <Copy className="w-3 h-3 text-gray-400" />
                          )}
                        </button>
                      </div>
                    </div>
                  </div>
                </div>
              ))
            )}
            
            {isLoading && (
              <div className="flex justify-start animate-fade-in">
                <div className="flex gap-2">
                  <div className="w-8 h-8 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                    <Bot className="w-4 h-4 text-white" />
                  </div>
                  <div className={`rounded-2xl px-4 py-3 ${darkMode ? 'bg-gray-800/80' : 'bg-gray-100'}`}>
                    <div className="flex gap-1.5">
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                      <div className="w-2 h-2 bg-purple-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Input Area */}
        <div className={`border-t ${darkMode ? 'border-gray-800' : 'border-gray-200'} ${darkMode ? 'bg-black/90' : 'bg-white/90'} backdrop-blur-sm p-4 pb-6`}>
          <div className="max-w-4xl mx-auto">
            {/* Model Selector Chips */}
            <div className="flex gap-2 mb-3 overflow-x-auto pb-1 lg:hidden">
              {MODELS.map((model) => {
                const Icon = model.icon;
                const isActive = selectedModel === model.id;
                return (
                  <button
                    key={model.id}
                    onClick={() => setSelectedModel(model.id)}
                    className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full text-xs whitespace-nowrap transition-all ${
                      isActive 
                        ? `bg-gradient-to-r ${model.gradient} text-white` 
                        : darkMode ? 'bg-gray-800 text-gray-400' : 'bg-gray-200 text-gray-600'
                    }`}
                  >
                    <Icon className="w-3.5 h-3.5" />
                    <span>{model.name}</span>
                  </button>
                );
              })}
            </div>
            
            {/* Input Bar */}
            <div className="flex gap-2 items-end">
              <div className="flex-1 relative">
                <textarea
                  ref={inputRef}
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  onKeyDown={handleKeyPress}
                  placeholder="Ask Mirabel anything..."
                  className={`w-full rounded-2xl px-4 py-3 resize-none focus:outline-none focus:ring-2 focus:ring-purple-500 text-sm ${
                    darkMode ? 'bg-gray-800 text-white' : 'bg-gray-100 text-gray-800'
                  }`}
                  rows="1"
                  disabled={isLoading || connectionStatus !== 'connected'}
                  style={{ maxHeight: '120px' }}
                />
              </div>
              
              <button
                onClick={startVoiceInput}
                disabled={isLoading}
                className={`p-3 rounded-2xl transition-all ${
                  isRecording 
                    ? 'bg-red-500 animate-pulse' 
                    : darkMode ? 'bg-gray-800 hover:bg-gray-700' : 'bg-gray-200 hover:bg-gray-300'
                }`}
              >
                {isRecording ? <MicOff className="w-5 h-5 text-white" /> : <Mic className={`w-5 h-5 ${darkMode ? 'text-gray-400' : 'text-gray-600'}`} />}
              </button>
              
              <button
                onClick={sendMessage}
                disabled={!input.trim() || isLoading || connectionStatus !== 'connected'}
                className={`p-3 rounded-2xl transition-all ${
                  input.trim() && !isLoading && connectionStatus === 'connected'
                    ? 'bg-gradient-to-r from-purple-500 to-pink-500 shadow-lg shadow-purple-500/25'
                    : darkMode ? 'bg-gray-700 cursor-not-allowed' : 'bg-gray-300 cursor-not-allowed'
                }`}
              >
                <Send className="w-5 h-5 text-white" />
              </button>
            </div>
            
            <div className="flex justify-between items-center mt-2 px-1">
              <div className="flex items-center gap-1.5">
                <div className={`w-1.5 h-1.5 rounded-full ${connectionStatus === 'connected' ? 'bg-green-400 animate-pulse' : connectionStatus === 'checking' ? 'bg-yellow-400' : 'bg-red-400'}`} />
                <p className="text-[10px] text-gray-500">
                  {connectionStatus === 'connected' 
                    ? `${getBackendDisplayName()} • ${currentModel.name} • Ready` 
                    : connectionStatus === 'checking' ? '🔄 Connecting...' : backendMessage}
                </p>
              </div>
              <p className="text-[10px] text-gray-600">
                Enter to send • Shift+Enter for new line
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Global Styles */}
      <style>{`
        @keyframes fade-in {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }
        .animate-fade-in { animation: fade-in 0.3s ease-out; }
        
        @keyframes bounce {
          0%, 100% { transform: translateY(0); }
          50% { transform: translateY(-4px); }
        }
        .animate-bounce { animation: bounce 0.6s ease-in-out infinite; }
        
        ::-webkit-scrollbar { width: 6px; height: 6px; }
        ::-webkit-scrollbar-track { background: ${darkMode ? '#1a1a1a' : '#f0f0f0'}; }
        ::-webkit-scrollbar-thumb { background: ${darkMode ? '#4a4a4a' : '#c0c0c0'}; border-radius: 10px; }
        ::-webkit-scrollbar-thumb:hover { background: ${darkMode ? '#6a6a6a' : '#a0a0a0'}; }
        
        .prose { max-width: none; }
        .prose p { margin: 0 0 0.5em 0; }
        .prose p:last-child { margin-bottom: 0; }
        .prose pre { margin: 0.5em 0; }
        .prose code { font-size: 0.75rem; }
        
        textarea, input { font-size: 16px; }
        
        .group:hover .group-hover\\:opacity-100 {
          opacity: 1;
        }
      `}</style>
    </div>
  );
}

export default App;