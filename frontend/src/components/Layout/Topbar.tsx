/**
 * SYNRGY Topbar Component
 * Implements SYNRGY.TXT specification: Logo | Mode Switch | Global Search | User Menu
 */

import React, { useState } from 'react'
import { Search, Settings, User, Bell, Zap } from 'lucide-react'
import { useAuth } from '@/providers/AuthProvider'
import { useAppStore } from '@/stores/appStore'
import { useNavigate } from 'react-router-dom'

interface TopbarProps {
  className?: string
}

const modes = [
  { key: 'dashboard', label: 'Dashboard', path: '/app/dashboard' },
  { key: 'chat', label: 'Chat', path: '/app/chat' },
  { key: 'hybrid', label: 'Hybrid', path: '/app/hybrid' },
] as const

export default function Topbar({ className = '' }: TopbarProps) {
  const { user, logout } = useAuth()
  const { mode, setMode } = useAppStore()
  const navigate = useNavigate()
  const [showUserMenu, setShowUserMenu] = useState(false)
  const [globalSearch, setGlobalSearch] = useState('')

  const handleModeSwitch = (newMode: typeof modes[number]['key']) => {
    setMode(newMode as any)
    const selectedMode = modes.find(m => m.key === newMode)
    if (selectedMode) {
      navigate(selectedMode.path)
    }
  }

  const handleGlobalSearch = (e: React.FormEvent) => {
    e.preventDefault()
    if (globalSearch.trim()) {
      // Navigate to chat with search query
      setMode('chat')
      navigate('/app/chat', { state: { initialQuery: globalSearch } })
      setGlobalSearch('')
    }
  }

  return (
    <div className={`h-16 bg-synrgy-surface border-b border-synrgy-primary/10 flex items-center justify-between px-6 ${className}`}>
      {/* Left Section: Logo + Mode Switch */}
      <div className="flex items-center gap-6">
        {/* SYNRGY Logo */}
        <div className="flex items-center gap-2">
          <Zap className="w-6 h-6 text-synrgy-primary" />
          <span className="text-xl font-heading font-bold text-gradient">ＳＹＮＲＧＹ</span>
        </div>

        {/* Mode Switcher */}
        <div className="flex items-center bg-synrgy-bg-900/50 rounded-lg p-1">
          {modes.map((modeOption) => (
            <button
              key={modeOption.key}
              onClick={() => handleModeSwitch(modeOption.key)}
              className={`px-4 py-2 rounded-md text-sm font-medium transition-colors ${
                mode === modeOption.key
                  ? 'bg-synrgy-primary text-synrgy-bg-900'
                  : 'text-synrgy-muted hover:text-synrgy-text hover:bg-synrgy-primary/10'
              }`}
            >
              {modeOption.label}
            </button>
          ))}
        </div>
      </div>

      {/* Center: Global Search */}
      <div className="flex-1 max-w-md mx-6">
        <form onSubmit={handleGlobalSearch} className="relative">
          <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-synrgy-muted" />
          <input
            type="text"
            value={globalSearch}
            onChange={(e) => setGlobalSearch(e.target.value)}
            placeholder="Ask CYNRGY anything..."
            className="w-full pl-10 pr-4 py-2 bg-synrgy-bg-900/50 border border-synrgy-primary/20 rounded-lg text-synrgy-text placeholder:text-synrgy-muted focus:border-synrgy-primary/50 focus:outline-none"
          />
        </form>
      </div>

      {/* Right Section: Notifications + User Menu */}
      <div className="flex items-center gap-4">
        {/* Notifications */}
        <button className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors relative">
          <Bell className="w-5 h-5 text-synrgy-muted" />
          <div className="absolute -top-1 -right-1 w-3 h-3 bg-synrgy-accent rounded-full" />
        </button>

        {/* Settings */}
        <button className="p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors">
          <Settings className="w-5 h-5 text-synrgy-muted" />
        </button>

        {/* User Menu */}
        <div className="relative">
          <button
            onClick={() => setShowUserMenu(!showUserMenu)}
            className="flex items-center gap-2 p-2 hover:bg-synrgy-primary/10 rounded-lg transition-colors"
          >
            <div className="w-8 h-8 bg-synrgy-primary/20 rounded-full flex items-center justify-center">
              <User className="w-4 h-4 text-synrgy-primary" />
            </div>
            <div className="text-left hidden sm:block">
              <div className="text-sm font-medium text-synrgy-text">
                {user?.full_name || user?.username || 'User'}
              </div>
              <div className="text-xs text-synrgy-muted capitalize">
                {user?.role || 'Analyst'}
              </div>
            </div>
          </button>

          {/* User Dropdown Menu */}
          {showUserMenu && (
            <div className="absolute right-0 mt-2 w-48 bg-synrgy-surface border border-synrgy-primary/20 rounded-lg shadow-lg z-50">
              <div className="p-2">
                <button
                  onClick={() => {
                    navigate('/app/settings')
                    setShowUserMenu(false)
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-synrgy-text hover:bg-synrgy-primary/10 rounded"
                >
                  Settings
                </button>
                <button
                  onClick={() => {
                    logout()
                    setShowUserMenu(false)
                  }}
                  className="w-full text-left px-3 py-2 text-sm text-red-400 hover:bg-red-400/10 rounded"
                >
                  Sign out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}
