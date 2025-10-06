const rawBase = import.meta.env.VITE_API_BASE?.toString() || ''
const normalized = rawBase.replace(/\/$/, '')

export const api = {
  base: normalized,
  async request(path: string, init: RequestInit = {}) {
    const token = sessionStorage.getItem('access_token')
    const headers = new Headers(init.headers || {})
    if (token) headers.set('Authorization', `Bearer ${token}`)
    if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

    const url = `${this.base}${path}`
    const res = await fetch(url, { ...init, headers })

    if (!res.ok) {
      let detail = `${res.status} ${res.statusText}`
      try {
        const j = await res.json()
        detail = j.detail || detail
      } catch {}
      throw new Error(detail)
    }

    const ct = res.headers.get('content-type') || ''
    return ct.includes('application/json') ? res.json() : res.text()
  },
  get(path: string) {
    return this.request(path)
  },
  post(path: string, body: any) {
    return this.request(path, { method: 'POST', body: JSON.stringify(body) })
  },
}
