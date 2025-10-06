import { Routes, Route, Navigate, Link, useLocation } from 'react-router-dom'
import { useEffect } from 'react'
import Login from '@/pages/Login'
import Chat from '@/pages/Chat'
import Investigate from '@/pages/Investigate'
import Reports from '@/pages/Reports'
import Dashboard from '@/pages/Dashboard'
import Header from '@/components/Header'
import { useAuth } from '@/hooks/useAuth'

function RequireAuth({ children }: { children: JSX.Element }) {
  const { token } = useAuth()
  const location = useLocation()
  if (!token) {
    return <Navigate to="/login" state={{ from: location }} replace />
  }
  return children
}

export default function App() {
  const { token, apiBase } = useAuth()
  useEffect(() => {
    document.title = 'Kartavya SIEM Assistant'
  }, [])

  return (
    <div style={{ fontFamily: 'Inter, system-ui, Arial, sans-serif' }}>
      <Header />
      <nav style={{ display: 'flex', gap: 12, padding: '8px 16px', borderBottom: '1px solid #eee' }}>
        <Link to="/chat">💬 Chat</Link>
        <Link to="/investigate">🧭 Investigate</Link>
        <Link to="/reports">📑 Reports</Link>
        <Link to="/dashboard">📊 Dashboard</Link>
        <span style={{ marginLeft: 'auto', opacity: 0.7 }}>API: {apiBase}</span>
      </nav>
      <div style={{ padding: 16 }}>
        <Routes>
          <Route path="/login" element={<Login />} />
          <Route path="/chat" element={<RequireAuth><Chat /></RequireAuth>} />
          <Route path="/investigate" element={<RequireAuth><Investigate /></RequireAuth>} />
          <Route path="/reports" element={<RequireAuth><Reports /></RequireAuth>} />
          <Route path="/dashboard" element={<RequireAuth><Dashboard /></RequireAuth>} />
          <Route path="/" element={<Navigate to={token ? '/chat' : '/login'} replace />} />
          <Route path="*" element={<div>Not found</div>} />
        </Routes>
      </div>
    </div>
  )
}
