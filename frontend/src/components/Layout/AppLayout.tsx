import { ReactNode } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { 
  LayoutDashboard, 
  MessageSquare, 
  FileText, 
  Search, 
  Settings, 
  Shield,
  Activity
} from 'lucide-react'
import { useAuth } from '@/stores/appStore'

interface AppLayoutProps {
  children: ReactNode
}

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutDashboard },
  { name: 'Chat', href: '/chat', icon: MessageSquare },
  { name: 'Hybrid', href: '/hybrid', icon: Activity },
  { name: 'Reports', href: '/reports', icon: FileText },
  { name: 'Investigations', href: '/investigations', icon: Search },
]

export default function AppLayout({ children }: AppLayoutProps) {
  const location = useLocation()
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  return (
    <div className="h-screen bg-synrgy-bg-900 flex overflow-hidden">
        {/* Sidebar - Fixed height and independently scrollable */}
        <div className="w-64 bg-synrgy-surface border-r border-synrgy-primary/10 flex flex-col h-full overflow-y-auto flex-shrink-0">
          {/* Logo */}
          <div className="p-6">
            <div className="text-gradient text-xl font-heading font-bold">
              SYNRGY
            </div>
            <p className="text-xs text-synrgy-muted mt-1">SIEM Assistant</p>
          </div>
          
          {/* Navigation */}
          <nav className="flex-1 px-3">
            <ul className="space-y-1">
              {navigation.map((item) => {
                const isActive = location.pathname === item.href
                return (
                  <li key={item.name}>
                    <button
                      onClick={() => navigate(item.href)}
                      className={`w-full flex items-center px-3 py-2 text-sm rounded-lg transition-colors ${
                        isActive
                          ? 'bg-synrgy-primary/10 text-synrgy-primary border border-synrgy-primary/20'
                          : 'text-synrgy-muted hover:text-synrgy-text hover:bg-synrgy-primary/5'
                      }`}
                    >
                      <item.icon className="w-5 h-5 mr-3" />
                      {item.name}
                    </button>
                  </li>
                )
              })}
            </ul>
          </nav>
          
          {/* User info */}
          <div className="p-4 border-t border-synrgy-primary/10">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 bg-synrgy-primary/10 rounded-full flex items-center justify-center">
                <Shield className="w-4 h-4 text-synrgy-primary" />
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm font-medium text-synrgy-text truncate">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-synrgy-muted capitalize">
                  {user?.role}
                </p>
              </div>
            </div>
          </div>
        </div>
        
        {/* Main content - Scrollable independently */}
        <div className="flex-1 h-full overflow-hidden">
          {children}
        </div>
    </div>
  )
}
