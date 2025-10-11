import { useNavigate } from 'react-router-dom'
import DashboardMain from '@/components/Dashboard/DashboardMain'
import { useAppStore } from '@/stores/appStore'

export default function DashboardPage() {
  const navigate = useNavigate()
  const { setMode, setChatPanelOpen } = useAppStore()
  
  const handleAskSynrgy = (query: string) => {
    // Switch to hybrid mode and open chat with the query
    setMode('hybrid')
    setChatPanelOpen(true)
    navigate('/hybrid', { state: { query } })
  }

  return (
    <div className="h-full overflow-y-auto">
      <DashboardMain onAskSynrgy={handleAskSynrgy} />
    </div>
  )
}
