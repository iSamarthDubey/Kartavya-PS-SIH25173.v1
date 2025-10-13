export default function InvestigationsPage() {
  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div className="mb-8">
          <h1 className="heading-lg text-synrgy-text mb-2">Investigations</h1>
          <p className="text-synrgy-muted">
            Manage and track security incidents and investigations.
          </p>
        </div>

        <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-6 bg-synrgy-primary/10 rounded-full flex items-center justify-center">
              <svg
                className="w-8 h-8 text-synrgy-primary"
                fill="none"
                stroke="currentColor"
                viewBox="0 0 24 24"
              >
                <path
                  strokeLinecap="round"
                  strokeLinejoin="round"
                  strokeWidth={1.5}
                  d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
                />
              </svg>
            </div>
            <h3 className="heading-md mb-2">Investigation Tools</h3>
            <p className="text-synrgy-muted mb-6">
              Advanced investigation and forensics capabilities are being developed.
            </p>
            <button className="btn-primary" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
