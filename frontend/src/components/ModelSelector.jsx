// src/components/ModelSelector.jsx
import { Heart, Code, BookOpen, FileText, Cpu } from 'lucide-react';

const models = [
  { id: 'llama3.2:3b', name: 'Emotional', icon: Heart, color: 'pink', description: 'Empathetic conversations' },
  { id: 'qwen2.5-coder:14b', name: 'Coder', icon: Code, color: 'blue', description: 'Flawless code generation' },
  { id: 'mistral:7b', name: 'Researcher', icon: BookOpen, color: 'green', description: 'Multi-platform research' },
  { id: 'granite3-dense:8b', name: 'Document Analyst', icon: FileText, color: 'purple', description: 'Document review expert' },
];

export default function ModelSelector({ selectedModel, onModelChange }) {
  return (
    <div className="bg-gray-900 rounded-lg p-3">
      <h3 className="text-sm font-semibold text-gray-300 mb-2">Active Model</h3>
      <div className="grid grid-cols-2 gap-2">
        {models.map((model) => {
          const Icon = model.icon;
          const isSelected = selectedModel === model.id;
          return (
            <button
              key={model.id}
              onClick={() => onModelChange(model.id)}
              className={`p-2 rounded-lg transition-all ${
                isSelected
                  ? `bg-${model.color}-600 text-white ring-2 ring-${model.color}-400`
                  : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
              }`}
            >
              <div className="flex items-center gap-2">
                <Icon className={`w-4 h-4 ${isSelected ? 'text-white' : `text-${model.color}-400`}`} />
                <div className="text-left">
                  <div className="text-xs font-medium">{model.name}</div>
                  <div className="text-xs opacity-70">{model.description}</div>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </div>
  );
}