/**
 * KARTAVYA SIEM - Layout Controls Component
 * Floating controls for layout management, sidebar toggle, and reset
 */

import React, { useState } from 'react';
import { 
  Settings, 
  PanelLeft, 
  RotateCcw, 
  Maximize2, 
  Minimize2, 
  ChevronUp, 
  ChevronDown,
  Eye,
  EyeOff
} from 'lucide-react';
import { useLayout } from '../../contexts/LayoutContext';

interface LayoutControlsProps {
  className?: string;
}

const LayoutControls: React.FC<LayoutControlsProps> = ({ className = '' }) => {
  const { state, actions } = useLayout();
  const [isExpanded, setIsExpanded] = useState(false);

  const handleResetLayout = () => {
    actions.resetLayout();
    // Show a brief feedback animation or notification
    setTimeout(() => {
      const notification = document.createElement('div');
      notification.className = 'fixed top-4 right-4 bg-blue-600 text-white px-4 py-2 rounded-lg shadow-lg z-[60] animate-fade-in';
      notification.textContent = 'Layout Reset';
      document.body.appendChild(notification);
      setTimeout(() => {
        notification.remove();
      }, 2000);
    }, 100);
  };

  const controlButtons = [
    {
      id: 'sidebar-toggle',
      icon: state.sidebarCollapsed ? PanelLeft : Minimize2,
      label: state.sidebarCollapsed ? 'Expand Sidebar' : 'Collapse Sidebar',
      action: actions.toggleSidebar,
      active: !state.sidebarCollapsed
    },
    {
      id: 'auto-collapse',
      icon: state.autoCollapseEnabled ? Eye : EyeOff,
      label: state.autoCollapseEnabled ? 'Disable Auto-Collapse' : 'Enable Auto-Collapse',
      action: () => actions.setAutoCollapseEnabled(!state.autoCollapseEnabled),
      active: state.autoCollapseEnabled
    },
    {
      id: 'reset-layout',
      icon: RotateCcw,
      label: 'Reset Layout',
      action: handleResetLayout,
      active: false
    }
  ];

  return (
    <div className={`fixed bottom-6 right-6 z-50 ${className}`}>
      {/* Main Control Panel */}
      <div className={`
        bg-gray-900/95 backdrop-blur-sm border border-gray-700/50 
        rounded-2xl shadow-2xl transition-all duration-300 ease-out
        hover:shadow-3xl hover:border-gray-600/50
        ${isExpanded ? 'p-4' : 'p-3'}
      `}>
        
        {/* Expanded Controls */}
        {isExpanded && (
          <div className="space-y-3 mb-3">
            <div className="text-xs font-semibold text-gray-400 uppercase tracking-wider px-2">
              Layout Controls
            </div>
            
            <div className="space-y-2">
              {controlButtons.map((button) => (
                <button
                  key={button.id}
                  onClick={button.action}
                  className={`
                    flex items-center space-x-3 w-full p-3 text-left rounded-lg 
                    transition-all duration-200 group
                    ${button.active 
                      ? 'bg-blue-600/20 text-blue-300 border border-blue-600/30' 
                      : 'text-gray-300 hover:bg-gray-800 hover:text-white border border-transparent hover:border-gray-700/50'
                    }
                  `}
                >
                  <button.icon className="w-4 h-4 flex-shrink-0" />
                  <span className="text-sm font-medium">{button.label}</span>
                </button>
              ))}
            </div>

            {/* Panel Size Indicators */}
            <div className="pt-2 border-t border-gray-700/30">
              <div className="text-xs text-gray-500 space-y-1">
                <div className="flex justify-between">
                  <span>Left Panel:</span>
                  <span className="text-gray-400">{state.leftPanelWidth}px</span>
                </div>
                <div className="flex justify-between">
                  <span>Right Panel:</span>
                  <span className="text-gray-400">{state.rightPanelWidth}px</span>
                </div>
                <div className="flex justify-between">
                  <span>Sidebar:</span>
                  <span className="text-gray-400">
                    {state.sidebarCollapsed ? 'Collapsed' : `${state.sidebarWidth}px`}
                  </span>
                </div>
              </div>
            </div>

            {/* Quick Tips */}
            <div className="pt-2 border-t border-gray-700/30">
              <div className="text-xs text-gray-500">
                <p className="mb-1">💡 <span className="text-gray-400">Tips:</span></p>
                <ul className="list-disc list-inside space-y-1 ml-2">
                  <li>Drag panel edges to resize</li>
                  <li>Auto-collapse saves space when chatting</li>
                  <li>Use reset to restore defaults</li>
                </ul>
              </div>
            </div>
          </div>
        )}

        {/* Toggle Button */}
        <div className="flex justify-center">
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="
              flex items-center justify-center w-12 h-12 
              bg-gradient-to-br from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 
              text-white rounded-full border-2 border-blue-500/30
              transition-all duration-200 shadow-lg hover:shadow-2xl
              transform hover:scale-110 active:scale-95
              relative
            "
            title={isExpanded ? 'Collapse Controls' : 'Layout Controls (Ctrl+B to toggle sidebar)'}
          >
            {isExpanded ? (
              <ChevronDown className="w-5 h-5" />
            ) : (
              <Settings className="w-5 h-5" />
            )}
          </button>
        </div>

        {/* Compact Indicator */}
        {!isExpanded && (
          <div className="absolute -top-1 -right-1 flex space-x-1">
            <div className={`
              w-2 h-2 rounded-full transition-colors border border-gray-600
              ${state.sidebarCollapsed ? 'bg-yellow-400' : 'bg-green-400'}
            `} />
          </div>
        )}
      </div>

    </div>
  );
};

export default LayoutControls;
