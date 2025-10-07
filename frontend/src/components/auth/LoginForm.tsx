import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Shield, 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  LogIn, 
  AlertTriangle,
  Smartphone,
  Key,
  Loader2
} from 'lucide-react';
import { useAuth, LoginCredentials } from '../../contexts/AuthContext';

interface LoginFormProps {
  onSuccess?: () => void;
}

export const LoginForm: React.FC<LoginFormProps> = ({ onSuccess }) => {
  const { login, loading, error, clearError } = useAuth();
  
  const [formData, setFormData] = useState<LoginCredentials>({
    username: '',
    password: '',
    mfaToken: '',
    rememberMe: false,
  });
  
  const [showPassword, setShowPassword] = useState(false);
  const [requiresMFA, setRequiresMFA] = useState(false);
  const [loginStep, setLoginStep] = useState<'credentials' | 'mfa'>('credentials');

  const handleInputChange = (field: keyof LoginCredentials, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }));
    if (error) clearError();
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    try {
      await login(formData);
      onSuccess?.();
    } catch (error: any) {
      // Check if MFA is required
      if (error.response?.status === 428) { // 428 Precondition Required
        setRequiresMFA(true);
        setLoginStep('mfa');
      }
    }
  };

  const renderCredentialsStep = () => (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: -20 }}
      className="space-y-6"
    >
      {/* Username Field */}
      <div>
        <label htmlFor="username" className="block text-sm font-medium text-space-300 mb-2">
          Username or Email
        </label>
        <div className="relative">
          <User className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-space-400" />
          <input
            id="username"
            type="text"
            value={formData.username}
            onChange={(e) => handleInputChange('username', e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-space-900/50 border border-space-700/50 rounded-lg text-white placeholder-space-400 focus:border-cyber-accent focus:ring-2 focus:ring-cyber-accent/20 transition-all duration-300"
            placeholder="Enter your username"
            required
            autoComplete="username"
          />
        </div>
      </div>

      {/* Password Field */}
      <div>
        <label htmlFor="password" className="block text-sm font-medium text-space-300 mb-2">
          Password
        </label>
        <div className="relative">
          <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-space-400" />
          <input
            id="password"
            type={showPassword ? 'text' : 'password'}
            value={formData.password}
            onChange={(e) => handleInputChange('password', e.target.value)}
            className="w-full pl-11 pr-12 py-3 bg-space-900/50 border border-space-700/50 rounded-lg text-white placeholder-space-400 focus:border-cyber-accent focus:ring-2 focus:ring-cyber-accent/20 transition-all duration-300"
            placeholder="Enter your password"
            required
            autoComplete="current-password"
          />
          <button
            type="button"
            onClick={() => setShowPassword(!showPassword)}
            className="absolute right-3 top-1/2 transform -translate-y-1/2 text-space-400 hover:text-space-300 transition-colors"
          >
            {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Remember Me */}
      <div className="flex items-center">
        <input
          id="remember-me"
          type="checkbox"
          checked={formData.rememberMe || false}
          onChange={(e) => handleInputChange('rememberMe', e.target.checked)}
          className="w-4 h-4 text-cyber-accent bg-space-900/50 border-space-700/50 rounded focus:ring-cyber-accent focus:ring-2"
        />
        <label htmlFor="remember-me" className="ml-2 text-sm text-space-300">
          Keep me signed in for 30 days
        </label>
      </div>
    </motion.div>
  );

  const renderMFAStep = () => (
    <motion.div
      initial={{ opacity: 0, x: 20 }}
      animate={{ opacity: 1, x: 0 }}
      exit={{ opacity: 0, x: 20 }}
      className="space-y-6"
    >
      <div className="text-center mb-6">
        <div className="w-16 h-16 bg-cyber-accent/20 rounded-full flex items-center justify-center mx-auto mb-4">
          <Smartphone className="w-8 h-8 text-cyber-accent" />
        </div>
        <h3 className="text-lg font-semibold text-white mb-2">Two-Factor Authentication</h3>
        <p className="text-sm text-space-400">
          Enter the 6-digit code from your authenticator app
        </p>
      </div>

      <div>
        <label htmlFor="mfa-token" className="block text-sm font-medium text-space-300 mb-2">
          Authentication Code
        </label>
        <div className="relative">
          <Key className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-space-400" />
          <input
            id="mfa-token"
            type="text"
            value={formData.mfaToken || ''}
            onChange={(e) => handleInputChange('mfaToken', e.target.value)}
            className="w-full pl-11 pr-4 py-3 bg-space-900/50 border border-space-700/50 rounded-lg text-white placeholder-space-400 focus:border-cyber-accent focus:ring-2 focus:ring-cyber-accent/20 transition-all duration-300 text-center text-lg font-mono tracking-wider"
            placeholder="000000"
            maxLength={6}
            pattern="[0-9]{6}"
            autoComplete="one-time-code"
            required
          />
        </div>
      </div>

      <button
        type="button"
        onClick={() => setLoginStep('credentials')}
        className="text-sm text-cyber-accent hover:text-cyber-accent/80 transition-colors"
      >
        ← Back to login
      </button>
    </motion.div>
  );

  return (
    <div className="min-h-screen bg-gradient-to-br from-cyber-darker via-space-950 to-cyber-dark flex items-center justify-center p-6">
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Header */}
        <div className="text-center mb-8">
          <div className="w-20 h-20 bg-space-gradient rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-glow">
            <Shield className="w-10 h-10 text-white" />
          </div>
          <h1 className="text-3xl font-bold text-white mb-2">Kartavya SIEM</h1>
          <p className="text-space-400">Conversational Security Intelligence</p>
          
          {/* ISRO Badge */}
          <div className="inline-flex items-center space-x-2 mt-4 px-3 py-1 bg-isro-primary/20 border border-isro-primary/30 rounded-full">
            <div className="w-2 h-2 bg-isro-orange rounded-full animate-pulse" />
            <span className="text-xs font-medium text-space-300">ISRO • Department of Space</span>
          </div>
        </div>

        {/* Login Form */}
        <div className="bg-gradient-to-br from-space-900/50 to-cyber-dark/50 backdrop-blur-sm border border-space-700/50 rounded-2xl p-8 shadow-space">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Error Message */}
            <AnimatePresence>
              {error && (
                <motion.div
                  initial={{ opacity: 0, y: -10 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -10 }}
                  className="bg-red-500/10 border border-red-500/20 rounded-lg p-4 flex items-center space-x-3"
                >
                  <AlertTriangle className="w-5 h-5 text-red-400 flex-shrink-0" />
                  <span className="text-sm text-red-300">{error}</span>
                </motion.div>
              )}
            </AnimatePresence>

            {/* Form Steps */}
            <AnimatePresence mode="wait">
              {loginStep === 'credentials' ? renderCredentialsStep() : renderMFAStep()}
            </AnimatePresence>

            {/* Submit Button */}
            <motion.button
              type="submit"
              disabled={loading || !formData.username || !formData.password}
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              className="w-full bg-cyber-accent/20 hover:bg-cyber-accent/30 border border-cyber-accent/50 text-cyber-accent font-semibold py-3 px-4 rounded-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
            >
              {loading ? (
                <Loader2 className="w-5 h-5 animate-spin" />
              ) : (
                <>
                  <LogIn className="w-5 h-5" />
                  <span>{loginStep === 'mfa' ? 'Verify & Sign In' : 'Sign In'}</span>
                </>
              )}
            </motion.button>
          </form>

          {/* Footer */}
          <div className="mt-8 text-center">
            <div className="text-xs text-space-500 space-y-1">
              <p>Secure authentication powered by industry standards</p>
              <p>© 2025 ISRO - All rights reserved</p>
            </div>
          </div>
        </div>

        {/* Security Notice */}
        <div className="mt-6 text-center text-xs text-space-500">
          <p className="flex items-center justify-center space-x-1">
            <Shield className="w-3 h-3" />
            <span>Your connection is secured with end-to-end encryption</span>
          </p>
        </div>
      </motion.div>
    </div>
  );
};
