/**
 * SIEM AI Assistant Chat Interface
 * Real-time chat with SIEM AI for security analysis and assistance
 */

import React, { useState, useEffect, useRef, useCallback } from 'react';
import {
  Send,
  Bot,
  User,
  Zap,
  Shield,
  AlertTriangle,
  Search,
  FileText,
  Settings,
  RotateCcw,
  Copy,
  ThumbsUp,
  ThumbsDown,
  MessageSquare,
  Sparkles,
  Terminal,
  Code,
  Database,
  Lock,
  Unlock,
  Eye,
  EyeOff,
  Download,
  Upload,
  Calendar,
  Clock,
  TrendingUp,
  BarChart3,
  PieChart,
  Activity,
  Wifi,
  WifiOff,
  Server,
  Cloud,
  HardDrive,
  Cpu,
  // Memory, // Not available in this version
  Network,
  Globe,
  MapPin,
  Filter,
  Layers,
  Hash,
  Key,
  Fingerprint,
  Bug,
  Crosshair,
  Target,
  Radar,
  Flame,
  Skull,
  ShieldAlert,
  ShieldCheck,
  ShieldX,
  Plus,
  Minus,
  X,
  Check,
  Info,
  HelpCircle,
  Lightbulb,
  BookOpen,
  FileCode,
  Monitor,
  Smartphone,
  Laptop,
  Users,
  UserCheck,
  UserX,
  Crown,
  Star
} from 'lucide-react';

import { useApiClient, ChatMessage } from '../services/api.service';
import { useAppStore } from '../store/appStore';
import { useNotifications } from './ui/NotificationSystem';
import { ChatSkeleton, LoadingButton, InlineLoading } from './ui/LoadingStates';
import { ChatErrorBoundary } from './ErrorBoundary';

interface ChatInterfaceProps {
  className?: string;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ className = '' }) => {
  return (
    <ChatErrorBoundary>
      <div className={`h-full bg-gray-900 text-white ${className}`}>
        <ChatContent />
      </div>
    </ChatErrorBoundary>
  );
};

const ChatContent: React.FC = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [chatMessages, setChatMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string>('');

  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Hooks
  const { api, callApi } = useApiClient();
  const { currentSessionId, setCurrentSessionId, addChatMessage } = useAppStore();
  const { showError, showSuccess } = useNotifications();

  // Initialize chat session
  useEffect(() => {
    const initializeChat = async () => {
      try {
        const sessionResponse = await callApi(
          () => api.createChatSession(),
          {
            onSuccess: (data) => {
              setSessionId(data.sessionId);
              setCurrentSessionId(data.sessionId);
            }
          }
        );

        // Load chat history if available
        if (sessionResponse?.sessionId) {
          await callApi(
            () => api.getChatHistory(sessionResponse.sessionId),
            {
              onSuccess: (history) => {
                setChatMessages(history);
              }
            }
          );
        }
      } catch (error) {
        console.error('Failed to initialize chat:', error);
      }
    };

    initializeChat();
  }, [api, callApi, setCurrentSessionId]);

  // Auto-scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSendMessage = useCallback(async () => {
    if (!message.trim() || isLoading) return;

    const userMessage: ChatMessage = {
      id: `user_${Date.now()}`,
      content: message.trim(),
      role: 'user',
      timestamp: new Date().toISOString()
    };

    // Add user message immediately
    setChatMessages(prev => [...prev, userMessage]);
    addChatMessage(userMessage);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await callApi(
        () => api.sendChatMessage(message.trim(), sessionId),
        {
          onSuccess: (aiResponse) => {
            setChatMessages(prev => [...prev, aiResponse]);
            addChatMessage(aiResponse);
          },
          onError: (error) => {
            // Add error message to chat
            const errorMessage: ChatMessage = {
              id: `error_${Date.now()}`,
              content: "I'm sorry, I encountered an error processing your request. Please try again or contact support if the issue persists.",
              role: 'assistant',
              timestamp: new Date().toISOString(),
              metadata: { error: true }
            };
            setChatMessages(prev => [...prev, errorMessage]);
          }
        }
      );
    } catch (error) {
      console.error('Failed to send message:', error);
    } finally {
      setIsLoading(false);
      inputRef.current?.focus();
    }
  }, [message, isLoading, sessionId, api, callApi, addChatMessage]);

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  const clearChat = useCallback(() => {
    setChatMessages([]);
    setCurrentSessionId(`session_${Date.now()}`);
    showSuccess('Chat Cleared', 'Started a new conversation');
  }, [setCurrentSessionId, showSuccess]);

  const copyMessage = useCallback((content: string) => {
    navigator.clipboard.writeText(content);
    showSuccess('Copied', 'Message copied to clipboard');
  }, [showSuccess]);

  const regenerateResponse = useCallback(async (messageIndex: number) => {
    const previousMessage = chatMessages[messageIndex - 1];
    if (!previousMessage || previousMessage.role !== 'user') return;

    // Remove the AI response we want to regenerate
    setChatMessages(prev => prev.slice(0, messageIndex));
    setIsLoading(true);

    try {
      await callApi(
        () => api.sendChatMessage(previousMessage.content, sessionId),
        {
          onSuccess: (aiResponse) => {
            setChatMessages(prev => [...prev, aiResponse]);
            addChatMessage(aiResponse);
          }
        }
      );
    } catch (error) {
      console.error('Failed to regenerate response:', error);
    } finally {
      setIsLoading(false);
    }
  }, [chatMessages, sessionId, api, callApi, addChatMessage]);

  if (chatMessages.length === 0 && isLoading) {
    return <ChatSkeleton />;
  }

  return (
    <div className="flex flex-col h-full">
      {/* Header */}
      <div className="border-b border-gray-700 bg-gradient-to-r from-gray-800 to-gray-900">
        <div className="flex items-center justify-between p-4">
          <div className="flex items-center space-x-4">
            <div className="relative">
              <div className="p-2 bg-gradient-to-br from-blue-600 to-purple-600 rounded-xl shadow-lg">
                <Sparkles className="w-6 h-6 text-white" />
              </div>
              <div className="absolute -top-1 -right-1 w-3 h-3 bg-green-400 rounded-full animate-pulse shadow-sm" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-white flex items-center space-x-2">
                <span>KARTAVYA AI</span>
                <div className="px-2 py-1 bg-gradient-to-r from-blue-600 to-purple-600 text-xs font-semibold rounded-full text-white">
                  SIEM GPT
                </div>
              </h2>
              <p className="text-sm text-gray-400 flex items-center space-x-2">
                <ShieldCheck className="w-4 h-4 text-green-400" />
                <span>Advanced Security Intelligence • Real-time Analysis • Threat Hunting</span>
              </p>
            </div>
          </div>
          
          <div className="flex items-center space-x-3">
            {/* Model Info */}
            <div className="hidden md:flex items-center space-x-2 px-3 py-1 bg-gray-700 rounded-lg border border-gray-600">
              <div className="w-2 h-2 bg-blue-400 rounded-full animate-pulse" />
              <span className="text-xs text-gray-300 font-medium">GPT-4 Turbo</span>
            </div>
            
            {/* Quick Actions */}
            <div className="flex items-center space-x-1">
              <button
                onClick={clearChat}
                className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all hover:scale-105"
                title="New conversation"
              >
                <Plus className="w-4 h-4" />
              </button>
              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all hover:scale-105">
                <BookOpen className="w-4 h-4" />
              </button>
              <button className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all hover:scale-105">
                <Settings className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
        
        {/* Quick Tools Bar */}
        <div className="px-4 pb-3">
          <div className="flex items-center space-x-2 overflow-x-auto">
            <QuickToolButton icon={<Terminal />} label="Query Builder" color="blue" />
            <QuickToolButton icon={<Code />} label="Code Analysis" color="green" />
            <QuickToolButton icon={<Database />} label="Log Parser" color="purple" />
            <QuickToolButton icon={<Target />} label="Threat Hunt" color="red" />
            <QuickToolButton icon={<BarChart3 />} label="Analytics" color="yellow" />
            <QuickToolButton icon={<FileText />} label="Report Gen" color="cyan" />
          </div>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {chatMessages.length === 0 ? (
          <WelcomeScreen onSuggestedQuery={setMessage} />
        ) : (
          chatMessages.map((msg, index) => (
            <MessageBubble
              key={msg.id}
              message={msg}
              isLast={index === chatMessages.length - 1}
              onCopy={() => copyMessage(msg.content)}
              onRegenerate={() => regenerateResponse(index)}
              showRegenerate={msg.role === 'assistant' && index === chatMessages.length - 1}
            />
          ))
        )}

        {/* Typing indicator */}
        {isLoading && (
          <div className="flex items-start space-x-3">
            <Bot className="w-8 h-8 text-blue-400 mt-1" />
            <div className="bg-gray-800 rounded-lg p-3 max-w-xs">
              <div className="flex space-x-1">
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }} />
                <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }} />
              </div>
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 bg-gray-800 p-4">
        <div className="flex items-end space-x-3">
          <div className="flex-1 relative">
            <input
              ref={inputRef}
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyPress={handleKeyPress}
              placeholder="Ask about security threats, analyze logs, get recommendations..."
              disabled={isLoading}
              className="w-full bg-gray-700 border border-gray-600 rounded-lg px-4 py-3 pr-12 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none disabled:opacity-50"
            />
            {message.trim() && (
              <button
                onClick={handleSendMessage}
                disabled={isLoading}
                className="absolute right-2 top-1/2 transform -translate-y-1/2 p-2 text-blue-400 hover:text-blue-300 disabled:text-gray-500 disabled:cursor-not-allowed"
              >
                <Send className="w-5 h-5" />
              </button>
            )}
          </div>
          
          <LoadingButton
            loading={isLoading}
            onClick={handleSendMessage}
            disabled={!message.trim()}
            className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600"
          >
            <Send className="w-4 h-4" />
            Send
          </LoadingButton>
        </div>
        
        <p className="text-xs text-gray-500 mt-2 text-center">
          AI responses may contain errors. Always verify critical security information.
        </p>
      </div>
    </div>
  );
};

// ============= COMPONENT DEFINITIONS =============

// Quick Tool Button Component
interface QuickToolButtonProps {
  icon: React.ReactNode;
  label: string;
  color: 'blue' | 'green' | 'purple' | 'red' | 'yellow' | 'cyan';
  onClick?: () => void;
}

const QuickToolButton: React.FC<QuickToolButtonProps> = ({ icon, label, color, onClick }) => {
  const colorClasses = {
    blue: 'text-blue-400 border-blue-700/50 hover:bg-blue-900/30',
    green: 'text-green-400 border-green-700/50 hover:bg-green-900/30',
    purple: 'text-purple-400 border-purple-700/50 hover:bg-purple-900/30',
    red: 'text-red-400 border-red-700/50 hover:bg-red-900/30',
    yellow: 'text-yellow-400 border-yellow-700/50 hover:bg-yellow-900/30',
    cyan: 'text-cyan-400 border-cyan-700/50 hover:bg-cyan-900/30'
  };

  return (
    <button
      onClick={onClick}
      className={`flex items-center space-x-2 px-3 py-2 bg-gray-800 border rounded-lg transition-all hover:scale-105 ${colorClasses[color]}`}
    >
      <div className="w-4 h-4">{icon}</div>
      <span className="text-xs font-medium whitespace-nowrap">{label}</span>
    </button>
  );
};

const WelcomeScreen: React.FC<{ onSuggestedQuery: (query: string) => void }> = ({ onSuggestedQuery }) => {
  const suggestions = [
    {
      icon: <ShieldAlert className="w-6 h-6 text-red-400" />,
      title: "Critical Threat Analysis",
      description: "Analyze high-severity security alerts and threats",
      query: "Show me all critical security alerts from the last 24 hours with detailed analysis and recommended actions",
      category: "Threat Intelligence"
    },
    {
      icon: <Terminal className="w-6 h-6 text-green-400" />,
      title: "Advanced Query Building",
      description: "Build complex SIEM queries and searches",
      query: "Help me build a KQL query to find suspicious PowerShell executions with network connections in the last 48 hours",
      category: "Query & Search"
    },
    {
      icon: <Bug className="w-6 h-6 text-orange-400" />,
      title: "Malware Investigation",
      description: "Deep dive into malware artifacts and IOCs",
      query: "Analyze this suspicious file hash and provide a comprehensive malware investigation report with MITRE ATT&CK mapping",
      category: "Forensics"
    },
    {
      icon: <Network className="w-6 h-6 text-purple-400" />,
      title: "Network Traffic Analysis",
      description: "Investigate network anomalies and traffic patterns",
      query: "Examine unusual network traffic patterns and identify potential data exfiltration or C2 communications",
      category: "Network Security"
    },
    {
      icon: <Users className="w-6 h-6 text-blue-400" />,
      title: "User Behavior Analytics",
      description: "Detect insider threats and user anomalies",
      query: "Analyze user login patterns and detect potential insider threats or compromised accounts",
      category: "Identity & Access"
    },
    {
      icon: <FileCode className="w-6 h-6 text-yellow-400" />,
      title: "Incident Response Playbook",
      description: "Generate IR procedures and runbooks",
      query: "Create a detailed incident response playbook for a suspected ransomware attack",
      category: "Incident Response"
    },
    {
      icon: <BarChart3 className="w-6 h-6 text-cyan-400" />,
      title: "Security Metrics & Reporting",
      description: "Generate executive security reports",
      query: "Create a comprehensive security posture report with key metrics, trends, and executive summary",
      category: "Reporting"
    },
    {
      icon: <Crosshair className="w-6 h-6 text-red-500" />,
      title: "Threat Hunting Campaign",
      description: "Proactive threat hunting methodology",
      query: "Design a threat hunting campaign to detect advanced persistent threats in our environment",
      category: "Threat Hunting"
    }
  ];

  const categories = Array.from(new Set(suggestions.map(s => s.category)));

  return (
    <div className="h-full overflow-y-auto p-6 space-y-8">
      {/* Hero Section */}
      <div className="text-center space-y-6">
        <div className="relative inline-block">
          <div className="p-4 bg-gradient-to-br from-blue-600 via-purple-600 to-cyan-600 rounded-2xl shadow-2xl">
            <Sparkles className="w-12 h-12 text-white" />
          </div>
          <div className="absolute -top-2 -right-2 w-6 h-6 bg-green-400 rounded-full flex items-center justify-center shadow-lg">
            <Check className="w-3 h-3 text-white" />
          </div>
        </div>
        
        <div className="space-y-3">
          <h1 className="text-3xl font-bold text-white flex items-center justify-center space-x-3">
            <span>KARTAVYA AI</span>
            <div className="px-3 py-1 bg-gradient-to-r from-blue-600 to-purple-600 text-sm font-bold rounded-full">
              SIEM GPT
            </div>
          </h1>
          <p className="text-gray-300 text-lg max-w-2xl mx-auto">
            Your intelligent security operations partner. I provide advanced threat analysis, 
            incident response guidance, and SIEM expertise at enterprise scale.
          </p>
        </div>
        
        {/* Capabilities Badge */}
        <div className="flex items-center justify-center flex-wrap gap-3">
          <div className="flex items-center space-x-2 px-3 py-1 bg-gray-800 border border-blue-700/50 rounded-full">
            <ShieldCheck className="w-4 h-4 text-green-400" />
            <span className="text-sm text-gray-300">Real-time Analysis</span>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-gray-800 border border-purple-700/50 rounded-full">
            <Code className="w-4 h-4 text-purple-400" />
            <span className="text-sm text-gray-300">Code Intelligence</span>
          </div>
          <div className="flex items-center space-x-2 px-3 py-1 bg-gray-800 border border-red-700/50 rounded-full">
            <Target className="w-4 h-4 text-red-400" />
            <span className="text-sm text-gray-300">Threat Hunting</span>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="space-y-6">
        <h2 className="text-xl font-semibold text-white text-center">What would you like to do today?</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {suggestions.map((suggestion, index) => (
            <button
              key={index}
              onClick={() => onSuggestedQuery(suggestion.query)}
              className="group p-5 bg-gray-800 border border-gray-700 rounded-xl hover:bg-gray-750 hover:border-gray-600 transition-all duration-300 text-left hover:scale-105 hover:shadow-lg"
            >
              <div className="flex items-start space-x-4">
                <div className="p-3 bg-gray-700 rounded-lg group-hover:bg-gray-600 transition-colors">
                  {suggestion.icon}
                </div>
                <div className="flex-1 space-y-2">
                  <div className="flex items-center justify-between">
                    <h3 className="font-semibold text-white group-hover:text-blue-400 transition-colors">
                      {suggestion.title}
                    </h3>
                    <span className="text-xs px-2 py-1 bg-gray-700 text-gray-300 rounded-full">
                      {suggestion.category}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 group-hover:text-gray-300 transition-colors">
                    {suggestion.description}
                  </p>
                </div>
              </div>
            </button>
          ))}
        </div>
      </div>

      {/* Additional Features */}
      <div className="border-t border-gray-700 pt-6">
        <div className="text-center space-y-4">
          <h3 className="text-lg font-semibold text-white">Advanced Capabilities</h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <CapabilityCard icon={<Code />} title="Code Analysis" description="Security code review" />
            <CapabilityCard icon={<Database />} title="Log Analysis" description="Multi-format parsing" />
            <CapabilityCard icon={<Radar />} title="Threat Intel" description="Real-time feeds" />
            <CapabilityCard icon={<FileText />} title="Report Gen" description="Executive summaries" />
          </div>
        </div>
      </div>
    </div>
  );
};

// Capability Card Component
interface CapabilityCardProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const CapabilityCard: React.FC<CapabilityCardProps> = ({ icon, title, description }) => (
  <div className="p-3 bg-gray-800 border border-gray-700 rounded-lg text-center hover:bg-gray-750 transition-colors">
    <div className="text-blue-400 mb-2 flex justify-center">{icon}</div>
    <h4 className="text-sm font-semibold text-white mb-1">{title}</h4>
    <p className="text-xs text-gray-400">{description}</p>
  </div>
);

interface MessageBubbleProps {
  message: ChatMessage;
  isLast: boolean;
  onCopy: () => void;
  onRegenerate: () => void;
  showRegenerate: boolean;
}

const MessageBubble: React.FC<MessageBubbleProps> = ({ 
  message, 
  isLast, 
  onCopy, 
  onRegenerate, 
  showRegenerate 
}) => {
  const [showActions, setShowActions] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);

  const isUser = message.role === 'user';
  const isError = message.metadata?.error;
  const isAI = message.role === 'assistant';

  // Enhanced message formatting with code detection
  const formatMessageContent = (content: string) => {
    // Check for code blocks
    const codeBlockRegex = /```([\w]*)?\n([\s\S]*?)\n```/g;
    const inlineCodeRegex = /`([^`]+)`/g;
    
    const parts = [];
    let lastIndex = 0;
    let match;

    // Handle code blocks
    while ((match = codeBlockRegex.exec(content)) !== null) {
      // Add text before code block
      if (match.index > lastIndex) {
        parts.push({
          type: 'text',
          content: content.slice(lastIndex, match.index)
        });
      }
      
      // Add code block
      parts.push({
        type: 'code-block',
        language: match[1] || 'text',
        content: match[2].trim()
      });
      
      lastIndex = match.index + match[0].length;
    }
    
    // Add remaining text
    if (lastIndex < content.length) {
      parts.push({
        type: 'text',
        content: content.slice(lastIndex)
      });
    }
    
    return parts.length > 0 ? parts : [{ type: 'text', content }];
  };

  const renderFormattedContent = () => {
    const parts = formatMessageContent(message.content);
    
    return (
      <div className="space-y-3">
        {parts.map((part, index) => {
          if (part.type === 'code-block') {
            return (
              <CodeBlock
                key={index}
                code={part.content}
                language={part.language ?? 'plaintext'}
                onCopy={() => navigator.clipboard.writeText(part.content)}
              />
            );
          } else {
            return (
              <div key={index} className="whitespace-pre-wrap break-words">
                {part.content.replace(/`([^`]+)`/g, (match, code) => (
                  `<code class="inline-code">${code}</code>`
                ))}
              </div>
            );
          }
        })}
      </div>
    );
  };

  return (
    <div 
      className={`flex ${isUser ? 'justify-end' : 'justify-start'} group`}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      <div className={`flex items-start space-x-3 max-w-4xl ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
        {/* Enhanced Avatar */}
        <div className={`flex-shrink-0 w-10 h-10 rounded-xl flex items-center justify-center shadow-lg ${
          isUser 
            ? 'bg-gradient-to-br from-blue-600 to-blue-700' 
            : isError 
              ? 'bg-gradient-to-br from-red-600 to-red-700' 
              : 'bg-gradient-to-br from-purple-600 to-blue-600'
        }`}>
          {isUser ? (
            <User className="w-5 h-5 text-white" />
          ) : isError ? (
            <AlertTriangle className="w-5 h-5 text-white" />
          ) : (
            <div className="relative">
              <Sparkles className="w-5 h-5 text-white" />
              <div className="absolute -top-1 -right-1 w-2 h-2 bg-green-400 rounded-full animate-pulse" />
            </div>
          )}
        </div>

        {/* Enhanced Message */}
        <div className={`flex flex-col space-y-3 ${isUser ? 'items-end' : 'items-start'} flex-1`}>
          {/* Message Role Badge */}
          {isAI && (
            <div className="flex items-center space-x-2">
              <div className="px-2 py-1 bg-gradient-to-r from-purple-600 to-blue-600 text-xs font-semibold rounded-full text-white">
                KARTAVYA AI
              </div>
              <div className="text-xs text-gray-400">
                {new Date(message.timestamp).toLocaleString()}
              </div>
            </div>
          )}
          
          <div className={`relative px-6 py-4 rounded-2xl shadow-lg ${
            isUser 
              ? 'bg-gradient-to-br from-blue-600 to-blue-700 text-white' 
              : isError 
                ? 'bg-red-900/50 border border-red-700 text-red-100'
                : 'bg-gray-800 text-white border border-gray-700 hover:bg-gray-750 transition-colors'
          }`}>
            {renderFormattedContent()}

            {/* Enhanced Metadata */}
            {message.metadata && !isError && (
              <div className="mt-4 pt-4 border-t border-gray-600 space-y-3">
                {/* SIEM Analysis Results */}
                {message.metadata.siemAnalysis && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold text-blue-400 flex items-center space-x-2">
                      <ShieldAlert className="w-4 h-4" />
                      <span>SIEM Analysis</span>
                    </h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                      <div className="p-3 bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-400">Threat Level</div>
                        <div className="text-sm font-semibold text-red-400">
                          {message.metadata.siemAnalysis.threatLevel || 'Medium'}
                        </div>
                      </div>
                      <div className="p-3 bg-gray-700 rounded-lg">
                        <div className="text-xs text-gray-400">IOCs Found</div>
                        <div className="text-sm font-semibold text-yellow-400">
                          {message.metadata.siemAnalysis.iocCount || 0}
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Sources */}
                {message.metadata.sources && (
                  <div>
                    <p className="text-sm font-semibold text-green-400 mb-2 flex items-center space-x-2">
                      <Database className="w-4 h-4" />
                      <span>Data Sources</span>
                    </p>
                    <div className="flex flex-wrap gap-2">
                      {message.metadata.sources.map((source, index) => (
                        <span key={index} className="text-xs bg-gray-700 border border-gray-600 px-3 py-1 rounded-full flex items-center space-x-1">
                          <div className="w-2 h-2 bg-green-400 rounded-full" />
                          <span>{source}</span>
                        </span>
                      ))}
                    </div>
                  </div>
                )}
                
                {/* Confidence Score */}
                {message.metadata.confidence && (
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Analysis Confidence</span>
                    <div className="flex items-center space-x-2">
                      <div className="w-24 bg-gray-700 rounded-full h-2">
                        <div 
                          className="bg-gradient-to-r from-green-400 to-green-500 h-2 rounded-full transition-all duration-1000"
                          style={{ width: `${message.metadata.confidence * 100}%` }}
                        />
                      </div>
                      <span className="text-sm font-semibold text-green-400">
                        {Math.round(message.metadata.confidence * 100)}%
                      </span>
                    </div>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Enhanced Actions */}
          <div className={`flex items-center space-x-2 transition-opacity duration-200 ${showActions ? 'opacity-100' : 'opacity-0'} ${isUser ? 'flex-row-reverse space-x-reverse' : ''}`}>
            <button
              onClick={onCopy}
              className="p-2 text-gray-400 hover:text-white hover:bg-gray-700 rounded-lg transition-all hover:scale-105"
              title="Copy message"
            >
              <Copy className="w-4 h-4" />
            </button>
            
            {!isUser && (
              <>
                <button className="p-2 text-gray-400 hover:text-green-400 hover:bg-gray-700 rounded-lg transition-all hover:scale-105">
                  <ThumbsUp className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-red-400 hover:bg-gray-700 rounded-lg transition-all hover:scale-105">
                  <ThumbsDown className="w-4 h-4" />
                </button>
                <button className="p-2 text-gray-400 hover:text-blue-400 hover:bg-gray-700 rounded-lg transition-all hover:scale-105">
                  <Download className="w-4 h-4" />
                </button>
                {showRegenerate && (
                  <button
                    onClick={onRegenerate}
                    className="p-2 text-gray-400 hover:text-purple-400 hover:bg-gray-700 rounded-lg transition-all hover:scale-105"
                    title="Regenerate response"
                  >
                    <RotateCcw className="w-4 h-4" />
                  </button>
                )}
              </>
            )}
          </div>

          {/* Timestamp for user messages */}
          {isUser && (
            <div className="text-xs text-gray-500 text-right">
              {new Date(message.timestamp).toLocaleTimeString()}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

// Code Block Component with Syntax Highlighting
interface CodeBlockProps {
  code: string;
  language: string;
  onCopy: () => void;
}

const CodeBlock: React.FC<CodeBlockProps> = ({ code, language, onCopy }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    onCopy();
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const getLanguageIcon = (lang: string) => {
    switch (lang.toLowerCase()) {
      case 'kql': case 'kusto': return <Database className="w-4 h-4" />;
      case 'sql': return <Database className="w-4 h-4" />;
      case 'powershell': case 'ps1': return <Terminal className="w-4 h-4" />;
      case 'bash': case 'sh': return <Terminal className="w-4 h-4" />;
      case 'python': case 'py': return <Code className="w-4 h-4" />;
      case 'json': return <FileCode className="w-4 h-4" />;
      case 'yaml': case 'yml': return <FileCode className="w-4 h-4" />;
      default: return <Code className="w-4 h-4" />;
    }
  };

  return (
    <div className="bg-gray-900 border border-gray-600 rounded-lg overflow-hidden">
      {/* Code Header */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-800 border-b border-gray-600">
        <div className="flex items-center space-x-2 text-sm text-gray-300">
          <div className="text-blue-400">{getLanguageIcon(language)}</div>
          <span className="font-mono font-semibold">{language.toUpperCase() || 'CODE'}</span>
        </div>
        <button
          onClick={handleCopy}
          className="flex items-center space-x-1 px-2 py-1 text-xs text-gray-400 hover:text-white hover:bg-gray-700 rounded transition-colors"
        >
          {copied ? <Check className="w-3 h-3 text-green-400" /> : <Copy className="w-3 h-3" />}
          <span>{copied ? 'Copied!' : 'Copy'}</span>
        </button>
      </div>
      
      {/* Code Content */}
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm text-gray-200 font-mono whitespace-pre-wrap break-all">
          <code>{code}</code>
        </pre>
      </div>
    </div>
  );
};

export default ChatInterface;
