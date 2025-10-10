/**
 * KARTAVYA SIEM - Main App Component 
 * Complete application with React Router and authentication
 */

import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Shield } from 'lucide-react';

// Components
import ErrorBoundary, { 
  ApiErrorBoundary, 
  DashboardErrorBoundary, 
  ChatErrorBoundary 
} from './components/ErrorBoundary';
import { 
  NotificationProvider, 
  ConnectionStatus
} from './components/ui/NotificationSystem';
import { FullPageLoader } from './components/ui/LoadingStates';
import LandingPage from './pages/LandingPage';
import LoginPage from './components/auth/LoginPage';
import OnboardingFlow from './components/OnboardingFlow';
import SimpleDashboard from './components/SimpleDashboard/SimpleDashboard';
import MainConsole from './components/MainConsole';
import ErrorHandlingDemo from './components/ErrorHandlingDemo';

// Store
import { useAuth } from './store/appStore';

// Lazy load less critical components
const Reports = React.lazy(() => import('./components/Reports'));
const Settings = React.lazy(() => import('./components/Settings'));

// Main App Component
const App: React.FC = () => {
  return (
    <ErrorBoundary>
      <NotificationProvider>
        <Router>
          <div className="min-h-screen bg-gray-900 text-white">
            <ConnectionStatus />
            <Routes>
              {/* Public Routes */}
              <Route path="/" element={<LandingPage />} />
              <Route path="/login" element={<LoginPage />} />
              
              {/* Protected Routes */}
              <Route path="/dashboard" element={<ProtectedRoute><AppLayout><SimpleDashboard /></AppLayout></ProtectedRoute>} />
              <Route path="/console" element={<ProtectedRoute><AppLayout><MainConsole /></AppLayout></ProtectedRoute>} />
              <Route path="/reports" element={<ProtectedRoute><AppLayout><React.Suspense fallback={<FullPageLoader message="Loading Reports..." />}><Reports /></React.Suspense></AppLayout></ProtectedRoute>} />
              <Route path="/settings" element={<ProtectedRoute><AppLayout><React.Suspense fallback={<FullPageLoader message="Loading Settings..." />}><Settings /></React.Suspense></AppLayout></ProtectedRoute>} />
              <Route path="/demo" element={<ProtectedRoute><AppLayout><ErrorHandlingDemo /></AppLayout></ProtectedRoute>} />
            </Routes>
          </div>
        </Router>
      </NotificationProvider>
    </ErrorBoundary>
  );
};

// Protected Route Component
const ProtectedRoute: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { isAuthenticated, loading } = useAuth();
  
  if (loading) {
    return <FullPageLoader message="Initializing SIEM Platform..." />;
  }
  
  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }
  
  return <>{children}</>;
};

// App Layout Component
const AppLayout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const { user, logout } = useAuth();
  const [showOnboarding, setShowOnboarding] = React.useState(false);

  // Check if user needs onboarding
  React.useEffect(() => {
    const hasCompletedOnboarding = localStorage.getItem('kartavya_onboarding_completed');
    if (!hasCompletedOnboarding && user) {
      setShowOnboarding(true);
    }
  }, [user]);

  const handleOnboardingComplete = () => {
    setShowOnboarding(false);
  };

  return (
    <>
      <div className="flex h-screen">
        {/* Sidebar Navigation */}
        <nav className="w-64 bg-gray-800 border-r border-gray-700">
          <div className="p-4">
            <div className="flex items-center space-x-3 mb-8">
              <Shield className="w-8 h-8 text-blue-400" />
              <div>
                <h1 className="text-lg font-bold text-white">KARTAVYA SIEM</h1>
                <p className="text-xs text-gray-400">{user?.role} • {user?.name}</p>
              </div>
            </div>
            
            <NavigationMenu />
            
            {/* User Profile & Logout */}
            <div className="mt-auto pt-4 border-t border-gray-700">
              <LogoutButton />
            </div>
          </div>
        </nav>

        {/* Main Content Area */}
        <main className="flex-1 overflow-y-auto">
          {children}
        </main>
      </div>
      
      {/* Onboarding Overlay */}
      {showOnboarding && (
        <OnboardingFlow onComplete={handleOnboardingComplete} />
      )}
    </>
  );
};

// Navigation Menu Component
const NavigationMenu: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  
  const navItems = [
    { path: '/dashboard', label: 'Dashboard', icon: <Shield className="w-4 h-4" /> },
    { path: '/console', label: 'AI Assistant', icon: <Shield className="w-4 h-4" /> },
    { path: '/reports', label: 'Reports', icon: <Shield className="w-4 h-4" /> },
    { path: '/settings', label: 'Settings', icon: <Shield className="w-4 h-4" /> },
    { path: '/demo', label: '🚨 Error Demo', icon: <Shield className="w-4 h-4" /> }
  ];
  
  return (
    <ul className="space-y-2">
      {navItems.map((item) => (
        <li key={item.path}>
          <button
            onClick={() => navigate(item.path)}
            className={`flex items-center space-x-3 w-full text-left p-3 rounded-lg transition-colors ${
              location.pathname === item.path
                ? 'bg-blue-600 text-white' 
                : 'text-gray-300 hover:bg-gray-700'
            }`}
          >
            {item.icon}
            <span>{item.label}</span>
          </button>
        </li>
      ))}
    </ul>
  );
};

// Logout Button Component
const LogoutButton: React.FC = () => {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  
  const handleLogout = async () => {
    logout();
    navigate('/');
  };
  
  return (
    <button
      onClick={handleLogout}
      className="w-full flex items-center space-x-3 p-3 text-gray-300 hover:bg-gray-700 rounded-lg transition-colors"
    >
      <div className="w-8 h-8 bg-gray-600 rounded-full flex items-center justify-center">
        <span className="text-xs font-semibold">{user?.name?.charAt(0) || 'U'}</span>
      </div>
      <div className="flex-1 text-left">
        <p className="text-sm font-medium">{user?.name}</p>
        <p className="text-xs text-gray-500">Click to logout</p>
      </div>
    </button>
  );
};

export default App;
