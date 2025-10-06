import { createContext, useContext, useMemo, useState } from 'react'
import { api } from '@/services/api'

type AuthCtx = {
  token: string | null
  role: string | null
  login: (u: string, p: string) => Promise<void>
  logout: () => void
  apiBase: string
}

const Ctx = createContext<AuthCtx | null>(null)

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(sessionStorage.getItem('access_token'))
  const [role, setRole] = useState<string | null>(sessionStorage.getItem('role'))

  async function login(username: string, password: string) {
    const res = await api.post('/assistant/auth/login', { username, password })
    sessionStorage.setItem('access_token', res.access_token)
    sessionStorage.setItem('role', res.role || '')
    setToken(res.access_token)
    setRole(res.role || null)
  }

  function logout() {
    sessionStorage.removeItem('access_token')
    sessionStorage.removeItem('role')
    setToken(null)
    setRole(null)
  }

  const value = useMemo(() => ({ token, role, login, logout, apiBase: api.base }), [token, role])

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>
}

export const useAuthCtx = () => {
  const ctx = useContext(Ctx)
  if (!ctx) throw new Error('useAuthCtx must be used within AuthProvider')
  return ctx
}
