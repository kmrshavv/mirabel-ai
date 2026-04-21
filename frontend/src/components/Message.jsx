// src/components/Message.jsx
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, Cpu, Code, BookOpen, FileText, Heart } from 'lucide-react';

const modelIcons = {
  'llama3.2:3b': <Heart className="w-4 h-4 text-pink-500" />,
  'qwen2.5-coder:14b': <Code className="w-4 h-4 text-blue-500" />,
  'mistral:7b': <BookOpen className="w-4 h-4 text-green-500" />,
  'granite3-dense:8b': <FileText className="w-4 h-4 text-purple-500" />,
};

export default function Message({ message, isUser, modelUsed, timestamp }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : 'bg-gray-600'
          }`}>
            {isUser ? <User className="w-4 h-4 text-white" /> : <Bot className="w-4 h-4 text-white" />}
          </div>
        </div>
        
        {/* Message Bubble */}
        <div className={`rounded-lg px-4 py-2 ${
          isUser 
            ? 'bg-blue-500 text-white' 
            : 'bg-gray-800 text-gray-100'
        }`}>
          {/* Model indicator (only for AI messages) */}
          {!isUser && modelUsed && (
            <div className="flex items-center gap-1 mb-1 text-xs opacity-70">
              {modelIcons[modelUsed] || <Cpu className="w-3 h-3" />}
              <span>{modelUsed.split(':')[0]}</span>
            </div>
          )}
          
          {/* Message content with markdown support */}
          <div className="prose prose-invert max-w-none">
            <ReactMarkdown
              components={{
                code({node, inline, className, children, ...props}) {
                  const match = /language-(\w+)/.exec(className || '');
                  return !inline && match ? (
                    <SyntaxHighlighter
                      style={vscDarkPlus}
                      language={match[1]}
                      PreTag="div"
                      {...props}
                    >
                      {String(children).replace(/\n$/, '')}
                    </SyntaxHighlighter>
                  ) : (
                    <code className={className} {...props}>
                      {children}
                    </code>
                  );
                }
              }}
            >
              {message}
            </ReactMarkdown>
          </div>
          
          {/* Timestamp */}
          <div className={`text-xs mt-1 ${isUser ? 'text-blue-200' : 'text-gray-400'}`}>
            {new Date(timestamp).toLocaleTimeString()}
          </div>
        </div>
      </div>
    </div>
  );
}