import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, AlertTriangle, Clock, Database, Filter } from 'lucide-react';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  queryInfo?: {
    intent: string;
    entities: any[];
    query_dsl: string;
    execution_time: number;
    results_count: number;
  };
  results?: any[];
}

interface ChatInterfaceProps {
  isConnected: boolean;
}

const ChatInterface: React.FC<ChatInterfaceProps> = ({ isConnected }) => {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Hello! I\'m your SIEM Assistant. I can help you investigate security events, analyze logs, and generate reports using natural language. Try asking me:\n\n• "Show me failed login attempts from the last hour"\n• "Any malware detections today?"\n• "Find suspicious network activity"\n• "Generate a security summary for yesterday"',
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => `session_${Date.now()}`);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      let response;
      
      if (isConnected) {
        // Real backend call
        const apiResponse = await fetch('http://localhost:8000/api/assistant/chat', {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            message: input,
            session_id: sessionId,
          }),
        });

        if (!apiResponse.ok) {
          throw new Error(`API Error: ${apiResponse.status}`);
        }

        response = await apiResponse.json();
      } else {
        // Mock response for demo
        await new Promise(resolve => setTimeout(resolve, 1000));
        response = generateMockResponse(input);
      }

      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: response.response || response.message,
        timestamp: new Date(),
        queryInfo: response.query_info || response.queryInfo,
        results: response.results,
      };

      setMessages(prev => [...prev, assistantMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'assistant',
        content: `Sorry, I encountered an error: ${error instanceof Error ? error.message : 'Unknown error'}. Please try again or check if the backend is running.`,
        timestamp: new Date(),
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateMockResponse = (query: string): any => {
    const lowerQuery = query.toLowerCase();
    
    if (lowerQuery.includes('failed login') || lowerQuery.includes('login fail')) {
      return {
        message: "I found 47 failed login attempts in the specified timeframe. Here are the key findings:\n\n🔴 **Critical Observations:**\n• 23 attempts from IP 192.168.1.45 (suspicious)\n• 12 attempts targeting admin accounts\n• 8 attempts during off-hours (2-4 AM)\n\n**Top Failed Users:**\n1. admin - 15 attempts\n2. service_account - 8 attempts\n3. backup_user - 6 attempts\n\n**Recommended Actions:**\n• Block IP 192.168.1.45\n• Enable account lockout policies\n• Review admin access permissions",
        queryInfo: {
          intent: "search_events",
          entities: ["failed_login", "time_range"],
          query_dsl: "event.action:login_failed AND @timestamp:[now-1h TO now]",
          execution_time: 247,
          results_count: 47
        },
        results: [
          { timestamp: "2025-01-08T06:30:15Z", user: "admin", source_ip: "192.168.1.45", reason: "invalid_password" },
          { timestamp: "2025-01-08T06:29:33Z", user: "service_account", source_ip: "10.0.0.15", reason: "account_locked" }
        ]
      };
    }
    
    if (lowerQuery.includes('malware') || lowerQuery.includes('virus')) {
      return {
        message: "🦠 **Malware Detection Report**\n\nI found 3 malware incidents in the last 24 hours:\n\n**Active Threats:**\n• Trojan.Win32.Agent - Host: WS-SEC-01\n• Backdoor.Generic - Host: SRV-DB-02\n• Phishing.Email.Suspect - Email Server\n\n**Status:**\n✅ 2 threats quarantined\n⚠️ 1 threat requires manual review\n\n**Affected Systems:**\n• Windows Workstations: 2\n• Linux Servers: 1\n• Email Gateway: Scanning active",
        queryInfo: {
          intent: "threat_detection",
          entities: ["malware", "today"],
          query_dsl: "threat.category:malware AND @timestamp:[now-24h TO now]",
          execution_time: 189,
          results_count: 3
        }
      };
    }
    
    if (lowerQuery.includes('network') || lowerQuery.includes('traffic')) {
      return {
        message: "📊 **Network Activity Analysis**\n\nCurrent network security status:\n\n**Traffic Summary:**\n• Total connections: 45,621\n• Blocked connections: 1,247 (2.7%)\n• Suspicious patterns: 12\n\n**Top Blocked Sources:**\n1. 203.45.12.8 (China) - 234 blocks\n2. 185.99.11.45 (Russia) - 189 blocks\n3. 91.234.567.12 (Unknown) - 156 blocks\n\n**Anomalies Detected:**\n• Unusual port scanning from 10.0.0.99\n• High bandwidth usage on VLAN 200\n• DNS tunneling attempts blocked",
        queryInfo: {
          intent: "network_analysis",
          entities: ["network", "suspicious"],
          query_dsl: "network.* AND event.category:network",
          execution_time: 312,
          results_count: 1247
        }
      };
    }
    
    return {
      message: `I understand you're asking about: "${query}"\n\nI can help you with:\n• Security event investigation\n• Log analysis and correlation\n• Threat detection and hunting\n• Incident response queries\n• Report generation\n\nTry being more specific, like:\n"Show me authentication failures from external IPs"\n"Find any privilege escalation attempts"\n"Generate weekly security summary"`,
      queryInfo: {
        intent: "general_help",
        entities: [],
        query_dsl: "N/A - Help request",
        execution_time: 45,
        results_count: 0
      }
    };
  };

  const renderMessage = (message: Message) => {
    return (
      <div
        key={message.id}
        className={`flex items-start space-x-3 mb-6 ${
          message.type === 'user' ? 'flex-row-reverse space-x-reverse' : ''
        }`}
      >
        <div
          className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
            message.type === 'user'
              ? 'bg-blue-600'
              : 'bg-gradient-to-br from-purple-500 to-blue-600'
          }`}
        >
          {message.type === 'user' ? (
            <User className="w-5 h-5 text-white" />
          ) : (
            <Bot className="w-5 h-5 text-white" />
          )}
        </div>

        <div
          className={`flex-1 max-w-4xl ${
            message.type === 'user' ? 'text-right' : ''
          }`}
        >
          <div
            className={`inline-block p-4 rounded-2xl ${
              message.type === 'user'
                ? 'bg-blue-600 text-white'
                : 'bg-gray-800 border border-gray-700 text-gray-100'
            }`}
          >
            <div className="whitespace-pre-wrap">{message.content}</div>
            
            {message.queryInfo && (
              <div className="mt-4 pt-4 border-t border-gray-600 space-y-2">
                <div className="flex items-center space-x-4 text-sm text-gray-300">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4" />
                    <span>{message.queryInfo.execution_time}ms</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Database className="w-4 h-4" />
                    <span>{message.queryInfo.results_count} results</span>
                  </div>
                  <div className="flex items-center space-x-1">
                    <Filter className="w-4 h-4" />
                    <span>{message.queryInfo.intent}</span>
                  </div>
                </div>
                
                {isConnected && (
                  <details className="text-xs text-gray-400">
                    <summary className="cursor-pointer hover:text-gray-300">Query Details</summary>
                    <pre className="mt-2 p-2 bg-gray-900 rounded text-green-400 font-mono text-xs overflow-x-auto">
                      {message.queryInfo.query_dsl}
                    </pre>
                  </details>
                )}
              </div>
            )}
          </div>

          <div className="mt-1 text-xs text-gray-500">
            {message.timestamp.toLocaleTimeString()}
          </div>
        </div>
      </div>
    );
  };

  const quickQueries = [
    "Show failed logins in last hour",
    "Any malware detections today?",
    "Find network anomalies",
    "Generate security summary",
  ];

  return (
    <div className="flex flex-col h-full">
      {/* Connection Banner */}
      {!isConnected && (
        <div className="bg-yellow-600/20 border border-yellow-600/30 rounded-lg p-3 mb-4">
          <div className="flex items-center space-x-2">
            <AlertTriangle className="w-5 h-5 text-yellow-400" />
            <span className="text-yellow-300 font-medium">Demo Mode</span>
            <span className="text-gray-300">- Using mock data for demonstration</span>
          </div>
        </div>
      )}

      {/* Quick Query Buttons */}
      <div className="mb-4">
        <p className="text-sm text-gray-400 mb-2">Quick queries:</p>
        <div className="flex flex-wrap gap-2">
          {quickQueries.map((query, index) => (
            <button
              key={index}
              onClick={() => setInput(query)}
              className="px-3 py-1 text-sm bg-gray-700 hover:bg-gray-600 text-gray-300 hover:text-white rounded-full transition-colors"
            >
              {query}
            </button>
          ))}
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto mb-4 space-y-4">
        {messages.map(renderMessage)}
        {isLoading && (
          <div className="flex items-start space-x-3 mb-6">
            <div className="flex-shrink-0 w-10 h-10 rounded-full bg-gradient-to-br from-purple-500 to-blue-600 flex items-center justify-center">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1">
              <div className="inline-block p-4 bg-gray-800 border border-gray-700 rounded-2xl">
                <div className="flex items-center space-x-2 text-gray-400">
                  <div className="animate-spin w-4 h-4 border-2 border-blue-500 border-t-transparent rounded-full"></div>
                  <span>Analyzing your query...</span>
                </div>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div className="border-t border-gray-700 pt-4">
        <div className="flex items-end space-x-4">
          <div className="flex-1">
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask me about security events, threats, or generate reports..."
              className="w-full p-4 bg-gray-800 border border-gray-700 rounded-2xl text-white placeholder-gray-400 resize-none focus:outline-none focus:ring-2 focus:ring-blue-500"
              rows={3}
              onKeyDown={(e) => {
                if (e.key === 'Enter' && !e.shiftKey) {
                  e.preventDefault();
                  sendMessage();
                }
              }}
            />
          </div>
          <button
            onClick={sendMessage}
            disabled={!input.trim() || isLoading}
            className="p-4 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-700 disabled:cursor-not-allowed text-white rounded-2xl transition-colors"
          >
            <Send className="w-5 h-5" />
          </button>
        </div>
        <p className="text-xs text-gray-500 mt-2">
          Press Enter to send, Shift+Enter for new line. 
          {isConnected ? 'Connected to live SIEM backend.' : 'Demo mode - mock responses.'}
        </p>
      </div>
    </div>
  );
};

export default ChatInterface;
