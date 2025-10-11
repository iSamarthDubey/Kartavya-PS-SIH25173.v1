import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { motion } from 'framer-motion'
import { Helmet } from 'react-helmet-async'
import { 
  Shield, 
  Eye,
  Activity,
  Globe,
  Zap,
  Lock,
  Server,
  AlertTriangle
} from 'lucide-react'

import LoginForm from '@/components/Auth/LoginForm'
import { useAppStore, useAuth } from '@/stores/appStore'

export default function Login() {
  const { login, isAuthenticated } = useAuth()
  const loading = useAppStore(state => state.loading)
  const [loginError, setLoginError] = useState<string>('')

  // Redirect if already authenticated
  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  const handleLogin = async (credentials: { username: string; password: string; remember?: boolean }) => {
    try {
      setLoginError('')
      await login(credentials.username, credentials.password)

      if (credentials.remember) {
        localStorage.setItem('synrgy_remember_user', credentials.username)
      } else {
        localStorage.removeItem('synrgy_remember_user')
      }
    } catch (error: any) {
      setLoginError(error.message || 'Authentication failed. Please check your credentials.')
    }
  }

  const features = [
    {
      icon: Eye,
      title: 'Real-time Monitoring',
      description: 'Continuous threat surveillance across your infrastructure'
    },
    {
      icon: Activity,
      title: 'Intelligent Analysis',
      description: 'AI-powered threat detection and pattern recognition'
    },
    {
      icon: Globe,
      title: 'Global Intelligence',
      description: 'Worldwide threat intelligence integration and correlation'
    },
    {
      icon: Zap,
      title: 'Rapid Response',
      description: 'Automated incident response and mitigation workflows'
    }
  ]

  return (
    <>
      <Helmet>
        <title>Sign In - SYNRGY</title>
        <meta name="description" content="Secure access to SYNRGY cybersecurity intelligence platform" />
      </Helmet>

      <div className="min-h-screen bg-synrgy-bg-900 flex">
        {/* Left Panel - Branding */}
        <div className="hidden lg:flex lg:w-1/2 relative overflow-hidden">
          {/* Background Pattern */}
          <div className="absolute inset-0 bg-gradient-to-br from-synrgy-primary/20 via-synrgy-bg-800 to-synrgy-accent/20" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_50%,rgba(120,119,198,0.3),transparent_50%),radial-gradient(circle_at_80%_20%,rgba(255,119,198,0.3),transparent_50%),radial-gradient(circle_at_40%_80%,rgba(120,119,198,0.2),transparent_50%)]" />
          
          <div className="relative z-10 flex flex-col justify-center p-12 text-white">
            {/* Logo and Brand */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
              className="mb-8"
            >
              <div className="flex items-center gap-3 mb-4">
                <div className="relative">
                  <Shield className="w-12 h-12 text-synrgy-primary" />
                  <div className="absolute inset-0 w-12 h-12 bg-synrgy-primary/20 rounded-lg blur-lg" />
                </div>
                <div>
                  <h1 className="text-4xl font-bold text-synrgy-text">SYNRGY</h1>
                  <p className="text-synrgy-muted">Cybersecurity Intelligence Platform</p>
                </div>
              </div>
              <p className="text-lg text-synrgy-text/80 max-w-md">
                Advanced threat intelligence and real-time security monitoring 
                for modern enterprises.
              </p>
            </motion.div>

            {/* Features */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4 }}
              className="space-y-6"
            >
              {features.map((feature, index) => (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, x: -20 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: 0.6 + index * 0.1 }}
                  className="flex items-start gap-4"
                >
                  <div className="flex-shrink-0 w-10 h-10 bg-synrgy-primary/20 rounded-lg flex items-center justify-center">
                    <feature.icon className="w-5 h-5 text-synrgy-primary" />
                  </div>
                  <div>
                    <h3 className="font-semibold text-synrgy-text">{feature.title}</h3>
                    <p className="text-sm text-synrgy-muted">{feature.description}</p>
                  </div>
                </motion.div>
              ))}
            </motion.div>

            {/* Stats */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 1.0 }}
              className="mt-12 flex items-center gap-8"
            >
              <div className="text-center">
                <div className="text-2xl font-bold text-synrgy-primary">99.9%</div>
                <div className="text-xs text-synrgy-muted">Uptime</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-synrgy-accent">24/7</div>
                <div className="text-xs text-synrgy-muted">Monitoring</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold text-green-400">100M+</div>
                <div className="text-xs text-synrgy-muted">Threats Blocked</div>
              </div>
            </motion.div>
          </div>

          {/* Animated Elements */}
          <div className="absolute top-10 right-10 w-20 h-20 border border-synrgy-primary/30 rounded-full animate-pulse" />
          <div className="absolute bottom-20 left-10 w-16 h-16 border border-synrgy-accent/30 rounded-full animate-bounce" style={{ animationDuration: '3s' }} />
          <div className="absolute top-1/3 right-1/4 w-12 h-12 border border-synrgy-primary/20 rounded-full animate-spin" style={{ animationDuration: '8s' }} />
        </div>

        {/* Right Panel - Login Form */}
        <div className="w-full lg:w-1/2 flex flex-col justify-center p-8">
          <div className="max-w-md mx-auto w-full">
            {/* Mobile Logo */}
            <motion.div
              initial={{ opacity: 0, y: -20 }}
              animate={{ opacity: 1, y: 0 }}
              className="lg:hidden text-center mb-8"
            >
              <div className="flex items-center justify-center gap-3 mb-4">
                <Shield className="w-10 h-10 text-synrgy-primary" />
                <h1 className="text-3xl font-bold text-synrgy-text">SYNRGY</h1>
              </div>
              <p className="text-synrgy-muted">Cybersecurity Intelligence Platform</p>
            </motion.div>

            {/* Welcome Message */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 }}
              className="text-center mb-8"
            >
              <h2 className="text-2xl font-bold text-synrgy-text mb-2">
                Welcome Back
              </h2>
              <p className="text-synrgy-muted">
                Sign in to access your security dashboard
              </p>
            </motion.div>

            {/* Login Form */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <LoginForm 
                onLogin={handleLogin}
                loading={loading}
                error={loginError}
              />
            </motion.div>

            {/* Security Notice */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.4 }}
              className="mt-8 text-center"
            >
              <div className="bg-amber-500/10 border border-amber-500/20 rounded-lg p-3">
                <div className="flex items-center justify-center gap-2 text-amber-400 text-sm">
                  <AlertTriangle className="w-4 h-4" />
                  <span>This system is monitored. Unauthorized access is prohibited.</span>
                </div>
              </div>
            </motion.div>

            {/* Footer */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.6 }}
              className="mt-8 text-center text-xs text-synrgy-muted"
            >
              <div className="flex items-center justify-center gap-4">
                <div className="flex items-center gap-1">
                  <Lock className="w-3 h-3" />
                  <span>SSL Secured</span>
                </div>
                <div className="flex items-center gap-1">
                  <Server className="w-3 h-3" />
                  <span>SOC 2 Compliant</span>
                </div>
              </div>
              <p className="mt-2">© 2024 SYNRGY. All rights reserved.</p>
            </motion.div>
          </div>
        </div>
      </div>
    </>
  )
}
