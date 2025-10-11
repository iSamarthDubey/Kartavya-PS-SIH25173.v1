export default function ReportsPage() {
  return (
    <div className="h-full overflow-y-auto bg-synrgy-bg-900">
      <div className="max-w-6xl mx-auto p-6 space-y-6">
        <div className="mb-8">
          <h1 className="heading-lg text-synrgy-text mb-2">Reports</h1>
          <p className="text-synrgy-muted">Generate and manage security reports and analytics.</p>
        </div>
        
        <div className="bg-synrgy-surface border border-synrgy-primary/10 rounded-lg p-6">
          <div className="text-center py-12">
            <div className="w-16 h-16 mx-auto mb-6 bg-synrgy-primary/10 rounded-full flex items-center justify-center">
              <svg className="w-8 h-8 text-synrgy-primary" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M9 17v-2m3 2v-4m3 4v-6m2 10H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
            </div>
            <h3 className="heading-md mb-2">Reports Module</h3>
            <p className="text-synrgy-muted mb-6">Advanced reporting and analytics features are currently in development.</p>
            <button className="btn-primary" disabled>
              Coming Soon
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
