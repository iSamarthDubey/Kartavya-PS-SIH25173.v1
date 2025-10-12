import VisualRendererTest from '../components/debug/VisualRendererTest'

export default function DebugPage() {
  return (
    <div className="container mx-auto p-4">
      <div className="mb-6 border-b border-gray-700 pb-4">
        <h1 className="text-2xl font-bold text-synrgy-primary">Debugging Page</h1>
        <p className="text-synrgy-muted">Testing environment for individual components</p>
      </div>
      
      <div className="bg-synrgy-surface p-6 rounded-lg">
        <VisualRendererTest />
      </div>
    </div>
  )
}