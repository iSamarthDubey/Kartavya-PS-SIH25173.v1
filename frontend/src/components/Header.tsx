import { Link, useNavigate } from 'react-router-dom'
import { useAuth } from '@/hooks/useAuth'

export default function Header() {
  const { token, role, logout } = useAuth()
  const navigate = useNavigate()
  return (
    <header style={{ display: 'flex', alignItems: 'center', padding: '10px 16px' }}>
      <div style={{ fontWeight: 700 }}>
        <Link to={token ? '/chat' : '/login'} style={{ textDecoration: 'none', color: 'inherit' }}>
          🤖 Kartavya SIEM Assistant
        </Link>
      </div>
      <div style={{ marginLeft: 'auto', display: 'flex', gap: 12, alignItems: 'center' }}>
        {token ? (
          <>
            <span style={{ opacity: 0.8 }}>Role: {role || 'unknown'}</span>
            <button
              onClick={() => {
                logout()
                navigate('/login')
              }}
            >Logout</button>
          </>
        ) : (
          <Link to="/login">Login</Link>
        )}
      </div>
    </header>
  )
}
