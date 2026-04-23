// src/components/Message.jsx - Updated to show "Mirabel AI" instead of model name
import ReactMarkdown from 'react-markdown';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { vscDarkPlus } from 'react-syntax-highlighter/dist/esm/styles/prism';
import { Bot, User, Sparkles } from 'lucide-react';

export default function Message({ message, isUser, timestamp }) {
  return (
    <div className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-4`}>
      <div className={`flex max-w-[80%] ${isUser ? 'flex-row-reverse' : 'flex-row'}`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 ${isUser ? 'ml-3' : 'mr-3'}`}>
          <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
            isUser ? 'bg-blue-500' : 'bg-purple-600'
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
          {/* Mirabel AI Brand (instead of model name) */}
          {!isUser && (
            <div className="flex items-center gap-1 mb-1 text-xs">
              <Sparkles className="w-3 h-3 text-purple-400" />
              <span className="font-semibold text-purple-300">Mirabel AI</span>
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