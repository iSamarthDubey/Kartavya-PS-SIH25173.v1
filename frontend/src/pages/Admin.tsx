export default function AdminPage() {
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
          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-synrgy-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197m13.5-9a2.25 2.25 0 11-4.5 0 2.25 2.25 0 014.5 0z"
                  />
                </svg>
              </div>
              <h3 className="heading-sm">User Management</h3>
            </div>
            <p className="text-sm text-synrgy-muted mb-4">
              Manage user accounts, roles, and permissions.
            </p>
            <button className="btn-primary w-full" disabled>
              Coming Soon
            </button>
          </div>

          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-synrgy-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z"
                  />
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"
                  />
                </svg>
              </div>
              <h3 className="heading-sm">System Settings</h3>
            </div>
            <p className="text-sm text-synrgy-muted mb-4">
              Configure system parameters and preferences.
            </p>
            <button className="btn-primary w-full" disabled>
              Coming Soon
            </button>
          </div>

          <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
            <div className="flex items-center gap-3 mb-4">
              <div className="w-10 h-10 bg-synrgy-primary/10 rounded-lg flex items-center justify-center">
                <svg
                  className="w-5 h-5 text-synrgy-primary"
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path
                    strokeLinecap="round"
                    strokeLinejoin="round"
                    strokeWidth={1.5}
                    d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
                  />
                </svg>
              </div>
              <h3 className="heading-sm">Security Policies</h3>
            </div>
            <p className="text-sm text-synrgy-muted mb-4">
              Manage security rules and compliance settings.
            </p>
            <button className="btn-primary w-full" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
