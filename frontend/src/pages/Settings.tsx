import React, { useState, useMemo, useCallback, memo } from 'react'
import { useAuth } from '@/stores/appStore'
import {
  User,
  Bell,
  Shield,
  Palette,
  Monitor,
  Moon,
  Sun,
  Globe,
  Lock,
  Database,
  Zap,
} from 'lucide-react'

const SettingsPage = memo(function SettingsPage() {
  const { user } = useAuth()
  const [activeTab, setActiveTab] = useState('profile')

  // Memoize tabs configuration to prevent unnecessary re-renders
  const tabs = useMemo(() => [
    { id: 'profile', name: 'Profile', icon: User },
    { id: 'notifications', name: 'Notifications', icon: Bell },
    { id: 'security', name: 'Security', icon: Shield },
    { id: 'appearance', name: 'Appearance', icon: Palette },
    { id: 'system', name: 'System', icon: Monitor },
  ], [])

  // Memoize tab change handler
  const handleTabChange = useCallback((tabId: string) => {
    setActiveTab(tabId)
  }, [])

  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        {/* Header */}
        <div className="mb-8">
          <h1 className="heading-lg text-synrgy-text mb-2">Settings</h1>
          <p className="text-synrgy-muted">Manage your account settings and preferences.</p>
        </div>

        <div className="flex gap-8">
          {/* Sidebar */}
          <div className="w-64 flex-shrink-0">
            <nav className="space-y-1">
              {tabs.map(tab => (
                <button
                  key={tab.id}
                  onClick={() => handleTabChange(tab.id)}
                  className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                    activeTab === tab.id
                      ? 'bg-synrgy-primary/10 text-synrgy-primary border border-synrgy-primary/20'
                      : 'text-synrgy-muted hover:text-synrgy-text hover:bg-synrgy-primary/5'
                  }`}
                >
                  <tab.icon className="w-4 h-4 mr-3" />
                  {tab.name}
                </button>
              ))}
            </nav>
          </div>

          {/* Content */}
          <div className="flex-1">
            <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
              {activeTab === 'profile' && (
                <div>
                  <h2 className="heading-md mb-4">Profile Information</h2>
                  <div className="space-y-4">
                    <div>
                      <label className="block text-sm font-medium text-synrgy-text mb-2">
                        Full Name
                      </label>
                      <input
                        type="text"
                        defaultValue={user?.full_name || ''}
                        className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-synrgy-text mb-2">
                        Username
                      </label>
                      <input
                        type="text"
                        defaultValue={user?.username || ''}
                        disabled
                        className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/10 rounded-lg text-synrgy-muted cursor-not-allowed"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-synrgy-text mb-2">
                        Email
                      </label>
                      <input
                        type="email"
                        defaultValue={user?.email || ''}
                        className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-synrgy-text mb-2">
                        Role
                      </label>
                      <input
                        type="text"
                        value={user?.role || ''}
                        disabled
                        className="w-full px-3 py-2 bg-synrgy-bg-900 border border-synrgy-primary/10 rounded-lg text-synrgy-muted cursor-not-allowed capitalize"
                      />
                    </div>
                    <button className="btn-primary">Save Changes</button>
                  </div>
                </div>
              )}

              {activeTab === 'notifications' && (
                <div>
                  <h2 className="heading-md mb-4">Notification Preferences</h2>
                  <div className="space-y-4">
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-synrgy-text">Security Alerts</h3>
                        <p className="text-sm text-synrgy-muted">
                          Get notified about security incidents
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-synrgy-bg-800 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-synrgy-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-synrgy-primary"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-synrgy-text">System Updates</h3>
                        <p className="text-sm text-synrgy-muted">
                          Notifications about system maintenance
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-synrgy-bg-800 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-synrgy-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-synrgy-primary"></div>
                      </label>
                    </div>
                    <div className="flex items-center justify-between">
                      <div>
                        <h3 className="text-sm font-medium text-synrgy-text">Report Generation</h3>
                        <p className="text-sm text-synrgy-muted">
                          Notifications when reports are ready
                        </p>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" />
                        <div className="w-11 h-6 bg-synrgy-bg-800 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-synrgy-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-synrgy-primary"></div>
                      </label>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'security' && (
                <div>
                  <h2 className="heading-md mb-4">Security Settings</h2>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-sm font-medium text-synrgy-text mb-3">Change Password</h3>
                      <div className="space-y-3">
                        <input
                          type="password"
                          placeholder="Current password"
                          className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50"
                        />
                        <input
                          type="password"
                          placeholder="New password"
                          className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50"
                        />
                        <input
                          type="password"
                          placeholder="Confirm new password"
                          className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50"
                        />
                        <button className="btn-primary">Update Password</button>
                      </div>
                    </div>

                    <div className="pt-6 border-t border-synrgy-primary/10">
                      <div className="flex items-center gap-3 mb-4">
                        <Lock className="w-5 h-5 text-synrgy-primary" />
                        <h3 className="text-sm font-medium text-synrgy-text">Session Management</h3>
                      </div>
                      <p className="text-sm text-synrgy-muted mb-4">
                        You are currently signed in on this device. You can sign out of all other
                        sessions.
                      </p>
                      <button className="btn-secondary">Sign out all other sessions</button>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'appearance' && (
                <div>
                  <h2 className="heading-md mb-4">Appearance</h2>
                  <div className="space-y-6">
                    <div>
                      <h3 className="text-sm font-medium text-synrgy-text mb-3">Theme</h3>
                      <div className="grid grid-cols-3 gap-3">
                        <label className="flex items-center p-3 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg cursor-pointer hover:border-synrgy-primary/40 transition-colors">
                          <input
                            type="radio"
                            name="theme"
                            value="dark"
                            defaultChecked
                            className="sr-only"
                          />
                          <Moon className="w-5 h-5 text-synrgy-primary mr-3" />
                          <span className="text-sm text-synrgy-text">Dark</span>
                        </label>
                        <label className="flex items-center p-3 bg-synrgy-bg-800 border border-synrgy-primary/10 rounded-lg cursor-pointer hover:border-synrgy-primary/40 transition-colors">
                          <input type="radio" name="theme" value="light" className="sr-only" />
                          <Sun className="w-5 h-5 text-synrgy-muted mr-3" />
                          <span className="text-sm text-synrgy-muted">Light</span>
                        </label>
                        <label className="flex items-center p-3 bg-synrgy-bg-800 border border-synrgy-primary/10 rounded-lg cursor-pointer hover:border-synrgy-primary/40 transition-colors">
                          <input type="radio" name="theme" value="auto" className="sr-only" />
                          <Monitor className="w-5 h-5 text-synrgy-muted mr-3" />
                          <span className="text-sm text-synrgy-muted">Auto</span>
                        </label>
                      </div>
                    </div>

                    <div>
                      <h3 className="text-sm font-medium text-synrgy-text mb-3">Language</h3>
                      <select className="w-full px-3 py-2 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded-lg text-synrgy-text focus:outline-none focus:ring-2 focus:ring-synrgy-primary/50">
                        <option value="en">English</option>
                        <option value="es">Español</option>
                        <option value="fr">Français</option>
                        <option value="de">Deutsch</option>
                      </select>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'system' && (
                <div>
                  <h2 className="heading-md mb-4">System Preferences</h2>
                  <div className="space-y-6">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Database className="w-5 h-5 text-synrgy-primary" />
                        <div>
                          <h3 className="text-sm font-medium text-synrgy-text">Data Retention</h3>
                          <p className="text-sm text-synrgy-muted">
                            Automatic cleanup of old logs and data
                          </p>
                        </div>
                      </div>
                      <select className="px-3 py-1 bg-synrgy-bg-800 border border-synrgy-primary/20 rounded text-sm text-synrgy-text">
                        <option value="30">30 days</option>
                        <option value="90">90 days</option>
                        <option value="180">180 days</option>
                        <option value="365">1 year</option>
                      </select>
                    </div>

                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-3">
                        <Zap className="w-5 h-5 text-synrgy-primary" />
                        <div>
                          <h3 className="text-sm font-medium text-synrgy-text">Performance Mode</h3>
                          <p className="text-sm text-synrgy-muted">Optimize system performance</p>
                        </div>
                      </div>
                      <label className="relative inline-flex items-center cursor-pointer">
                        <input type="checkbox" className="sr-only peer" defaultChecked />
                        <div className="w-11 h-6 bg-synrgy-bg-800 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-synrgy-primary/25 rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-synrgy-primary"></div>
                      </label>
                    </div>

                    <div className="pt-6 border-t border-synrgy-primary/10">
                      <div className="flex items-center gap-3 mb-4">
                        <Globe className="w-5 h-5 text-synrgy-primary" />
                        <h3 className="text-sm font-medium text-synrgy-text">System Information</h3>
                      </div>
                      <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                          <span className="text-synrgy-muted">Version:</span>
                          <span className="text-synrgy-text ml-2">SYNRGY v1.0.0</span>
                        </div>
                        <div>
                          <span className="text-synrgy-muted">Build:</span>
                          <span className="text-synrgy-text ml-2">2025.01.11</span>
                        </div>
                        <div>
                          <span className="text-synrgy-muted">Environment:</span>
                          <span className="text-synrgy-text ml-2">Development</span>
                        </div>
                        <div>
                          <span className="text-synrgy-muted">API Status:</span>
                          <span className="text-synrgy-accent ml-2">Online</span>
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
})

export default SettingsPage
