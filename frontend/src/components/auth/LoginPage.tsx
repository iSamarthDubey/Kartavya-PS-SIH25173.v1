/**
 * KARTAVYA SIEM - Professional Login Page
 * Enterprise-grade authentication interface with demo users and real API integration
 */

import React, { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import {
  Shield,
  ShieldCheck,
  ShieldAlert,
  Mail,
  KeyRound,
  Eye,
  EyeOff,
  UserCheck,
  Users,
  Crown,
  Search,
  AlertTriangle,
  CheckCircle,
  ArrowRight,
  Lock,
  Fingerprint,
  Zap,
  Brain,
  Activity
} from 'lucide-react';

import { useAuth } from '../../store/appStore';
import { useNotifications } from '../ui/NotificationSystem';
import { LoadingButton } from '../ui/LoadingStates';
import ErrorBoundary from '../ErrorBoundary';

const LoginPage: React.FC = () => {
  return (
    <ErrorBoundary>
      <div className="min-h-screen bg-gray-900 flex">
        <LoginContent />
      </div>
    </ErrorBoundary>
  );
};

const LoginContent: React.FC = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [selectedDemoUser, setSelectedDemoUser] = useState<'admin' | 'analyst' | 'viewer' | null>(null);
  const [showDemoOptions, setShowDemoOptions] = useState(true);

  const { login, loading, error, isAuthenticated } = useAuth();
  const { showSuccess } = useNotifications();
  const navigate = useNavigate();

  // Redirect if already authenticated
  useEffect(() => {
    if (isAuthenticated) {
      navigate('/dashboard');
    }
  }, [isAuthenticated, navigate]);

  // Demo users with realistic credentials
  const demoUsers = {
    admin: {
      email: 'admin@kartavya.demo',
      password: 'admin123',
      name: 'Security Administrator',
      role: 'admin',
      description: 'Full system access, user management, configuration'
    },
    analyst: {
      email: 'analyst@kartavya.demo', 
      password: 'analyst123',
      name: 'Security Analyst',
      role: 'analyst',
      description: 'Incident analysis, threat hunting, investigations'
    },
    viewer: {
      email: 'viewer@kartavya.demo',
      password: 'viewer123', 
      name: 'Security Viewer',
      role: 'viewer',
      description: 'Read-only access to dashboards and reports'
    }
  };

  // Auto-fill when demo user is selected
  useEffect(() => {
    if (selectedDemoUser && showDemoOptions) {
      setEmail(demoUsers[selectedDemoUser].email);
      setPassword(demoUsers[selectedDemoUser].password);
    }
  }, [selectedDemoUser, showDemoOptions]);

  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!email || !password) return;
    
    try {
      await login(email, password);
      showSuccess('Authentication Successful', `Welcome to Kartavya SIEM!`);
      navigate('/dashboard');
    } catch (error) {
      // Error handling is done by the auth store and notifications
    }
  };

  const handleDemoUserSelect = (userType: 'admin' | 'analyst' | 'viewer') => {
    setSelectedDemoUser(userType);
    setEmail(demoUsers[userType].email);
    setPassword(demoUsers[userType].password);
  };

  return (
    <div className="flex-1 flex">
      {/* Left Side - Branding & Features */}
      <div className="hidden lg:flex lg:flex-1 bg-gradient-to-br from-blue-900 via-gray-900 to-purple-900 relative overflow-hidden">
        {/* Animated Background */}
        <div className="absolute inset-0 bg-grid-white/[0.02] bg-[size:60px_60px]" />
        <div className="absolute inset-0 bg-gradient-to-t from-gray-900/50 via-transparent to-gray-900/50" />
        
        {/* Floating Elements */}
        {[...Array(15)].map((_, i) => (
          <div
            key={i}
            className="absolute w-1 h-1 bg-blue-400/20 rounded-full animate-pulse"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
              animationDelay: `${Math.random() * 3}s`,
              animationDuration: `${2 + Math.random() * 3}s`
            }}
          />
        ))}
        
        <div className="relative z-10 flex flex-col justify-center px-12 text-white">
          <div className="space-y-8">
            {/* Logo */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <Shield className="w-12 h-12 text-blue-400" />
                <div className="absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full flex items-center justify-center">
                  <CheckCircle className="w-3 h-3 text-gray-900" />
                </div>
              </div>
              <div>
                <h1 className="text-3xl font-bold">KARTAVYA SIEM</h1>
                <p className="text-blue-400 text-sm">Security Intelligence Platform</p>
              </div>
            </div>

            {/* Value Props */}
            <div className="space-y-6">
              <h2 className="text-2xl font-semibold">
                Enterprise-Grade Cybersecurity
              </h2>
              
              <div className="space-y-4">
                <FeatureItem 
                  icon={<Zap className="w-5 h-5 text-yellow-400" />}
                  title="Real-time Threat Detection"
                  description="AI-powered monitoring with sub-second response times"
                />
                <FeatureItem 
                  icon={<Brain className="w-5 h-5 text-purple-400" />}
                  title="Advanced Analytics"
                  description="Machine learning algorithms for predictive security"
                />
                <FeatureItem 
                  icon={<Activity className="w-5 h-5 text-green-400" />}
                  title="Comprehensive Monitoring"
                  description="360° visibility across your entire infrastructure"
                />
              </div>
            </div>

            {/* Stats */}
            <div className="grid grid-cols-3 gap-4 pt-8 border-t border-gray-700">
              <div className="text-center">
                <div className="text-2xl font-bold text-blue-400">99.9%</div>
                <div className="text-xs text-gray-400">Detection Rate</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">&lt;3s</div>
                <div className="text-xs text-gray-400">Response Time</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-purple-400">24/7</div>
                <div className="text-xs text-gray-400">Monitoring</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Right Side - Login Form */}
      <div className="flex-1 flex items-center justify-center p-8">
        <div className="w-full max-w-md space-y-8">
          {/* Header */}
          <div className="text-center">
            <div className="lg:hidden mb-6">
              <Shield className="w-12 h-12 text-blue-400 mx-auto mb-3" />
              <h1 className="text-2xl font-bold text-white">KARTAVYA SIEM</h1>
            </div>
            
            <h2 className="text-3xl font-bold text-white">Access Your Platform</h2>
            <p className="mt-2 text-gray-400">
              Sign in to your security intelligence dashboard
            </p>
          </div>

          {/* Demo Users Quick Access */}
          {showDemoOptions && (
            <div className="bg-gray-800/50 border border-gray-700 rounded-xl p-6">
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-white">Demo Access</h3>
                <button
                  onClick={() => setShowDemoOptions(false)}
                  className="text-gray-400 hover:text-gray-300 text-sm"
                >
                  Use Custom Login
                </button>
              </div>
              
              <div className="space-y-3">
                {Object.entries(demoUsers).map(([key, user]) => (
                  <button
                    key={key}
                    onClick={() => handleDemoUserSelect(key as any)}
                    className={`w-full p-4 text-left border rounded-lg transition-all hover:border-gray-500 ${
                      selectedDemoUser === key
                        ? 'border-blue-500 bg-blue-900/20'
                        : 'border-gray-600 hover:bg-gray-700/30'
                    }`}
                  >
                    <div className="flex items-center space-x-3">
                      <div className="flex-shrink-0">
                        {key === 'admin' && <Crown className="w-5 h-5 text-yellow-400" />}
                        {key === 'analyst' && <Search className="w-5 h-5 text-blue-400" />}
                        {key === 'viewer' && <Eye className="w-5 h-5 text-green-400" />}
                      </div>
                      <div className="flex-1">
                        <div className="font-medium text-white">{user.name}</div>
                        <div className="text-sm text-gray-400">{user.description}</div>
                      </div>
                      {selectedDemoUser === key && (
                        <CheckCircle className="w-5 h-5 text-blue-400" />
                      )}
                    </div>
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* Login Form */}
          <form onSubmit={handleLogin} className="space-y-6">
            <div>
              <label htmlFor="email" className="block text-sm font-medium text-gray-300 mb-2">
                Email Address
              </label>
              <div className="relative">
                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="email"
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="Enter your email"
                  disabled={showDemoOptions && selectedDemoUser !== null}
                  className="w-full pl-10 pr-4 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                  required
                />
              </div>
            </div>

            <div>
              <label htmlFor="password" className="block text-sm font-medium text-gray-300 mb-2">
                Password
              </label>
              <div className="relative">
                <KeyRound className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-gray-400" />
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  disabled={showDemoOptions && selectedDemoUser !== null}
                  className="w-full pl-10 pr-12 py-3 bg-gray-800 border border-gray-600 rounded-lg text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent disabled:opacity-50"
                  required
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-300"
                >
                  {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
                </button>
              </div>
            </div>

            {error && (
              <div className="p-4 bg-red-900/20 border border-red-700/50 rounded-lg">
                <div className="flex items-center space-x-2">
                  <AlertTriangle className="w-5 h-5 text-red-400" />
                  <p className="text-red-400 text-sm">{error}</p>
                </div>
              </div>
            )}

            <LoadingButton
              type="submit"
              loading={loading}
              disabled={!email || !password}
              className="w-full bg-blue-600 hover:bg-blue-700 text-white py-3 px-4 rounded-lg font-semibold transition-colors flex items-center justify-center space-x-2"
            >
              <UserCheck className="w-5 h-5" />
              <span>Sign In to Platform</span>
            </LoadingButton>
          </form>

          {/* Footer */}
          <div className="text-center space-y-4">
            <div className="flex items-center justify-center space-x-4 text-sm text-gray-500">
              <span>Secure authentication</span>
              <div className="w-1 h-1 bg-gray-500 rounded-full" />
              <span>Enterprise-grade security</span>
            </div>
            
            <Link
              to="/"
              className="inline-flex items-center space-x-2 text-blue-400 hover:text-blue-300 transition-colors"
            >
              <span>← Back to Homepage</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};

// Helper Component
interface FeatureItemProps {
  icon: React.ReactNode;
  title: string;
  description: string;
}

const FeatureItem: React.FC<FeatureItemProps> = ({ icon, title, description }) => (
  <div className="flex items-start space-x-3">
    <div className="flex-shrink-0 mt-1">{icon}</div>
    <div>
      <h4 className="font-medium text-white">{title}</h4>
      <p className="text-sm text-gray-400">{description}</p>
    </div>
  </div>
);

export default LoginPage;
