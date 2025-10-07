import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './components/Sidebar';
import { Header } from './components/layout/Header';
import { Chat } from './pages/Chat';
import { Dashboard } from './pages/NewDashboard';
import { Reports } from './pages/Reports';
import { SettingsPage } from './pages/Settings';

const App: React.FC = () => {
  const [activeTab, setActiveTab] = React.useState('chat');

  const getCurrentPage = () => {
    switch (activeTab) {
      case 'chat':
        return <Chat />;
      case 'dashboard':
        return <Dashboard />;
      case 'reports':
        return <Reports />;
      case 'settings':
        return <SettingsPage />;
      case 'investigation':
        return <Chat />; // Use chat for investigation for now
      case 'alerts':
        return <Dashboard />; // Use dashboard for alerts for now
      case 'analytics':
        return <Dashboard />; // Use dashboard for analytics for now
      case 'history':
        return <Chat />; // Use chat for history for now
      case 'filters':
        return <SettingsPage />; // Use settings for filters for now
      case 'exports':
        return <Reports />; // Use reports for exports for now
      default:
        return <Chat />;
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-cyber-gradient text-white overflow-hidden relative">
        {/* Background Effects */}
        <div className="absolute inset-0 opacity-30">
          <div className="absolute top-0 left-0 w-96 h-96 bg-cyber-blue/10 rounded-full blur-3xl animate-pulse-slow"></div>
          <div className="absolute top-1/2 right-0 w-96 h-96 bg-cyber-purple/10 rounded-full blur-3xl animate-pulse-slow delay-1000"></div>
          <div className="absolute bottom-0 left-1/3 w-96 h-96 bg-cyber-cyan/10 rounded-full blur-3xl animate-pulse-slow delay-500"></div>
        </div>

        <div className="relative flex h-screen">
          {/* Sidebar */}
          <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
          
          {/* Main Content */}
          <main className="flex-1 flex flex-col overflow-hidden">
            {/* Header */}
            <Header />
            
            {/* Page Content */}
            <div className="flex-1 overflow-hidden">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3, ease: "easeInOut" }}
                  className="h-full"
                >
                  {getCurrentPage()}
                </motion.div>
              </AnimatePresence>
            </div>
          </main>
        </div>

        {/* Loading Overlay */}
        <AnimatePresence>
          {false && ( // Set to true when loading
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-cyber-dark/80 backdrop-blur-sm flex items-center justify-center z-50"
            >
              <div className="text-center">
                <div className="w-16 h-16 border-4 border-cyber-cyan/30 border-t-cyber-cyan rounded-full animate-spin mb-4"></div>
                <p className="text-cyber-gray-300">Initializing SIEM Assistant...</p>
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </Router>
  );
};

export default App;