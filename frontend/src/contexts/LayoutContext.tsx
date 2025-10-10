/**
 * KARTAVYA SIEM - Layout Context
 * Manages layout state (sidebar, panels, etc.)
 */

import React, { createContext, useContext, useReducer, ReactNode } from 'react';

// Layout State Type
interface LayoutState {
  sidebarCollapsed: boolean;
  sidebarWidth: number;
  rightPanelOpen: boolean;
  rightPanelWidth: number;
  activeRightPanel: 'query' | 'context' | 'insights' | null;
}

// Actions
type LayoutAction = 
  | { type: 'TOGGLE_SIDEBAR' }
  | { type: 'SET_SIDEBAR_WIDTH'; width: number }
  | { type: 'TOGGLE_RIGHT_PANEL'; panel?: 'query' | 'context' | 'insights' }
  | { type: 'SET_RIGHT_PANEL_WIDTH'; width: number }
  | { type: 'CLOSE_RIGHT_PANEL' };

// Initial State
const initialState: LayoutState = {
  sidebarCollapsed: false,
  sidebarWidth: 256,
  rightPanelOpen: false,
  rightPanelWidth: 400,
  activeRightPanel: null
};

// Reducer
const layoutReducer = (state: LayoutState, action: LayoutAction): LayoutState => {
  switch (action.type) {
    case 'TOGGLE_SIDEBAR':
      return {
        ...state,
        sidebarCollapsed: !state.sidebarCollapsed
      };
    
    case 'SET_SIDEBAR_WIDTH':
      return {
        ...state,
        sidebarWidth: action.width
      };
    
    case 'TOGGLE_RIGHT_PANEL':
      const newPanel = action.panel || 'query';
      return {
        ...state,
        rightPanelOpen: state.activeRightPanel === newPanel ? !state.rightPanelOpen : true,
        activeRightPanel: newPanel
      };
    
    case 'SET_RIGHT_PANEL_WIDTH':
      return {
        ...state,
        rightPanelWidth: action.width
      };
    
    case 'CLOSE_RIGHT_PANEL':
      return {
        ...state,
        rightPanelOpen: false,
        activeRightPanel: null
      };
    
    default:
      return state;
  }
};

// Context
interface LayoutContextType {
  state: LayoutState;
  actions: {
    toggleSidebar: () => void;
    setSidebarWidth: (width: number) => void;
    toggleRightPanel: (panel?: 'query' | 'context' | 'insights') => void;
    setRightPanelWidth: (width: number) => void;
    closeRightPanel: () => void;
  };
}

const LayoutContext = createContext<LayoutContextType | undefined>(undefined);

// Provider Component
export const LayoutProvider: React.FC<{ children: ReactNode }> = ({ children }) => {
  const [state, dispatch] = useReducer(layoutReducer, initialState);

  const actions = {
    toggleSidebar: () => dispatch({ type: 'TOGGLE_SIDEBAR' }),
    setSidebarWidth: (width: number) => dispatch({ type: 'SET_SIDEBAR_WIDTH', width }),
    toggleRightPanel: (panel?: 'query' | 'context' | 'insights') => 
      dispatch({ type: 'TOGGLE_RIGHT_PANEL', panel }),
    setRightPanelWidth: (width: number) => dispatch({ type: 'SET_RIGHT_PANEL_WIDTH', width }),
    closeRightPanel: () => dispatch({ type: 'CLOSE_RIGHT_PANEL' })
  };

  return (
    <LayoutContext.Provider value={{ state, actions }}>
      {children}
    </LayoutContext.Provider>
  );
};

// Hook
export const useLayout = (): LayoutContextType => {
  const context = useContext(LayoutContext);
  if (context === undefined) {
    throw new Error('useLayout must be used within a LayoutProvider');
  }
  return context;
};
