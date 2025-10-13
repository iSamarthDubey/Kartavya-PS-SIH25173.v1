import React, { memo, useMemo, useCallback } from 'react'
import { Users, Settings, Shield } from 'lucide-react'

// Memoized admin card component for better performance
const AdminCard = memo(function AdminCard({
  icon: Icon,
  title,
  description,
  onClick,
  disabled = false,
}: {
  icon: React.ComponentType<{ className?: string }>
  title: string
  description: string
  onClick?: () => void
  disabled?: boolean
}) {
  return (
    <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
      <div className="flex items-center gap-3 mb-4">
        <div className="w-10 h-10 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
          <Icon className="w-5 h-5 text-synrgy-primary" />
        </div>
        <h3 className="heading-sm">{title}</h3>
      </div>
      <p className="text-sm text-synrgy-muted mb-4">{description}</p>
      <button
        className="btn-primary w-full"
        onClick={onClick}
        disabled={disabled}
      >
        {disabled ? 'Coming Soon' : 'Manage'}
      </button>
    </div>
  )
})

const AdminPage = memo(function AdminPage() {
  // Memoize admin sections to prevent unnecessary re-renders
  const adminSections = useMemo(
    () => [
      {
        id: 'users',
        icon: Users,
        title: 'User Management',
        description: 'Manage user accounts, roles, and permissions.',
        disabled: true,
      },
      {
        id: 'system',
        icon: Settings,
        title: 'System Settings',
        description: 'Configure system parameters and preferences.',
        disabled: true,
      },
      {
        id: 'security',
        icon: Shield,
        title: 'Security Policies',
        description: 'Manage security rules and compliance settings.',
        disabled: true,
      },
    ],
    []
  )

  // Memoize click handlers to prevent unnecessary re-renders
  const handleSectionClick = useCallback((sectionId: string) => {
    console.log(`Clicked section: ${sectionId}`)
    // Future: Navigate to specific admin section
  }, [])

  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div className="mb-8">
          <h1 className="heading-lg text-synrgy-text mb-2">Administration</h1>
          <p className="text-synrgy-muted">
            Manage system settings, users, and security configurations.
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {adminSections.map((section) => (
            <AdminCard
              key={section.id}
              icon={section.icon}
              title={section.title}
              description={section.description}
              onClick={() => handleSectionClick(section.id)}
              disabled={section.disabled}
            />
          ))}
        </div>
      </div>
    </div>
  )
})

export default AdminPage
