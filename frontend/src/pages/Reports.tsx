import { useEffect, useState } from 'react'
import { api } from '@/services/api'

function Download({ data, name, type }: { data: string; name: string; type: string }) {
  return (
    <a
      href={`data:${type};charset=utf-8,${encodeURIComponent(data)}`}
      download={name}
      style={{ textDecoration: 'none' }}
    >
      <button>Download</button>
    </a>
  )
}

export default function Reports() {
  const [busy, setBusy] = useState(false)
  const [resp, setResp] = useState<any | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    document.title = 'Reports · Kartavya SIEM Assistant'
  }, [])

  async function runReport(title: string, query: string, filters?: Record<string, any>, limit = 200) {
    setBusy(true)
    setError(null)
    setResp(null)
    try {
      const payload: any = { query, conversation_id: `conv_${Date.now()}`, limit }
      if (filters) payload.filters = filters
      const r = await api.post('/assistant/ask', payload)
      setResp({ title, ...r })
    } catch (e: any) {
      setError(e?.message || 'Failed')
    } finally {
      setBusy(false)
    }
  }

  const csv = (() => {
    const rows = (resp?.data || resp?.results || []) as any[]
    if (!rows || rows.length === 0) return ''
    const cols = Array.from(new Set(rows.flatMap(r => Object.keys(r || {}))))
    const head = cols.join(',')
    const body = rows
      .slice(0, 1000)
      .map(r => cols.map(c => JSON.stringify((r && r[c]) ?? '')).join(','))
      .join('\n')
    return [head, body].join('\n')
  })()

  const jsonStr = JSON.stringify(resp?.data || resp?.results || [], null, 2)

  return (
    <div style={{ display: 'grid', gap: 16 }}>
      <div>
        <h3>One-click Reports</h3>
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 8 }}>
          <button disabled={busy} onClick={() => runReport('Failed Logins Report (24h)', 'Show failed login attempts', { time_window_gte: 'now-1d' })}>Failed Logins (24h)</button>
          <button disabled={busy} onClick={() => runReport('High Severity Alerts (24h)', 'Show security alerts', { time_window_gte: 'now-1d', severity: 'High' })}>High Severity Alerts (24h)</button>
          <button disabled={busy} onClick={() => runReport('Network Activity Summary (24h)', 'Show network activity', { time_window_gte: 'now-1d', index_class: 'network' })}>Network Activity (24h)</button>
        </div>
      </div>

      {error && <div style={{ color: 'crimson' }}>❌ {error}</div>}

      {resp && (
        <div style={{ display: 'grid', gap: 8 }}>
          <div style={{ padding: 12, border: '1px solid #eee', background: '#fafafa' }}>
            <strong>{resp.title}</strong>
            <div style={{ marginTop: 6 }}>{resp.answer || resp.summary || 'Report generated.'}</div>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            {csv && <Download data={csv} name={`report_${Date.now()}.csv`} type="text/csv" />}
            {jsonStr && <Download data={jsonStr} name={`report_${Date.now()}.json`} type="application/json" />}
          </div>
          <details>
            <summary>Show Generated DSL</summary>
            <pre style={{ overflow: 'auto' }}>{JSON.stringify(resp.siem_query || {}, null, 2)}</pre>
          </details>
          <pre style={{ maxHeight: 400, overflow: 'auto', border: '1px solid #eee', padding: 8 }}>{jsonStr}</pre>
        </div>
      )}
    </div>
  )
}
