/**
 * KARTAVYA SIEM - Simple Layout with ChatGPT-style Sidebar
 * Clean, minimal layout exactly like ChatGPT interface
 */

import React, { useState, useEffect } from 'react';
import ChatGPTSidebar from './ChatGPTSidebar';

interface SimpleLayoutProps {
  children: React.ReactNode;
}

const SimpleLayout: React.FC<SimpleLayoutProps> = ({ children }) => {
  const [isSidebarCollapsed, setIsSidebarCollapsed] = useState(false);

  // Persist sidebar state
  useEffect(() => {
    const saved = localStorage.getItem('sidebar-collapsed');
    if (saved !== null) {
      setIsSidebarCollapsed(JSON.parse(saved));
    }
  }, []);

  const handleToggleSidebar = () => {
    const newState = !isSidebarCollapsed;
    setIsSidebarCollapsed(newState);
    localStorage.setItem('sidebar-collapsed', JSON.stringify(newState));
  };

  return (
    <div className="flex h-screen bg-gray-950 text-white overflow-hidden">
      {/* ChatGPT-style Sidebar */}
      <ChatGPTSidebar 
        isCollapsed={isSidebarCollapsed}
        onToggle={handleToggleSidebar}
      />
      
      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0">
        {children}
      </div>
    </div>
  );
};

export default SimpleLayout;
