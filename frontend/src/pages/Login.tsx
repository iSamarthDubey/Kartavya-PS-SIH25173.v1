import { useState } from 'react'
import { useAuth } from '@/hooks/useAuth'

export default function Login() {
  const { login } = useAuth()
  const [username, setUsername] = useState('admin')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  async function handleLogin(e: React.FormEvent) {
    e.preventDefault()
    setLoading(true)
    setError(null)
    try {
      await login(username, password)
    } catch (err: any) {
      setError(err?.message || 'Login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div style={{ maxWidth: 400, margin: '40px auto' }}>
      <h2>Sign in</h2>
      <form onSubmit={handleLogin}>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
          <label>
            Username
            <input value={username} onChange={e => setUsername(e.target.value)} required style={{ width: '100%' }} />
          </label>
          <label>
            Password
            <input type="password" value={password} onChange={e => setPassword(e.target.value)} required style={{ width: '100%' }} />
          </label>
          <button type="submit" disabled={loading}>{loading ? 'Signing in…' : 'Sign in'}</button>
        </div>
      </form>
      {error && <p style={{ color: 'crimson' }}>{error}</p>}
      <p style={{ opacity: 0.8, marginTop: 12 }}>You need valid credentials for the Assistant API.</p>
    </div>
  )
}
