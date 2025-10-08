import React, { useState, useRef, useEffect } from 'react';
import { 
  Send, 
  Mic, 
  MicOff, 
  Loader, 
  Download, 
  Copy, 
  Share, 
  Zap,
  Clock,
  Database,
  Filter,
  TrendingUp,
  AlertTriangle,
  CheckCircle,
  XCircle
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

interface QueryInterfaceProps {
  onSubmit: (query: string, options?: QueryOptions) => Promise<void>;
  isLoading: boolean;
  suggestions?: string[];
  isConnected: boolean;
}

interface QueryOptions {
  timeRange?: string;
  maxResults?: number;
  format?: 'table' | 'json' | 'chart';
  export?: boolean;
}

interface QuerySuggestion {
  text: string;
  category: 'authentication' | 'network' | 'malware' | 'system' | 'general';
  icon: React.ReactNode;
  description: string;
}

const QueryInterface: React.FC<QueryInterfaceProps> = ({
  onSubmit,
  isLoading,
  suggestions = [],
  isConnected
}) => {
  const [query, setQuery] = useState('');
  const [isRecording, setIsRecording] = useState(false);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [selectedOption, setSelectedOption] = useState<QueryOptions>({});
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Smart query suggestions based on SIEM use cases
  const smartSuggestions: QuerySuggestion[] = [
    {
      text: "Show me failed SSH login attempts from external IPs in the last hour",
      category: 'authentication',
      icon: <XCircle className="w-4 h-4 text-red-400" />,
      description: "Authentication failures from external sources"
    },
    {
      text: "Find all malware detections with high severity today",
      category: 'malware',
      icon: <AlertTriangle className="w-4 h-4 text-orange-400" />,
      description: "Critical malware threats detected"
    },
    {
      text: "Analyze network traffic anomalies in the DMZ",
      category: 'network',
      icon: <TrendingUp className="w-4 h-4 text-blue-400" />,
      description: "Unusual network patterns and flows"
    },
    {
      text: "Generate security incident summary for yesterday",
      category: 'general',
      icon: <CheckCircle className="w-4 h-4 text-green-400" />,
      description: "Comprehensive security report"
    }
  ];

  const handleSubmit = async () => {
    if (!query.trim() || isLoading) return;
    
    await onSubmit(query, selectedOption);
    setQuery('');
    setShowSuggestions(false);
    setSelectedOption({});
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleVoiceInput = () => {
    if (!('webkitSpeechRecognition' in window)) {
      alert('Speech recognition not supported in this browser');
      return;
    }

    const recognition = new (window as any).webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => setIsRecording(true);
    recognition.onend = () => setIsRecording(false);
    
    recognition.onresult = (event: any) => {
      const transcript = event.results[0][0].transcript;
      setQuery(transcript);
    };

    recognition.start();
  };

  const copyToClipboard = (text: string) => {
    navigator.clipboard.writeText(text);
    // Add toast notification here
  };

  const getCategoryColor = (category: QuerySuggestion['category']) => {
    const colors = {
      authentication: 'bg-red-500/10 text-red-400 border-red-500/20',
      network: 'bg-blue-500/10 text-blue-400 border-blue-500/20',
      malware: 'bg-orange-500/10 text-orange-400 border-orange-500/20',
      system: 'bg-purple-500/10 text-purple-400 border-purple-500/20',
      general: 'bg-green-500/10 text-green-400 border-green-500/20'
    };
    return colors[category];
  };

  return (
    <div className="w-full max-w-4xl mx-auto space-y-4">
      {/* Status Bar */}
      <div className="flex items-center justify-between p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center space-x-4">
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-yellow-400'}`} />
            <span className="text-sm text-gray-300">
              {isConnected ? 'Live SIEM Connected' : 'Demo Mode'}
            </span>
          </div>
          
          {isConnected && (
            <div className="flex items-center space-x-1 text-xs text-gray-400">
              <Zap className="w-3 h-3" />
              <span>Response: ~200ms</span>
            </div>
          )}
        </div>

        <div className="flex items-center space-x-2">
          <button
            onClick={() => setShowSuggestions(!showSuggestions)}
            className="px-3 py-1 text-xs bg-blue-600/20 text-blue-400 border border-blue-600/30 rounded-full hover:bg-blue-600/30 transition-colors"
          >
            Smart Queries
          </button>
          
          <div className="flex items-center space-x-1 text-xs text-gray-400">
            <Database className="w-3 h-3" />
            <span>Elasticsearch</span>
          </div>
        </div>
      </div>

      {/* Smart Suggestions */}
      <AnimatePresence>
        {showSuggestions && (
          <motion.div
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -20 }}
            className="grid grid-cols-1 md:grid-cols-2 gap-3"
          >
            {smartSuggestions.map((suggestion, index) => (
              <motion.button
                key={index}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                onClick={() => {
                  setQuery(suggestion.text);
                  setShowSuggestions(false);
                }}
                className={`p-4 rounded-lg border text-left hover:scale-105 transition-all ${getCategoryColor(suggestion.category)}`}
              >
                <div className="flex items-start space-x-3">
                  {suggestion.icon}
                  <div className="flex-1 min-w-0">
                    <div className="text-sm font-medium text-gray-200 mb-1">
                      {suggestion.text}
                    </div>
                    <div className="text-xs opacity-70">
                      {suggestion.description}
                    </div>
                  </div>
                </div>
              </motion.button>
            ))}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Query Options */}
      <div className="flex items-center space-x-4 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
        <div className="flex items-center space-x-2">
          <Clock className="w-4 h-4 text-gray-400" />
          <select
            value={selectedOption.timeRange || '1h'}
            onChange={(e) => setSelectedOption(prev => ({ ...prev, timeRange: e.target.value }))}
            className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200"
          >
            <option value="15m">Last 15 minutes</option>
            <option value="1h">Last hour</option>
            <option value="24h">Last 24 hours</option>
            <option value="7d">Last week</option>
            <option value="30d">Last month</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <Filter className="w-4 h-4 text-gray-400" />
          <select
            value={selectedOption.format || 'table'}
            onChange={(e) => setSelectedOption(prev => ({ ...prev, format: e.target.value as any }))}
            className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200"
          >
            <option value="table">Table View</option>
            <option value="json">JSON Format</option>
            <option value="chart">Chart View</option>
          </select>
        </div>

        <div className="flex items-center space-x-2">
          <Database className="w-4 h-4 text-gray-400" />
          <input
            type="number"
            value={selectedOption.maxResults || 1000}
            onChange={(e) => setSelectedOption(prev => ({ ...prev, maxResults: parseInt(e.target.value) }))}
            className="bg-gray-700 border border-gray-600 rounded px-2 py-1 text-sm text-gray-200 w-20"
            placeholder="Max"
          />
          <span className="text-xs text-gray-400">results</span>
        </div>
      </div>

      {/* Main Query Input */}
      <div className="relative">
        <div className="relative">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask me anything about your SIEM data... 
            
Examples:
• Show failed login attempts from external IPs
• Find malware detections with high severity  
• Analyze unusual network traffic patterns
• Generate security summary for last 24 hours"
            className="w-full p-4 pr-32 bg-gray-800 border border-gray-700 rounded-2xl text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent min-h-[120px]"
            rows={4}
          />
          
          {/* Input Actions */}
          <div className="absolute bottom-4 right-4 flex items-center space-x-2">
            <button
              onClick={handleVoiceInput}
              disabled={isRecording}
              className={`p-2 rounded-lg transition-colors ${
                isRecording 
                  ? 'bg-red-600 text-white animate-pulse' 
                  : 'bg-gray-700 text-gray-300 hover:bg-gray-600 hover:text-white'
              }`}
              title="Voice input"
            >
              {isRecording ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4" />}
            </button>

            <button
              onClick={handleSubmit}
              disabled={!query.trim() || isLoading}
              className="p-2 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-lg transition-colors"
              title="Send query"
            >
              {isLoading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Send className="w-4 h-4" />
              )}
            </button>
          </div>
        </div>

        {/* Character Counter */}
        <div className="flex justify-between items-center mt-2 text-xs text-gray-500">
          <span>
            {isConnected 
              ? 'Connected to live SIEM • Press Enter to send, Shift+Enter for new line'
              : 'Demo mode with mock responses'
            }
          </span>
          <span className={query.length > 500 ? 'text-yellow-400' : ''}>
            {query.length}/1000
          </span>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex flex-wrap gap-2">
        <button
          onClick={() => copyToClipboard(query)}
          disabled={!query.trim()}
          className="flex items-center space-x-1 px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 disabled:bg-gray-800 disabled:text-gray-500 text-gray-300 rounded-full transition-colors"
        >
          <Copy className="w-3 h-3" />
          <span>Copy Query</span>
        </button>

        <button
          onClick={() => setSelectedOption(prev => ({ ...prev, export: !prev.export }))}
          className={`flex items-center space-x-1 px-3 py-1 text-xs rounded-full transition-colors ${
            selectedOption.export 
              ? 'bg-green-600/20 text-green-400 border border-green-600/30'
              : 'bg-gray-700 hover:bg-gray-600 text-gray-300'
          }`}
        >
          <Download className="w-3 h-3" />
          <span>Auto Export</span>
        </button>

        <button
          className="flex items-center space-x-1 px-3 py-1 text-xs bg-gray-700 hover:bg-gray-600 text-gray-300 rounded-full transition-colors"
        >
          <Share className="w-3 h-3" />
          <span>Share Query</span>
        </button>
      </div>
    </div>
  );
};

export default QueryInterface;
