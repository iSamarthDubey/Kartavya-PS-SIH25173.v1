import { useEffect, useMemo, useRef, useState } from 'react'
import { api } from '@/services/api'
import { useAuth } from '@/hooks/useAuth'

function ResultsTable({ rows }: { rows: any[] }) {
  if (!rows || rows.length === 0) return null
  // Collect a modest set of columns from first N rows
  const columns = useMemo(() => {
    const cols = new Set<string>()
    for (const r of rows.slice(0, 20)) {
      Object.keys(r || {}).forEach(k => cols.add(k))
    }
    // Prefer common SIEM-ish fields first
    const preferred = ['@timestamp', 'user.name', 'source.ip', 'destination.ip', 'event.severity', 'message']
    const rest = Array.from(cols).filter(c => !preferred.includes(c))
    return [...preferred.filter(c => cols.has(c)), ...rest].slice(0, 12) // cap columns
  }, [rows])

  return (
    <div style={{ overflow: 'auto', border: '1px solid #eee' }}>
      <table style={{ borderCollapse: 'collapse', width: '100%', fontSize: 13 }}>
        <thead>
          <tr>
            {columns.map(c => (
              <th key={c} style={{ textAlign: 'left', padding: 6, borderBottom: '1px solid #eee', background: '#fafafa' }}>{c}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.slice(0, 100).map((r, i) => (
            <tr key={i}>
              {columns.map(c => (
                <td key={c} style={{ padding: 6, borderBottom: '1px solid #f2f2f2', verticalAlign: 'top' }}>
                  {String((r && r[c]) ?? '')}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}

export default function Chat() {
  const { token } = useAuth()
  const [query, setQuery] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [answer, setAnswer] = useState<string>('')
  const [results, setResults] = useState<any[]>([])
  const [dsl, setDsl] = useState<any | null>(null)
  const [meta, setMeta] = useState<any | null>(null)
  const [chartB64, setChartB64] = useState<string | null>(null)
  const convRef = useRef(`conv_${Date.now()}`)

  useEffect(() => {
    document.title = 'Chat · Kartavya SIEM Assistant'
  }, [])

  async function runQuery(forceIntent?: string) {
    if (!query.trim()) return
    setBusy(true)
    setError(null)
    try {
      const payload: any = { query: query.trim(), conversation_id: convRef.current }
      if (forceIntent) payload.force_intent = forceIntent
      const res = await api.post('/assistant/ask', payload)
      // Map both assistant and backend styles just in case
      const a = res.answer || res.summary || 'Query processed.'
      const data = res.data || res.results || []
      const viz = res.visualizations || []
      const meta = res.metadata || {}
      setAnswer(a)
      setResults(Array.isArray(data) ? data : [])
      setDsl(res.siem_query || null)
      setMeta(meta)
      // If backend delivered base64 chart(s) in visualizations, prefer first image-like
      const firstB64 = (viz.find((v: any) => typeof v === 'string') as string) || null
      setChartB64(firstB64)
    } catch (e: any) {
      setError(e?.message || 'Query failed')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', display: 'grid', gap: 12 }}>
      <div style={{ display: 'flex', gap: 8 }}>
        <input
          value={query}
          onChange={e => setQuery(e.target.value)}
          placeholder="Ask anything (e.g., Show failed logins last 24 hours)"
          style={{ flex: 1, padding: '10px 12px' }}
          onKeyDown={e => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              runQuery()
            }
          }}
        />
        <button onClick={() => runQuery()} disabled={busy || !token}>{busy ? 'Running…' : 'Run'}</button>
      </div>

      {error && <div style={{ color: 'crimson' }}>❌ {error}</div>}

      {answer && (
        <div style={{ padding: 12, border: '1px solid #eee', borderLeft: '4px solid #667eea', background: '#fafafa' }}>
          <strong>Answer:</strong>
          <div style={{ marginTop: 8 }}>{answer}</div>
        </div>
      )}

      {meta && (
        <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap' }}>
          {meta.intent && <span style={{ background: '#e3f2fd', color: '#1976d2', padding: '4px 8px', borderRadius: 12 }}>Intent: {meta.intent}</span>}
          {typeof meta.confidence_score === 'number' && (
            <span style={{ background: '#e8f5e9', color: '#388e3c', padding: '4px 8px', borderRadius: 12 }}>Confidence: {Math.round(meta.confidence_score * 100)}%</span>
          )}
          {typeof meta.results_count === 'number' && (
            <span style={{ background: '#fff3e0', color: '#f57c00', padding: '4px 8px', borderRadius: 12 }}>Results: {meta.results_count}</span>
          )}
        </div>
      )}

      {dsl && (
        <details>
          <summary>Show Generated DSL</summary>
          <pre style={{ overflow: 'auto', background: '#0f172a', color: '#e2e8f0', padding: 12, borderRadius: 6 }}>
            {JSON.stringify(dsl, null, 2)}
          </pre>
        </details>
      )}

      {chartB64 && (
        <div>
          <img alt="chart" src={`data:image/png;base64,${chartB64}`} style={{ maxWidth: '100%', border: '1px solid #eee' }} />
        </div>
      )}

      <ResultsTable rows={results} />
    </div>
  )
}
