/**
 * KARTAVYA SIEM - Main Console Component
 * Implements blueprint's three-column layout: Sidebar | Chat | Context Panel
 * This replaces separate dashboard/chat routes with unified interface
 */

import React, { useState, useEffect } from 'react';
import { Settings, Filter, BarChart3, FileText, AlertTriangle, Loader2 } from 'lucide-react';

// Context and Layout Components
import { useLayout } from '../contexts/LayoutContext';
import ResizeHandle from './Layout/ResizeHandle';
import LayoutControls from './Layout/LayoutControls';

// Import our new components (will create these next)
import ChatConsole from './ChatConsole/ChatConsole';
import QueryPreview from './QueryPreview/QueryPreview';

// Services
import apiService from '../services/apiService';

interface MainConsoleProps {
  // Props for customization and theming
}

const MainConsole: React.FC<MainConsoleProps> = () => {
  const { state, actions } = useLayout();
  const [rightPanelTab, setRightPanelTab] = useState<'query' | 'context' | 'saved'>('query');
  const [currentQuery, setCurrentQuery] = useState<any>(null);
  const [activeFilters, setActiveFilters] = useState<any[]>([]);
  const [quickActions, setQuickActions] = useState<any[]>([]);
  const [recentInvestigations, setRecentInvestigations] = useState<any[]>([]);
  const [isLoadingData, setIsLoadingData] = useState(true);
  const [queryStats, setQueryStats] = useState<{
    totalEvents: number;
    queryTime: number;
    isLoading: boolean;
  }>({ totalEvents: 0, queryTime: 0, isLoading: false });

  // Auto-collapse main sidebar when user starts using chat console
  const handleChatInteraction = () => {
    actions.setLastInteraction('chat');
    // Auto-collapse main sidebar if enabled
    if (state.autoCollapseEnabled) {
      actions.autoCollapse();
    }
  };

  const handlePanelInteraction = () => {
    actions.setLastInteraction('panels');
  };

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyboard = (e: KeyboardEvent) => {
      // Ctrl+L to toggle layout controls
      if (e.ctrlKey && e.key.toLowerCase() === 'l') {
        e.preventDefault();
        // This will be handled by the LayoutControls component
      }
      // Ctrl+B to toggle sidebar
      if (e.ctrlKey && e.key.toLowerCase() === 'b') {
        e.preventDefault();
        actions.toggleSidebar();
      }
      // Ctrl+R to reset layout
      if (e.ctrlKey && e.shiftKey && e.key.toLowerCase() === 'r') {
        e.preventDefault();
        actions.resetLayout();
      }
    };

    window.addEventListener('keydown', handleKeyboard);
    return () => window.removeEventListener('keydown', handleKeyboard);
  }, [actions]);

  // Load dynamic data on component mount
  useEffect(() => {
    const loadDashboardData = async () => {
      try {
        // Load quick action suggestions from backend
        const suggestions = await apiService.getQuerySuggestions();
        if (Array.isArray(suggestions)) {
          const actions = suggestions.flatMap(category => 
            category.queries?.slice(0, 2).map((query: string) => ({
              label: query.split(' ').slice(0, 2).join(' '), // First 2 words as label
              icon: category.category.includes('Auth') ? AlertTriangle :
                    category.category.includes('Network') ? BarChart3 : FileText,
              query: query
            })) || []
          ).slice(0, 4); // Max 4 actions
          setQuickActions(actions);
        }
        
        // TODO: Load recent investigations from backend
        // For now, leave empty until we have the endpoint
        setRecentInvestigations([]);
        
      } catch (error) {
        console.error('Failed to load dashboard data:', error);
        // Fallback to empty arrays
        setQuickActions([]);
        setRecentInvestigations([]);
      } finally {
        setIsLoadingData(false);
      }
    };

    loadDashboardData();
  }, []);

  return (
    <div className="flex h-screen bg-gray-900">
      {/* LEFT SIDEBAR - Navigation & Quick Actions */}
      <div 
        className="bg-gray-800 border-r border-gray-700 flex flex-col flex-shrink-0 h-full"
        style={{ width: `${state.leftPanelWidth}px` }}
      >
        {/* Quick Actions */}
        <div className="p-3 border-b border-gray-700">
          <h3 className="text-xs font-semibold text-gray-400 mb-2">QUICK ACTIONS</h3>
          <div className="space-y-1">
            {isLoadingData ? (
              <div className="flex items-center justify-center p-4">
                <Loader2 className="w-4 h-4 animate-spin text-gray-400" />
                <span className="text-xs text-gray-400 ml-2">Loading...</span>
              </div>
            ) : quickActions.length > 0 ? (
              quickActions.map((action, index) => (
                <button
                  key={index}
                  className="w-full flex items-center space-x-2 p-1.5 text-left text-gray-300 hover:bg-gray-700 rounded transition-colors"
                  onClick={() => {
                    // TODO: Integrate with ChatConsole to auto-fill query
                    console.log('Quick action:', action.query);
                  }}
                >
                  <action.icon className="w-3 h-3" />
                  <span className="text-xs">{action.label}</span>
                </button>
              ))
            ) : (
              <div className="text-xs text-gray-500 p-1.5">
                No quick actions available
              </div>
            )}
          </div>
        </div>

        {/* Recent Investigations */}
        <div className="p-3 flex-1">
          <h3 className="text-xs font-semibold text-gray-400 mb-2">RECENT</h3>
          <div className="space-y-1">
            {isLoadingData ? (
              <div className="flex items-center justify-center p-2">
                <Loader2 className="w-3 h-3 animate-spin text-gray-400" />
              </div>
            ) : recentInvestigations.length > 0 ? (
              recentInvestigations.map((investigation, index) => (
                <div key={index} className="p-2 text-xs text-gray-300 bg-gray-700/50 rounded hover:bg-gray-700 cursor-pointer transition-colors">
                  {investigation.title}
                  <div className="text-gray-500 text-xs mt-1">{investigation.date}</div>
                </div>
              ))
            ) : (
              <div className="p-1.5 text-xs text-gray-500 bg-gray-700/50 rounded">
                No recent investigations
              </div>
            )}
          </div>
        </div>

        {/* Status Panel */}
        <div className="p-3 border-t border-gray-700">
          <div className="flex items-center justify-between text-xs text-gray-400">
            <span>SIEM Status</span>
            <span className="flex items-center">
              <div className="w-1.5 h-1.5 bg-green-400 rounded-full mr-1.5"></div>
              Connected
            </span>
          </div>
        </div>
      </div>

      {/* Left Panel Resize Handle */}
      <ResizeHandle
        direction="vertical"
        onResize={(delta) => actions.setLeftPanelWidth(state.leftPanelWidth + delta)}
      />

      {/* CENTER - Chat Console (Primary Focus) */}
      <div className="flex-1 flex flex-col h-full min-w-0">
        {/* Main Chat Interface */}
        <div 
          className="flex-1 h-full min-h-0"
          onFocus={handleChatInteraction}
          onClick={handleChatInteraction}
        >
          <ChatConsole 
            onQueryGenerated={setCurrentQuery}
            activeFilters={activeFilters}
            onQueryStatsChange={setQueryStats}
            onFilterChange={setActiveFilters}
          />
        </div>
      </div>

      {/* Right Panel Resize Handle */}
      <ResizeHandle
        direction="vertical"
        onResize={(delta) => actions.setRightPanelWidth(state.rightPanelWidth - delta)}
      />

      {/* RIGHT PANEL - Context & Query Preview */}
      <div 
        className="bg-gray-800 border-l border-gray-700 flex flex-col flex-shrink-0 h-full"
        style={{ width: `${state.rightPanelWidth}px` }}
        onFocus={handlePanelInteraction}
        onClick={handlePanelInteraction}
      >
        {/* Panel Tabs */}
        <div className="flex border-b border-gray-700">
          {[
            { id: 'query', label: 'Query', icon: FileText },
            { id: 'context', label: 'Context', icon: Filter },
            { id: 'saved', label: 'Saved', icon: Settings }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setRightPanelTab(tab.id as any)}
              className={`flex-1 flex items-center justify-center space-x-1 p-2 text-xs transition-colors ${
                rightPanelTab === tab.id 
                  ? 'bg-blue-600 text-white' 
                  : 'text-gray-400 hover:text-gray-300 hover:bg-gray-700'
              }`}
            >
              <tab.icon className="w-3 h-3" />
              <span>{tab.label}</span>
            </button>
          ))}
        </div>

        {/* Panel Content */}
        <div className="flex-1 overflow-y-auto">
          {rightPanelTab === 'query' && (
            <QueryPreview query={currentQuery} />
          )}
          {rightPanelTab === 'context' && (
            <div className="p-3">
              <h3 className="text-xs font-semibold text-gray-400 mb-3">ACTIVE CONTEXT</h3>
              {activeFilters.length === 0 ? (
                <p className="text-xs text-gray-500">No active filters</p>
              ) : (
                <div className="space-y-2">
                  {activeFilters.map((filter, index) => (
                    <div key={index} className="p-2 bg-gray-700 rounded text-xs">
                      {JSON.stringify(filter)}
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
          {rightPanelTab === 'saved' && (
            <div className="p-3">
              <h3 className="text-xs font-semibold text-gray-400 mb-3">SAVED ITEMS</h3>
              <p className="text-xs text-gray-500">No saved investigations</p>
            </div>
          )}
        </div>
      </div>
      
      {/* Layout Controls */}
      <LayoutControls />
    </div>
  );
};

export default MainConsole;
