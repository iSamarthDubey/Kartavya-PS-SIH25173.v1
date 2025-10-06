const STORAGE_KEY = 'siem-assistant:last-backend-base'

const normalizeBase = (input?: string | null) => {
  if (!input) return ''
  try {
    const url = new URL(input, window.location.origin)
    url.hash = ''
    return url.origin
  } catch {
    return ''
  }
}

const readStoredBase = () => {
  if (typeof window === 'undefined') return ''
  try {
    return window.sessionStorage.getItem(STORAGE_KEY) || window.localStorage.getItem(STORAGE_KEY) || ''
  } catch {
    return ''
  }
}

const rememberBase = (base: string) => {
  if (typeof window === 'undefined') return
  if (!base) {
    try {
      window.sessionStorage.removeItem(STORAGE_KEY)
      window.localStorage.removeItem(STORAGE_KEY)
    } catch {}
    return
  }
  try {
    window.sessionStorage.setItem(STORAGE_KEY, base)
  } catch {}
  try {
    window.localStorage.setItem(STORAGE_KEY, base)
  } catch {}
}

const addPortCandidates = (set: Set<string>, value?: string | null) => {
  if (!value) return
  const numeric = Number(value)
  if (!Number.isFinite(numeric) || numeric <= 0) return
  for (const host of ['localhost', '127.0.0.1']) {
    set.add(`http://${host}:${numeric}`)
  }
}

const gatherCandidates = () => {
  if (typeof window === 'undefined') return []

  const hints = new Set<string>()

  // 1. Explicit environment overrides
  const envBase = normalizeBase(import.meta.env.VITE_API_BASE)
  if (envBase) hints.add(envBase)

  // 2. Previously discovered base
  const stored = normalizeBase(readStoredBase())
  if (stored) hints.add(stored)

  // 3. Global configuration objects (launcher can inject)
  const globalCfg = (window as any).__APP_CONFIG__
  const globalBase = normalizeBase(globalCfg?.apiBase || (window as any).__ASSISTANT_API_BASE__)
  if (globalBase) hints.add(globalBase)

  // 4. Query-string overrides (?backend=...)
  const url = new URL(window.location.href)
  const queryKeys = ['backend', 'apiBase', 'api_base', 'backendUrl']
  for (const key of queryKeys) {
    const candidate = normalizeBase(url.searchParams.get(key))
    if (candidate) hints.add(candidate)
  }

  // 5. Query-string ports (?backendPort=8002)
  addPortCandidates(hints, url.searchParams.get('backendPort'))
  addPortCandidates(hints, url.searchParams.get('port'))

  // 6. Environment-supplied port hints
  addPortCandidates(hints, import.meta.env.VITE_API_PORT)
  addPortCandidates(hints, import.meta.env.VITE_BACKEND_PORT)
  addPortCandidates(hints, import.meta.env.SIEM_BACKEND_PORT)
  addPortCandidates(hints, import.meta.env.ASSISTANT_PORT)

  // 7. Current window origin + common fallbacks
  hints.add(normalizeBase(window.location.origin))
  for (const port of [8001, 8002, 8003, 8004, 8005]) {
    addPortCandidates(hints, String(port))
  }

  return Array.from(hints).filter(Boolean)
}

const probeCandidate = async (base: string) => {
  try {
    const res = await fetch(`${base}/assistant/ping`, { method: 'GET', credentials: 'omit' })
    if (res.ok) {
      rememberBase(base)
      return base
    }
  } catch {
    /* ignore */
  }
  return ''
}

let resolving: Promise<string> | null = null
let cachedBase = normalizeBase(import.meta.env.VITE_API_BASE) || ''

const resolveBase = async (): Promise<string> => {
  if (cachedBase) return cachedBase

  if (resolving) {
    return resolving
  }

  resolving = (async () => {
    const candidates = gatherCandidates()
    for (const candidate of candidates) {
      const hit = await probeCandidate(candidate)
      if (hit) {
        cachedBase = hit
        resolving = null
        return hit
      }
    }

    resolving = null
    return ''
  })()

  return resolving
}

type RequestOptions = RequestInit & { parseJson?: boolean }

const request = async <T = unknown>(path: string, options: RequestOptions = {}) => {
  const base = (await resolveBase()) || normalizeBase(import.meta.env.VITE_API_BASE) || 'http://localhost:8001'
  const url = `${base}${path.startsWith('/') ? path : `/${path}`}`

  const headers = new Headers(options.headers || {})
  if (!headers.has('Content-Type')) {
    headers.set('Content-Type', 'application/json')
  }

  const res = await fetch(url, { ...options, headers })
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const body = await res.json()
      detail = body.detail || detail
    } catch {
      // noop
    }
    throw new Error(detail)
  }

  const contentType = res.headers.get('content-type') || ''
  const shouldParseJson = options.parseJson ?? contentType.includes('application/json')
  return (shouldParseJson ? res.json() : res.text()) as Promise<T>
}

export const api = {
  get base() {
    return cachedBase
  },
  resolveBase,
  request,
  get: <T = unknown>(path: string) => request<T>(path),
  post: <T = unknown, B = unknown>(path: string, body: B) =>
    request<T>(path, { method: 'POST', body: JSON.stringify(body) }),
}

export default api
