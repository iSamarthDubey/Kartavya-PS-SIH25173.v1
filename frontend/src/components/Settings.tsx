/**
 * Settings Component - Placeholder
 * System configuration and user preferences
 */

import React from 'react';
import { 
  Settings as SettingsIcon, 
  User, 
  Shield, 
  Bell, 
  Palette, 
  Database,
  Key,
  Globe
} from 'lucide-react';
import { useAuth } from '../store/appStore';
import { ApiErrorBoundary } from './ErrorBoundary';

const Settings: React.FC = () => {
  const { user } = useAuth();

  return (
    <ApiErrorBoundary>
      <div className="p-6 min-h-screen bg-gray-900">
        <div className="max-w-6xl mx-auto">
          <div className="mb-8">
            <h1 className="text-3xl font-bold text-white mb-4 flex items-center space-x-3">
              <SettingsIcon className="w-8 h-8 text-blue-400" />
              <span>Settings</span>
            </h1>
            <p className="text-gray-400">
              Configure your SIEM platform settings, preferences, and security options.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {/* User Profile */}
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <User className="w-6 h-6 text-blue-400" />
                <h2 className="text-xl font-semibold text-white">User Profile</h2>
              </div>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                  <div className="p-3 bg-gray-700 rounded-lg text-white">
                    {user?.name || 'N/A'}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                  <div className="p-3 bg-gray-700 rounded-lg text-white">
                    {user?.email || 'N/A'}
                  </div>
                </div>
                
                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
                  <div className="p-3 bg-gray-700 rounded-lg text-white capitalize">
                    {user?.role || 'N/A'}
                  </div>
                </div>
              </div>
            </div>

            {/* Security Settings */}
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Shield className="w-6 h-6 text-green-400" />
                <h2 className="text-xl font-semibold text-white">Security</h2>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Two-Factor Authentication</p>
                    <p className="text-sm text-gray-400">Add extra security to your account</p>
                  </div>
                  <div className="w-10 h-6 bg-gray-600 rounded-full relative">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 left-1"></div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Session Timeout</p>
                    <p className="text-sm text-gray-400">Automatically log out after inactivity</p>
                  </div>
                  <span className="text-blue-400 font-medium">30 min</span>
                </div>
              </div>
            </div>

            {/* Notifications */}
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Bell className="w-6 h-6 text-yellow-400" />
                <h2 className="text-xl font-semibold text-white">Notifications</h2>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Critical Alerts</p>
                    <p className="text-sm text-gray-400">Receive immediate notifications</p>
                  </div>
                  <div className="w-10 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1"></div>
                  </div>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Email Reports</p>
                    <p className="text-sm text-gray-400">Daily and weekly summaries</p>
                  </div>
                  <div className="w-10 h-6 bg-blue-600 rounded-full relative">
                    <div className="w-4 h-4 bg-white rounded-full absolute top-1 right-1"></div>
                  </div>
                </div>
              </div>
            </div>

            {/* System Settings */}
            <div className="bg-gray-800 border border-gray-700 rounded-lg p-6">
              <div className="flex items-center space-x-3 mb-4">
                <Database className="w-6 h-6 text-purple-400" />
                <h2 className="text-xl font-semibold text-white">System</h2>
              </div>
              
              <div className="space-y-4">
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Data Retention</p>
                    <p className="text-sm text-gray-400">How long to keep security logs</p>
                  </div>
                  <span className="text-blue-400 font-medium">90 days</span>
                </div>
                
                <div className="flex items-center justify-between p-3 bg-gray-700 rounded-lg">
                  <div>
                    <p className="text-white font-medium">Refresh Rate</p>
                    <p className="text-sm text-gray-400">Dashboard auto-refresh interval</p>
                  </div>
                  <span className="text-blue-400 font-medium">30 sec</span>
                </div>
              </div>
            </div>
          </div>

          <div className="mt-8 text-center">
            <div className="bg-blue-900/20 border border-blue-700/50 rounded-lg p-6">
              <h3 className="text-blue-400 font-semibold mb-2">Demo Environment</h3>
              <p className="text-gray-400">
                This is a demonstration environment. Settings shown here are for display purposes only 
                and do not affect real system configuration.
              </p>
            </div>
          </div>
        </div>
      </div>
    </ApiErrorBoundary>
  );
};

export default Settings;
