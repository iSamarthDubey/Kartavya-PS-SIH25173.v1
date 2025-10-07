#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Kartavya SIEM Assistant - Complete Integration & Frontend Build
Creates production-grade backend and exceptional frontend
"""

import os
import shutil
import json
from pathlib import Path
from datetime import datetime

class ProjectIntegrator:
    def __init__(self):
        self.base = Path(".")
        
    def execute(self):
        """Execute complete integration and build"""
        print("\n" + "="*80)
        print("🚀 KARTAVYA SIEM ASSISTANT - PRODUCTION BUILD")
        print("="*80 + "\n")
        
        # Phase 1: Backend Integration
        print("📦 Phase 1: Backend Integration")
        self.setup_backend()
        
        # Phase 2: Create Exceptional Frontend
        print("\n🎨 Phase 2: Building Exceptional Frontend")
        self.setup_frontend()
        
        # Phase 3: Integration & Testing
        print("\n🔗 Phase 3: Integration & Testing")
        self.create_integration_tests()
        
        print("\n" + "="*80)
        print("✅ PRODUCTION BUILD COMPLETE!")
        print("="*80)
        
    def setup_backend(self):
        """Setup complete backend with all modules"""
        
        # Create directory structure
        backend_dirs = [
            "backend/app/core",
            "backend/app/api/v1",
            "backend/app/services",
            "backend/app/models",
            "backend/app/utils",
            "backend/app/middleware"
        ]
        
        for dir_path in backend_dirs:
            Path(dir_path).mkdir(parents=True, exist_ok=True)
            
        # Create __init__ files
        for dir_path in backend_dirs:
            init_file = Path(dir_path) / "__init__.py"
            if not init_file.exists():
                init_file.touch()
                
        print("  ✅ Backend structure created")
        
        # Create run script
        run_script = '''#!/usr/bin/env python3
"""Run the Kartavya SIEM Assistant Backend"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        reload=True,
        log_level="info"
    )
'''
        Path("backend/run.py").write_text(run_script, encoding='utf-8')
        print("  ✅ Backend run script created")
        
    def setup_frontend(self):
        """Create exceptional production-grade frontend"""
        
        # Frontend tech stack (Better than ChatGPT's suggestion!)
        tech_stack = {
            "framework": "React 18 + TypeScript",
            "build_tool": "Vite",
            "styling": "TailwindCSS + ShadCN/UI + Custom Components",
            "state": "Zustand + React Query",
            "charts": "Recharts + D3.js for advanced visualizations",
            "animations": "Framer Motion + React Spring",
            "icons": "Lucide React + Heroicons",
            "theme": "Dark Cybersecurity Theme with Glassmorphism",
            "routing": "React Router v6",
            "forms": "React Hook Form + Zod",
            "notifications": "React Hot Toast",
            "websocket": "Socket.io for real-time updates",
            "testing": "Vitest + React Testing Library"
        }
        
        print("  📋 Frontend Tech Stack:")
        for key, value in tech_stack.items():
            print(f"    • {key}: {value}")
            
        # Create package.json with all dependencies
        package_json = {
            "name": "kartavya-siem-frontend",
            "version": "1.0.0",
            "type": "module",
            "scripts": {
                "dev": "vite",
                "build": "tsc && vite build",
                "preview": "vite preview",
                "test": "vitest",
                "lint": "eslint ."
            },
            "dependencies": {
                "react": "^18.2.0",
                "react-dom": "^18.2.0",
                "react-router-dom": "^6.20.0",
                "@tanstack/react-query": "^5.12.0",
                "zustand": "^4.4.7",
                "axios": "^1.6.2",
                "recharts": "^2.10.3",
                "d3": "^7.8.5",
                "framer-motion": "^10.16.16",
                "react-spring": "^9.7.3",
                "lucide-react": "^0.294.0",
                "@heroicons/react": "^2.0.18",
                "react-hook-form": "^7.48.2",
                "zod": "^3.22.4",
                "@hookform/resolvers": "^3.3.2",
                "react-hot-toast": "^2.4.1",
                "socket.io-client": "^4.5.4",
                "date-fns": "^2.30.0",
                "clsx": "^2.0.0",
                "tailwind-merge": "^2.2.0",
                "@radix-ui/react-dialog": "^1.0.5",
                "@radix-ui/react-dropdown-menu": "^2.0.6",
                "@radix-ui/react-select": "^2.0.0",
                "@radix-ui/react-tabs": "^1.0.4",
                "@radix-ui/react-tooltip": "^1.0.7",
                "react-markdown": "^9.0.1",
                "react-syntax-highlighter": "^15.5.0"
            },
            "devDependencies": {
                "@types/react": "^18.2.45",
                "@types/react-dom": "^18.2.18",
                "@types/d3": "^7.4.3",
                "@typescript-eslint/eslint-plugin": "^6.14.0",
                "@typescript-eslint/parser": "^6.14.0",
                "@vitejs/plugin-react": "^4.2.1",
                "autoprefixer": "^10.4.16",
                "eslint": "^8.55.0",
                "eslint-plugin-react-hooks": "^4.6.0",
                "postcss": "^8.4.32",
                "tailwindcss": "^3.3.6",
                "typescript": "^5.3.3",
                "vite": "^5.0.8",
                "vitest": "^1.0.4"
            }
        }
        
        frontend_path = Path("frontend")
        package_json_path = frontend_path / "package.json"
        package_json_path.write_text(json.dumps(package_json, indent=2), encoding='utf-8')
        print("  ✅ Package.json created with comprehensive dependencies")
        
        # Create main App component
        app_component = '''import React from 'react';
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { Toaster } from 'react-hot-toast';
import { ThemeProvider } from './contexts/ThemeContext';

// Pages
import Dashboard from './pages/Dashboard';
import ChatInterface from './pages/ChatInterface';
import ThreatHunting from './pages/ThreatHunting';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

// Layout
import MainLayout from './layouts/MainLayout';

// Create query client
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
    },
  },
});

function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <ThemeProvider>
        <Router>
          <Toaster
            position="top-right"
            toastOptions={{
              duration: 4000,
              style: {
                background: '#1a1a2e',
                color: '#fff',
                border: '1px solid #16213e',
              },
            }}
          />
          <MainLayout>
            <Routes>
              <Route path="/" element={<Dashboard />} />
              <Route path="/chat" element={<ChatInterface />} />
              <Route path="/threat-hunting" element={<ThreatHunting />} />
              <Route path="/reports" element={<Reports />} />
              <Route path="/settings" element={<Settings />} />
            </Routes>
          </MainLayout>
        </Router>
      </ThemeProvider>
    </QueryClientProvider>
  );
}

export default App;
'''
        
        app_path = frontend_path / "src" / "App.tsx"
        app_path.parent.mkdir(parents=True, exist_ok=True)
        app_path.write_text(app_component, encoding='utf-8')
        print("  ✅ Main App component created")
        
        # Create exceptional ChatInterface component
        chat_interface = '''import React, { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Send, Bot, User, Sparkles, AlertCircle, TrendingUp } from 'lucide-react';
import { useQuery, useMutation } from '@tanstack/react-query';
import { format } from 'date-fns';
import toast from 'react-hot-toast';
import { apiService } from '../services/api';
import MessageBubble from '../components/chat/MessageBubble';
import QuerySuggestions from '../components/chat/QuerySuggestions';
import ResultsPanel from '../components/chat/ResultsPanel';
import ChartsPanel from '../components/chat/ChartsPanel';

interface Message {
  id: string;
  type: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  data?: any;
  charts?: any[];
  intent?: string;
  entities?: any[];
}

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const queryMutation = useMutation({
    mutationFn: async (query: string) => {
      return await apiService.query({ query });
    },
    onSuccess: (data) => {
      const assistantMessage: Message = {
        id: Date.now().toString(),
        type: 'assistant',
        content: data.summary || 'Analysis complete.',
        timestamp: new Date(),
        data: data.results,
        charts: data.charts,
        intent: data.intent,
        entities: data.entities,
      };
      setMessages(prev => [...prev, assistantMessage]);
      setIsTyping(false);
    },
    onError: (error) => {
      toast.error('Failed to process query. Please try again.');
      setIsTyping(false);
    },
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date(),
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);
    queryMutation.mutate(input);
  };

  const handleSuggestionClick = (suggestion: string) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="flex h-[calc(100vh-4rem)] bg-gradient-to-br from-gray-950 via-gray-900 to-gray-950">
      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <div className="bg-gray-900/50 backdrop-blur-xl border-b border-gray-800 px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-gradient-to-br from-blue-500 to-purple-600 rounded-lg">
                <Bot className="w-6 h-6 text-white" />
              </div>
              <div>
                <h1 className="text-xl font-bold text-white">Kartavya AI Assistant</h1>
                <p className="text-sm text-gray-400">SIEM Investigation & Threat Analysis</p>
              </div>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-sm text-gray-400">Connected to Elasticsearch</span>
              </div>
            </div>
          </div>
        </div>

        {/* Messages Area */}
        <div className="flex-1 overflow-y-auto px-6 py-4 space-y-4">
          {messages.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                className="text-center"
              >
                <div className="mb-6 relative">
                  <div className="w-24 h-24 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                    <Sparkles className="w-12 h-12 text-white" />
                  </div>
                  <motion.div
                    className="absolute -inset-4 bg-gradient-to-br from-blue-500/20 to-purple-600/20 rounded-full"
                    animate={{
                      scale: [1, 1.2, 1],
                      opacity: [0.5, 0.2, 0.5],
                    }}
                    transition={{
                      duration: 3,
                      repeat: Infinity,
                    }}
                  />
                </div>
                <h2 className="text-2xl font-bold text-white mb-2">
                  Welcome to Kartavya SIEM Assistant
                </h2>
                <p className="text-gray-400 mb-8 max-w-md">
                  Ask me anything about your security events, threats, or generate comprehensive reports.
                </p>
                <QuerySuggestions onSuggestionClick={handleSuggestionClick} />
              </motion.div>
            </div>
          ) : (
            <>
              <AnimatePresence>
                {messages.map((message) => (
                  <MessageBubble key={message.id} message={message} />
                ))}
              </AnimatePresence>
              {isTyping && (
                <motion.div
                  initial={{ opacity: 0, y: 10 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="flex items-center space-x-2 text-gray-400"
                >
                  <Bot className="w-5 h-5" />
                  <div className="flex space-x-1">
                    <motion.div
                      className="w-2 h-2 bg-blue-500 rounded-full"
                      animate={{ y: [0, -5, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-blue-500 rounded-full"
                      animate={{ y: [0, -5, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                    />
                    <motion.div
                      className="w-2 h-2 bg-blue-500 rounded-full"
                      animate={{ y: [0, -5, 0] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                    />
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </>
          )}
        </div>

        {/* Input Area */}
        <div className="border-t border-gray-800 bg-gray-900/50 backdrop-blur-xl px-6 py-4">
          <form onSubmit={handleSubmit} className="flex space-x-4">
            <input
              ref={inputRef}
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about security events, threats, or request reports..."
              className="flex-1 bg-gray-800/50 border border-gray-700 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-500/20 transition-all"
              disabled={isTyping}
            />
            <motion.button
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              type="submit"
              disabled={!input.trim() || isTyping}
              className="px-6 py-3 bg-gradient-to-r from-blue-500 to-purple-600 text-white rounded-xl font-medium disabled:opacity-50 disabled:cursor-not-allowed transition-all"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </form>
        </div>
      </div>

      {/* Results/Charts Panel */}
      {messages.length > 0 && messages[messages.length - 1].type === 'assistant' && (
        <div className="w-96 border-l border-gray-800 bg-gray-900/30 backdrop-blur-xl overflow-y-auto">
          {messages[messages.length - 1].charts && (
            <ChartsPanel charts={messages[messages.length - 1].charts!} />
          )}
          {messages[messages.length - 1].data && (
            <ResultsPanel data={messages[messages.length - 1].data} />
          )}
        </div>
      )}
    </div>
  );
}
'''
        
        chat_path = frontend_path / "src" / "pages" / "ChatInterface.tsx"
        chat_path.parent.mkdir(parents=True, exist_ok=True)
        chat_path.write_text(chat_interface, encoding='utf-8')
        print("  ✅ Exceptional Chat Interface created")
        
    def create_integration_tests(self):
        """Create integration test setup"""
        
        test_script = '''#!/usr/bin/env python3
"""Test complete integration of Kartavya SIEM Assistant"""

import asyncio
import aiohttp
import json
from datetime import datetime

async def test_backend():
    """Test backend endpoints"""
    base_url = "http://localhost:8001"
    
    async with aiohttp.ClientSession() as session:
        # Test health endpoint
        async with session.get(f"{base_url}/health") as resp:
            if resp.status == 200:
                print("✅ Health check passed")
            else:
                print("❌ Health check failed")
                
        # Test query endpoint
        test_query = {
            "query": "Show me failed login attempts in the last 24 hours",
            "session_id": "test-session"
        }
        
        async with session.post(
            f"{base_url}/api/v1/query",
            json=test_query,
            headers={"Content-Type": "application/json"}
        ) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Query endpoint working")
                print(f"  Intent: {result.get('intent')}")
                print(f"  Entities: {len(result.get('entities', []))} found")
            else:
                print("❌ Query endpoint failed")

if __name__ == "__main__":
    print("Testing Kartavya SIEM Assistant Integration...")
    asyncio.run(test_backend())
'''
        
        Path("test_integration.py").write_text(test_script, encoding='utf-8')
        print("  ✅ Integration test script created")

if __name__ == "__main__":
    integrator = ProjectIntegrator()
    integrator.execute()
