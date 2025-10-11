import { useState } from 'react'
import { motion } from 'framer-motion'
import { 
  User, 
  Lock, 
  Eye, 
  EyeOff, 
  Shield,
  Loader2,
  ArrowRight,
  AlertCircle,
  CheckCircle
} from 'lucide-react'

interface LoginFormProps {
  onLogin: (credentials: { username: string; password: string; remember?: boolean }) => Promise<void>
  loading?: boolean
  error?: string
  className?: string
}

export default function LoginForm({ onLogin, loading = false, error, className = '' }: LoginFormProps) {
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    remember: false
  })
  const [showPassword, setShowPassword] = useState(false)
  const [formErrors, setFormErrors] = useState<Record<string, string>>({})

  const validateForm = () => {
    const errors: Record<string, string> = {}
    
    if (!formData.username.trim()) {
      errors.username = 'Username is required'
    }
    
    if (!formData.password) {
      errors.password = 'Password is required'
    } else if (formData.password.length < 6) {
      errors.password = 'Password must be at least 6 characters'
    }
    
    setFormErrors(errors)
    return Object.keys(errors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    try {
      await onLogin(formData)
    } catch (err) {
      // Error handling is managed by parent component
    }
  }

  const handleInputChange = (field: string, value: string | boolean) => {
    setFormData(prev => ({ ...prev, [field]: value }))
    
    // Clear field error when user starts typing
    if (formErrors[field]) {
      setFormErrors(prev => ({ ...prev, [field]: '' }))
    }
  }

  return (
    <div className={`w-full max-w-md ${className}`}>
      <form onSubmit={handleSubmit} className="space-y-6">
        {/* Username Field */}
        <div className="space-y-2">
          <label htmlFor="username" className="block text-sm font-medium text-synrgy-text">
            Username
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <User className={`w-5 h-5 ${formErrors.username ? 'text-red-400' : 'text-synrgy-muted'}`} />
            </div>
            <input
              id="username"
              type="text"
              value={formData.username}
              onChange={(e) => handleInputChange('username', e.target.value)}
              className={`w-full pl-10 pr-4 py-3 bg-synrgy-surface border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                formErrors.username
                  ? 'border-red-400 focus:ring-red-400/50'
                  : 'border-synrgy-primary/20 focus:border-synrgy-primary focus:ring-synrgy-primary/50'
              } text-synrgy-text placeholder-synrgy-muted`}
              placeholder="Enter your username"
              disabled={loading}
            />
          </div>
          {formErrors.username && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-red-400 flex items-center gap-1"
            >
              <AlertCircle className="w-4 h-4" />
              {formErrors.username}
            </motion.p>
          )}
        </div>

        {/* Password Field */}
        <div className="space-y-2">
          <label htmlFor="password" className="block text-sm font-medium text-synrgy-text">
            Password
          </label>
          <div className="relative">
            <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
              <Lock className={`w-5 h-5 ${formErrors.password ? 'text-red-400' : 'text-synrgy-muted'}`} />
            </div>
            <input
              id="password"
              type={showPassword ? 'text' : 'password'}
              value={formData.password}
              onChange={(e) => handleInputChange('password', e.target.value)}
              className={`w-full pl-10 pr-12 py-3 bg-synrgy-surface border rounded-lg focus:outline-none focus:ring-2 transition-all ${
                formErrors.password
                  ? 'border-red-400 focus:ring-red-400/50'
                  : 'border-synrgy-primary/20 focus:border-synrgy-primary focus:ring-synrgy-primary/50'
              } text-synrgy-text placeholder-synrgy-muted`}
              placeholder="Enter your password"
              disabled={loading}
            />
            <button
              type="button"
              onClick={() => setShowPassword(!showPassword)}
              className="absolute inset-y-0 right-0 pr-3 flex items-center text-synrgy-muted hover:text-synrgy-text transition-colors"
              disabled={loading}
            >
              {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
            </button>
          </div>
          {formErrors.password && (
            <motion.p
              initial={{ opacity: 0, y: -5 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-sm text-red-400 flex items-center gap-1"
            >
              <AlertCircle className="w-4 h-4" />
              {formErrors.password}
            </motion.p>
          )}
        </div>

        {/* Remember Me */}
        <div className="flex items-center justify-between">
          <div className="flex items-center">
            <input
              id="remember"
              type="checkbox"
              checked={formData.remember}
              onChange={(e) => handleInputChange('remember', e.target.checked)}
              className="w-4 h-4 text-synrgy-primary bg-synrgy-surface border-synrgy-primary/20 rounded focus:ring-synrgy-primary focus:ring-2"
              disabled={loading}
            />
            <label htmlFor="remember" className="ml-2 text-sm text-synrgy-muted">
              Remember me
            </label>
          </div>
          
          <button
            type="button"
            className="text-sm text-synrgy-primary hover:text-synrgy-accent transition-colors"
            disabled={loading}
          >
            Forgot password?
          </button>
        </div>

        {/* Error Message */}
        {error && (
          <motion.div
            initial={{ opacity: 0, y: -5 }}
            animate={{ opacity: 1, y: 0 }}
            className="bg-red-500/10 border border-red-500/20 rounded-lg p-3"
          >
            <div className="flex items-center gap-2 text-red-400">
              <AlertCircle className="w-4 h-4" />
              <span className="text-sm">{error}</span>
            </div>
          </motion.div>
        )}

        {/* Submit Button */}
        <motion.button
          type="submit"
          disabled={loading || !formData.username || !formData.password}
          whileHover={{ scale: loading ? 1 : 1.02 }}
          whileTap={{ scale: loading ? 1 : 0.98 }}
          className={`w-full py-3 px-4 rounded-lg font-medium text-synrgy-bg-900 transition-all flex items-center justify-center gap-2 ${
            loading || !formData.username || !formData.password
              ? 'bg-synrgy-muted cursor-not-allowed'
              : 'bg-synrgy-primary hover:bg-synrgy-accent shadow-synrgy-glow hover:shadow-synrgy-glow-strong'
          }`}
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Signing in...</span>
            </>
          ) : (
            <>
              <Shield className="w-5 h-5" />
              <span>Sign In to SYNRGY</span>
              <ArrowRight className="w-4 h-4" />
            </>
          )}
        </motion.button>
      </form>

      {/* Additional Options */}
      <div className="mt-6 text-center">
        <p className="text-sm text-synrgy-muted">
          Don't have an account?{' '}
          <button 
            type="button"
            className="text-synrgy-primary hover:text-synrgy-accent transition-colors font-medium"
            disabled={loading}
          >
            Request Access
          </button>
        </p>
      </div>

      {/* Security Note */}
      <div className="mt-4 bg-synrgy-primary/5 border border-synrgy-primary/10 rounded-lg p-3">
        <div className="flex items-start gap-2 text-xs text-synrgy-muted">
          <CheckCircle className="w-4 h-4 text-green-400 mt-0.5 flex-shrink-0" />
          <div>
            <p className="font-medium text-synrgy-text">Secure Connection</p>
            <p>Your connection is encrypted and monitored for security purposes.</p>
          </div>
        </div>
      </div>
    </div>
  )
}
