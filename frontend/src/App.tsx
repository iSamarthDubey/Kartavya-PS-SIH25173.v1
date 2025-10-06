import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import { motion, AnimatePresence } from 'framer-motion';
import { Sidebar } from './components/Sidebar';
import { Chat } from './pages/Chat';
import { Dashboard } from './pages/Dashboard';
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
      default:
        return <Chat />;
    }
  };

  return (
    <Router>
      <div className="min-h-screen bg-cyber-dark text-white overflow-hidden">
        <div className="flex h-screen">
          {/* Sidebar */}
          <Sidebar activeTab={activeTab} onTabChange={setActiveTab} />
          
          {/* Main Content */}
          <main className="flex-1 flex flex-col overflow-hidden">
            <div className="flex-1 p-6 overflow-hidden">
              <AnimatePresence mode="wait">
                <motion.div
                  key={activeTab}
                  initial={{ opacity: 0, x: 20 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -20 }}
                  transition={{ duration: 0.3 }}
                  className="h-full"
                >
                  {getCurrentPage()}
                </motion.div>
              </AnimatePresence>
            </div>
          </main>
        </div>
      </div>
    </Router>
  );
};

export default App;
