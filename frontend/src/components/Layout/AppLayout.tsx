import { ReactNode } from 'react'

interface AppLayoutProps {
  children: ReactNode
}

export default function AppLayout({ children }: AppLayoutProps) {
  return (
    <div className="min-h-screen bg-synrgy-bg-900">
      <div className="flex">
        {/* Sidebar placeholder */}
        <div className="w-64 bg-synrgy-surface border-r border-synrgy-primary/10 p-4">
          <div className="text-gradient text-xl font-heading font-bold mb-8">
            SYNRGY
          </div>
          <p className="text-synrgy-muted text-sm">Sidebar implementation coming soon...</p>
        </div>
        
        {/* Main content */}
        <div className="flex-1">
          {children}
        </div>
      </div>
    </div>
  )
}
