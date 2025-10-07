import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { MessageBubble } from './MessageBubble';
import { QueryInput } from './QueryInput';
import { useChatStore } from '../store/useChatStore';
import { api } from '../services/api';
import { config, isDemo, isMockSiem, labels } from '../config/environment';
import { Shield, Database, Cpu, AlertTriangle } from 'lucide-react';

interface ChatWindowProps {
  onSendMessage?: (message: string) => void;
}

interface ApiResponse {
  response: string;
  query_executed?: {
    dsl: any;
    index: string;
  };
  entities?: Record<string, any>;
  intent?: string;
  confidence?: number;
  results?: any[];
  metadata?: {
    total_hits: number;
    execution_time: number;
    platform: string;
  };
}

export const ChatWindow: React.FC<ChatWindowProps> = ({ onSendMessage }) => {
  const { messages, addMessage, isLoading, setLoading } = useChatStore();
  const [connectionStatus, setConnectionStatus] = useState<'connected' | 'connecting' | 'disconnected'>('connecting');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Check backend connection on mount
  useEffect(() => {
    checkConnection();
  }, []);

  const checkConnection = async () => {
    try {
      setConnectionStatus('connecting');
      await api.get('/health');
      setConnectionStatus('connected');
    } catch (error) {
      setConnectionStatus('disconnected');
      console.error('Backend connection failed:', error);
    }
  };

  const handleSendMessage = async (message: string) => {
    // Add user message
    addMessage({ 
      sender: 'user', 
      text: message, 
      timestamp: new Date().toISOString() 
    });

    // Set loading state
    setLoading(true);

    try {
      // Call the real backend API
      const response: ApiResponse = await api.post('/api/assistant/chat', {
        query: message,
        session_id: `session_${Date.now()}`,
        context: {},
        siem_platform: config.siemPlatform
      });

      // Add AI response with metadata
      addMessage({
        sender: 'ai',
        text: response.response,
        timestamp: new Date().toISOString(),
        metadata: {
          intent: response.intent,
          confidence: response.confidence,
          entities: response.entities,
          query: response.query_executed,
          results_count: response.metadata?.total_hits,
          execution_time: response.metadata?.execution_time,
          platform: response.metadata?.platform || config.siemPlatform
        }
      });

    } catch (error) {
      console.error('Chat API error:', error);
      
      // Add error message
      addMessage({
        sender: 'ai',
        text: `I encountered an error while processing your request: ${error instanceof Error ? error.message : 'Unknown error'}. Please check your connection and try again.`,
        timestamp: new Date().toISOString(),
        isError: true
      });
    } finally {
      setLoading(false);
    }

    // Call optional callback
    if (onSendMessage) {
      onSendMessage(message);
    }
  };

  const getConnectionStatusColor = () => {
    switch (connectionStatus) {
      case 'connected': return 'text-cyber-green';
      case 'connecting': return 'text-cyber-yellow';
      case 'disconnected': return 'text-cyber-red';
    }
  };

  const getSiemIcon = () => {
    switch (config.siemPlatform) {
      case 'elasticsearch': return <Database className="w-4 h-4" />;
      case 'wazuh': return <Shield className="w-4 h-4" />;
      case 'mock': return <Cpu className="w-4 h-4" />;
    }
  };

  return (
    <div className="flex flex-col h-full bg-cyber-darker">
      {/* Header with connection status */}
      <div className="flex items-center justify-between p-4 border-b border-space-800/50 bg-gradient-to-r from-space-950 to-cyber-dark">
        <div className="flex items-center space-x-3">
          <div className="flex items-center space-x-2">
            {getSiemIcon()}
            <span className="text-sm font-medium text-space-300">
              {labels.siem[config.siemPlatform]}
            </span>
          </div>
          
          <div className="w-px h-4 bg-space-700" />
          
          <div className="flex items-center space-x-2">
            <div className={`w-2 h-2 rounded-full ${connectionStatus === 'connected' ? 'bg-cyber-green animate-pulse' : connectionStatus === 'connecting' ? 'bg-cyber-yellow animate-pulse' : 'bg-cyber-red'}`} />
            <span className={`text-xs ${getConnectionStatusColor()}`}>
              {connectionStatus === 'connected' ? 'Connected' : connectionStatus === 'connecting' ? 'Connecting...' : 'Disconnected'}
            </span>
          </div>
        </div>

        {/* Demo mode indicator */}
        {isDemo() && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className="flex items-center space-x-1 px-2 py-1 bg-cyber-accent/20 border border-cyber-accent/30 rounded text-xs text-cyber-accent"
          >
            <AlertTriangle className="w-3 h-3" />
            <span>Demo Mode</span>
          </motion.div>
        )}
      </div>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 bg-cyber-grid">
        <AnimatePresence mode="popLayout">
          {messages.length === 0 ? (
            <motion.div
              key="welcome"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -20 }}
              className="text-center py-12"
            >
              <div className="bg-gradient-to-br from-space-950/80 to-cyber-dark/80 backdrop-blur-sm border border-space-800/50 rounded-2xl p-8 max-w-lg mx-auto shadow-space">
                <div className="mb-4">
                  <div className="w-16 h-16 bg-space-gradient rounded-full mx-auto flex items-center justify-center shadow-cyber">
                    <Shield className="w-8 h-8 text-white" />
                  </div>
                </div>
                
                <h3 className="text-xl font-bold mb-3 text-transparent bg-clip-text bg-gradient-to-r from-space-400 to-cyber-accent">
                  SIEM NLP Assistant
                </h3>
                
                <p className="text-space-300 text-sm mb-4">
                  Ask questions about your security data in natural language
                </p>

                <div className="grid grid-cols-1 gap-2 text-xs text-space-400">
                  <div className="flex items-center justify-center space-x-1">
                    <span>Try:</span>
                    <span className="text-cyber-accent">"Show failed login attempts from yesterday"</span>
                  </div>
                  <div className="flex items-center justify-center space-x-1">
                    <span>Or:</span>
                    <span className="text-cyber-accent">"Generate malware detection report"</span>
                  </div>
                </div>
              </div>
            </motion.div>
          ) : (
            messages.map((message, index) => (
              <MessageBubble
                key={`message-${index}`}
                sender={message.sender}
                text={message.text}
                timestamp={message.timestamp}
                metadata={message.metadata}
                isError={message.isError}
              />
            ))
          )}
        </AnimatePresence>
        
        {/* Loading indicator */}
        {isLoading && (
          <motion.div
            key="loading"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="flex items-center space-x-2 text-space-400 text-sm"
          >
            <div className="flex space-x-1">
              <div className="w-2 h-2 bg-cyber-accent rounded-full animate-bounce" />
              <div className="w-2 h-2 bg-cyber-accent rounded-full animate-bounce" style={{ animationDelay: '0.1s' }} />
              <div className="w-2 h-2 bg-cyber-accent rounded-full animate-bounce" style={{ animationDelay: '0.2s' }} />
            </div>
            <span>Processing your query...</span>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-space-800/50 bg-gradient-to-r from-cyber-dark to-space-950">
        <QueryInput 
          onSendMessage={handleSendMessage}
          disabled={connectionStatus === 'disconnected' || isLoading}
          placeholder={connectionStatus === 'disconnected' ? 'Disconnected - check connection' : 'Ask about your security data...'}
        />
      </div>
    </div>
  );
};
