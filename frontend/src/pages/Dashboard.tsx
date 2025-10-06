import { useEffect, useState } from 'react'
import { api } from '@/services/api'

export default function Dashboard() {
  const [health, setHealth] = useState<any | null>(null)
  const [ping, setPing] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    document.title = 'Dashboard · Kartavya SIEM Assistant'
    ;(async () => {
      try {
        const [h, p] = await Promise.all([
          api.get('/assistant/health'),
          api.get('/assistant/ping'),
        ])
        setHealth(h)
        setPing(p)
      } catch (e: any) {
        setError(e?.message || 'Failed to load dashboard')
      }
    })()
  }, [])

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <h3>System Status</h3>
      {error && <div style={{ color: 'crimson' }}>❌ {error}</div>}
      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
        <div style={{ padding: 12, border: '1px solid #eee', borderLeft: '4px solid #22c55e', minWidth: 240 }}>
          <div><strong>Assistant</strong></div>
          <div>Status: {health?.status || '—'}</div>
          <div>Initialized: {String(health?.is_initialized ?? '')}</div>
          <div>Health: {health?.health_score || '—'}</div>
        </div>
        <div style={{ padding: 12, border: '1px solid #eee', borderLeft: '4px solid #3b82f6', minWidth: 240 }}>
          <div><strong>Ping</strong></div>
          <div>{ping?.service || '—'}</div>
          <div>Version: {ping?.version || '—'}</div>
        </div>
      </div>

      <details>
        <summary>Components</summary>
        <pre style={{ overflow: 'auto' }}>{JSON.stringify(health?.components || {}, null, 2)}</pre>
      </details>
    </div>
  )
}
