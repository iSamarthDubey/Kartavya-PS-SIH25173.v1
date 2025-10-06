import { useEffect, useState } from 'react'
import { api } from '@/services/api'

export default function Investigate() {
  const [busy, setBusy] = useState(false)
  const [resp, setResp] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    document.title = 'Investigate · Kartavya SIEM Assistant'
  }, [])

  async function runPreset(query: string, filters?: Record<string, any>) {
    setBusy(true)
    setError(null)
    setResp(null)
    try {
      const payload: any = { query, conversation_id: `conv_${Date.now()}` }
      if (filters) payload.filters = filters
      const r = await api.post('/assistant/ask', payload)
      setResp(r)
    } catch (e: any) {
      setError(e?.message || 'Failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div style={{ display: 'grid', gap: 8 }}>
        <h3>Quick Investigations</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          <button disabled={busy} onClick={() => runPreset('Show failed login attempts', { time_window_gte: 'now-1d' })}>Failed Logins (24h)</button>
          <button disabled={busy} onClick={() => runPreset('Show security alerts', { time_window_gte: 'now-1d', severity: 'High' })}>High Severity Alerts (24h)</button>
          <button disabled={busy} onClick={() => runPreset('Show network activity', { time_window_gte: 'now-1d', index_class: 'network' })}>Network Activity (24h)</button>
        </div>
      </div>

      {error && <div style={{ color: 'crimson' }}>❌ {error}</div>}

      {resp && (
        <div style={{ display: 'grid', gap: 8 }}>
          <div style={{ padding: 12, border: '1px solid #eee', background: '#fafafa' }}>
            <strong>Summary:</strong>
            <div>{resp.answer || resp.summary || 'Query processed.'}</div>
          </div>
          <details>
            <summary>Show Generated DSL</summary>
            <pre style={{ overflow: 'auto' }}>{JSON.stringify(resp.siem_query || {}, null, 2)}</pre>
          </details>
          {Array.isArray(resp.data || resp.results) && (resp.data || resp.results).length > 0 ? (
            <pre style={{ maxHeight: 400, overflow: 'auto', border: '1px solid #eee', padding: 8 }}>{JSON.stringify((resp.data || resp.results).slice(0, 50), null, 2)}</pre>
          ) : (
            <div>No results</div>
          )}
        </div>
      )}
    </div>
  )
}
