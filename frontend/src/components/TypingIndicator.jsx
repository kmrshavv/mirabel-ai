// src/components/TypingIndicator.jsx
import { Bot } from 'lucide-react';

export default function TypingIndicator() {
  return (
    <div className="flex justify-start mb-4">
      <div className="flex max-w-[80%] flex-row">
        <div className="flex-shrink-0 mr-3">
          <div className="w-8 h-8 rounded-full bg-gray-600 flex items-center justify-center">
            <Bot className="w-4 h-4 text-white" />
          </div>
        </div>
        <div className="bg-gray-800 rounded-lg px-4 py-3">
          <div className="flex gap-1">
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></span>
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></span>
            <span className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></span>
          </div>
        </div>
      </div>
    </div>
  );
}