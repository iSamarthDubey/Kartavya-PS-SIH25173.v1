import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { User, Bot, Clock, Database, Zap, AlertTriangle, ChevronDown, ChevronUp, Copy, Check } from 'lucide-react';

interface MessageMetadata {
  intent?: string;
  confidence?: number;
  entities?: Record<string, any>;
  query?: {
    dsl: any;
    index: string;
  };
  results_count?: number;
  execution_time?: number;
  platform?: string;
}

interface MessageBubbleProps {
  sender: 'user' | 'ai';
  text: string;
  timestamp?: string;
  metadata?: MessageMetadata;
  isError?: boolean;
}

export const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  sender, 
  text, 
  timestamp, 
  metadata, 
  isError = false 
}) => {
  const isUser = sender === 'user';
  const [showMetadata, setShowMetadata] = useState(false);
  const [copied, setCopied] = useState(false);

  const formatTimestamp = (timestamp?: string) => {
    if (!timestamp) return '';
    return new Date(timestamp).toLocaleTimeString('en-US', {
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const handleCopy = async (content: string) => {
    try {
      await navigator.clipboard.writeText(content);
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    } catch (error) {
      console.error('Failed to copy:', error);
    }
  };

  const getIntentColor = (intent?: string) => {
    switch (intent?.toLowerCase()) {
      case 'search_logs': return 'text-blue-400';
      case 'investigate_threat': return 'text-red-400';
      case 'generate_report': return 'text-green-400';
      case 'analyze_anomaly': return 'text-yellow-400';
      default: return 'text-space-400';
    }
  };

  const getConfidenceColor = (confidence?: number) => {
    if (!confidence) return 'text-gray-400';
    if (confidence >= 0.8) return 'text-green-400';
    if (confidence >= 0.6) return 'text-yellow-400';
    return 'text-red-400';
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 10, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ duration: 0.3, ease: 'easeOut' }}
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} mb-6`}
    >
      <div className={`flex ${isUser ? 'flex-row-reverse' : 'flex-row'} items-start space-x-3 max-w-4xl`}>
        {/* Avatar */}
        <div className={`flex-shrink-0 w-8 h-8 rounded-full flex items-center justify-center shadow-lg ${
          isUser 
            ? 'bg-space-gradient' 
            : isError 
              ? 'bg-gradient-to-br from-red-500 to-red-600' 
              : 'bg-gradient-to-br from-cyber-accent to-space-500'
        }`}>
          {isUser ? (
            <User className="w-4 h-4 text-white" />
          ) : isError ? (
            <AlertTriangle className="w-4 h-4 text-white" />
          ) : (
            <Bot className="w-4 h-4 text-white" />
          )}
        </div>

        {/* Message Content */}
        <div className={`${isUser ? 'mr-3' : 'ml-3'} flex-1`}>
          {/* Main Message */}
          <div className={`
            relative p-4 rounded-2xl shadow-lg backdrop-blur-sm border group
            ${
              isUser
                ? 'bg-space-gradient text-white border-space-600/50'
                : isError
                  ? 'bg-gradient-to-br from-red-950/80 to-red-900/60 text-red-100 border-red-500/50'
                  : 'bg-gradient-to-br from-cyber-dark/90 to-space-950/80 text-space-100 border-space-700/50'
            }
          `}>
            {/* Copy button */}
            <button
              onClick={() => handleCopy(text)}
              className={`absolute top-2 right-2 p-1 rounded opacity-0 group-hover:opacity-100 transition-opacity ${
                isUser ? 'hover:bg-white/20' : 'hover:bg-space-800/50'
              }`}
              title="Copy message"
            >
              {copied ? (
                <Check className="w-3 h-3 text-green-400" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
            </button>

            <p className="text-sm leading-relaxed pr-8">
              {text}
            </p>

            {/* Timestamp */}
            {timestamp && (
              <div className={`flex items-center mt-2 text-xs opacity-70 ${
                isUser ? 'justify-end' : 'justify-start'
              }`}>
                <Clock className="w-3 h-3 mr-1" />
                <span>{formatTimestamp(timestamp)}</span>
              </div>
            )}
          </div>

          {/* Metadata Section */}
          {metadata && !isUser && (
            <div className="mt-2">
              <motion.button
                onClick={() => setShowMetadata(!showMetadata)}
                className="flex items-center space-x-2 text-xs text-space-400 hover:text-space-300 transition-colors"
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <Database className="w-3 h-3" />
                <span>Query Details</span>
                {showMetadata ? <ChevronUp className="w-3 h-3" /> : <ChevronDown className="w-3 h-3" />}
              </motion.button>

              <AnimatePresence>
                {showMetadata && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: 'auto' }}
                    exit={{ opacity: 0, height: 0 }}
                    transition={{ duration: 0.2 }}
                    className="mt-2 p-3 bg-cyber-dark/50 rounded-lg border border-space-800/30 text-xs space-y-2"
                  >
                    {/* Intent & Confidence */}
                    {metadata.intent && (
                      <div className="flex items-center justify-between">
                        <span className="text-space-400">Intent:</span>
                        <span className={getIntentColor(metadata.intent)}>
                          {metadata.intent.replace('_', ' ').toUpperCase()}
                          {metadata.confidence && (
                            <span className={`ml-2 ${getConfidenceColor(metadata.confidence)}`}>
                              ({Math.round(metadata.confidence * 100)}%)
                            </span>
                          )}
                        </span>
                      </div>
                    )}

                    {/* Platform */}
                    {metadata.platform && (
                      <div className="flex items-center justify-between">
                        <span className="text-space-400">Platform:</span>
                        <span className="text-cyber-accent capitalize">
                          {metadata.platform}
                        </span>
                      </div>
                    )}

                    {/* Results & Performance */}
                    <div className="grid grid-cols-2 gap-4">
                      {metadata.results_count !== undefined && (
                        <div className="flex items-center space-x-1">
                          <Database className="w-3 h-3 text-space-400" />
                          <span className="text-space-400">Results:</span>
                          <span className="text-space-200">{metadata.results_count.toLocaleString()}</span>
                        </div>
                      )}
                      
                      {metadata.execution_time && (
                        <div className="flex items-center space-x-1">
                          <Zap className="w-3 h-3 text-space-400" />
                          <span className="text-space-400">Time:</span>
                          <span className="text-space-200">{metadata.execution_time}ms</span>
                        </div>
                      )}
                    </div>

                    {/* Entities */}
                    {metadata.entities && Object.keys(metadata.entities).length > 0 && (
                      <div>
                        <div className="text-space-400 mb-1">Detected Entities:</div>
                        <div className="flex flex-wrap gap-1">
                          {Object.entries(metadata.entities).map(([key, value]) => (
                            <span 
                              key={key}
                              className="px-2 py-1 bg-space-800/50 rounded text-cyber-accent text-xs"
                            >
                              {key}: {Array.isArray(value) ? value.join(', ') : String(value)}
                            </span>
                          ))}
                        </div>
                      </div>
                    )}

                    {/* DSL Query Preview */}
                    {metadata.query?.dsl && (
                      <div>
                        <div className="flex items-center justify-between mb-1">
                          <span className="text-space-400">Generated Query:</span>
                          <button
                            onClick={() => handleCopy(JSON.stringify(metadata.query?.dsl, null, 2))}
                            className="text-cyber-accent hover:text-cyber-accent/80 transition-colors"
                            title="Copy DSL query"
                          >
                            <Copy className="w-3 h-3" />
                          </button>
                        </div>
                        <pre className="bg-cyber-darker p-2 rounded text-xs text-space-300 overflow-x-auto font-mono">
                          {JSON.stringify(metadata.query.dsl, null, 2)}
                        </pre>
                      </div>
                    )}
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          )}
        </div>
      </div>
    </motion.div>
  );
};
