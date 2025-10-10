/**
 * KARTAVYA SIEM - Composer Component
 * Chat input with quick-suggest chips and voice input per blueprint
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Mic, Zap } from 'lucide-react';

interface ComposerProps {
  value: string;
  onChange: (value: string) => void;
  onSend: (message: string) => void;
  isLoading: boolean;
  quickActions: string[];
}

const Composer: React.FC<ComposerProps> = ({ 
  value, 
  onChange, 
  onSend, 
  isLoading, 
  quickActions 
}) => {
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [filteredSuggestions, setFilteredSuggestions] = useState<string[]>([]);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = textareaRef.current.scrollHeight + 'px';
    }
  }, [value]);

  // Filter suggestions based on input
  useEffect(() => {
    if (value.trim().length > 0) {
      const filtered = quickActions.filter(action => 
        action.toLowerCase().includes(value.toLowerCase())
      );
      setFilteredSuggestions(filtered.slice(0, 3));
      setShowSuggestions(filtered.length > 0 && value.length > 2);
    } else {
      setShowSuggestions(false);
      setFilteredSuggestions([]);
    }
  }, [value, quickActions]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (value.trim() && !isLoading) {
      onSend(value.trim());
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e as any);
    }
    if (e.key === 'Escape') {
      setShowSuggestions(false);
    }
  };

  const handleSuggestionClick = (suggestion: string) => {
    onChange(suggestion);
    setShowSuggestions(false);
    setTimeout(() => textareaRef.current?.focus(), 0);
  };

  const handleQuickActionClick = (action: string) => {
    if (!isLoading) {
      onSend(action);
    }
  };

  return (
    <div className="relative">
      {/* Quick Action Chips - Show when input is empty */}
      {!value && !isLoading && (
        <div className="mb-3">
          <div className="flex items-center space-x-2 mb-2">
            <Zap className="w-4 h-4 text-yellow-400" />
            <span className="text-xs text-gray-400 font-medium">QUICK ACTIONS</span>
          </div>
          <div className="flex flex-wrap gap-2">
            {quickActions.slice(0, 4).map((action, index) => (
              <button
                key={index}
                onClick={() => handleQuickActionClick(action)}
                className="bg-gray-800 hover:bg-gray-700 border border-gray-600 px-3 py-1.5 rounded-lg text-xs text-gray-300 transition-colors"
              >
                {action}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Suggestions Dropdown */}
      {showSuggestions && (
        <div className="absolute bottom-full left-0 right-0 mb-2 bg-gray-800 border border-gray-600 rounded-lg shadow-lg z-10">
          <div className="p-2">
            <div className="text-xs text-gray-400 mb-2">Suggestions:</div>
            {filteredSuggestions.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="w-full text-left p-2 hover:bg-gray-700 rounded text-sm text-gray-200 transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end space-x-2">
          {/* Text Input */}
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={value}
              onChange={(e) => onChange(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder={isLoading ? "Processing your request..." : "Ask me about your security data..."}
              disabled={isLoading}
              rows={1}
              className="w-full bg-gray-800 border border-gray-600 rounded-lg px-4 py-3 pr-12 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 resize-none min-h-[48px] max-h-32"
            />
            
            {/* Character/word count for long queries */}
            {value.length > 100 && (
              <div className="absolute top-2 right-12 text-xs text-gray-500">
                {value.length}/1000
              </div>
            )}
          </div>

          {/* Voice Input Button */}
          <button
            type="button"
            className="p-3 bg-gray-700 hover:bg-gray-600 border border-gray-600 rounded-lg transition-colors"
            title="Voice input (coming soon)"
          >
            <Mic className="w-4 h-4 text-gray-400" />
          </button>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!value.trim() || isLoading}
            className={`p-3 rounded-lg transition-colors ${
              value.trim() && !isLoading
                ? 'bg-blue-600 hover:bg-blue-700 text-white'
                : 'bg-gray-700 text-gray-500 cursor-not-allowed'
            }`}
          >
            <Send className="w-4 h-4" />
          </button>
        </div>

        {/* Helper Text */}
        <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
          <span>Press Enter to send, Shift+Enter for new line</span>
          {isLoading && (
            <span className="flex items-center space-x-1">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse"></div>
              <span>Processing...</span>
            </span>
          )}
        </div>
      </form>
    </div>
  );
};

export default Composer;
