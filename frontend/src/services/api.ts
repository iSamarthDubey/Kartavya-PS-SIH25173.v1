/// <reference types="vite/client" />
const rawBase = import.meta.env.VITE_API_BASE?.toString() || ''

const STORAGE_KEY = 'siem_api_base'

let cachedBase = normalizeBase(rawBase)
let resolvingBase: Promise<string> | null = null

function normalizeBase(value?: string | null): string {
  if (!value) return ''
  const trimmed = value.trim()
  if (!trimmed) return ''
  try {
    const candidate = trimmed.match(/^https?:\/\//i) ? trimmed : `http://${trimmed}`
    const url = new URL(candidate)
    return url.origin.replace(/\/$/, '')
  } catch {
    return ''
  }
}

function rememberBase(base: string) {
  cachedBase = base
  if (typeof window === 'undefined') return
  if (!base) {
    try {
      window.sessionStorage.removeItem(STORAGE_KEY)
    } catch {}
    try {
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

function readStoredBase(): string {
  if (typeof window === 'undefined') return ''
  try {
    const fromSession = window.sessionStorage.getItem(STORAGE_KEY)
    if (fromSession) return normalizeBase(fromSession)
  } catch {}
  try {
    const fromLocal = window.localStorage.getItem(STORAGE_KEY)
    if (fromLocal) return normalizeBase(fromLocal)
  } catch {}
  return ''
}

async function probeOrigin(origin: string): Promise<boolean> {
  const controller = typeof AbortController !== 'undefined' ? new AbortController() : undefined
  const timeoutId = controller ? setTimeout(() => controller.abort(), 2500) : null
  try {
    const res = await fetch(`${origin}/assistant/ping`, {
      method: 'GET',
      headers: { Accept: 'application/json' },
      signal: controller?.signal,
    })
    return res.ok
  } catch {
    return false
  } finally {
    if (timeoutId) clearTimeout(timeoutId)
  }
}

function gatherCandidates(): string[] {
  if (typeof window === 'undefined') return []

  const hints = new Set<string>()

  const stored = readStoredBase()
  if (stored) hints.add(stored)

  const globalCfg = (window as any).__APP_CONFIG__
  const globalBase = normalizeBase(globalCfg?.apiBase || (window as any).__ASSISTANT_API_BASE__)
  if (globalBase) hints.add(globalBase)

  const url = new URL(window.location.href)
  const queryHint = normalizeBase(
    url.searchParams.get('backend') ||
      url.searchParams.get('apiBase') ||
      url.searchParams.get('api_base') ||
      url.searchParams.get('backendUrl')
  )
  if (queryHint) hints.add(queryHint)

  function addPortCandidates(portValue: string | null | undefined) {
    if (!portValue) return
    const numeric = Number(portValue)
    if (!Number.isFinite(numeric) || numeric <= 0) return
    for (const host of ['localhost', '127.0.0.1']) {
      hints.add(`http://${host}:${numeric}`)
    }
  }

  addPortCandidates(url.searchParams.get('backendPort'))
  addPortCandidates(url.searchParams.get('port'))

  const origin = normalizeBase(window.location.origin)
  if (origin) hints.add(origin)

  const envPortValues = [
    import.meta.env.VITE_API_PORT,
    import.meta.env.VITE_BACKEND_PORT,
    import.meta.env.SIEM_BACKEND_PORT,
    import.meta.env.ASSISTANT_PORT,
  ]
  envPortValues.forEach((value) => addPortCandidates(value))

  const numericPorts = [8001, 8002, 8003, 8004, 8005]
  for (const port of numericPorts) {
    addPortCandidates(String(port))
  }

  return Array.from(hints)
}

async function resolveBase(): Promise<string> {
  if (cachedBase) return cachedBase
  if (resolvingBase) return resolvingBase

  resolvingBase = (async () => {
    if (rawBase) {
      const normalized = normalizeBase(rawBase)
      if (normalized) {
        rememberBase(normalized)
        return normalized
      }
    }

    const stored = readStoredBase()
    if (stored) {
      rememberBase(stored)
      return stored
    }

    const candidates = gatherCandidates()
    for (const candidate of candidates) {
      const normalized = normalizeBase(candidate)
      if (!normalized) continue
      if (await probeOrigin(normalized)) {
        rememberBase(normalized)
        return normalized
      }
    }

    rememberBase('')
    return ''
  })()

  try {
    return await resolvingBase
  } finally {
    resolvingBase = null
  }
}

export const api = {
  get base() {
    return cachedBase
  },
  async resolveBase() {
    return resolveBase()
  },
  clearCachedBase() {
    cachedBase = ''
    if (typeof window !== 'undefined') {
      try {
        window.sessionStorage.removeItem(STORAGE_KEY)
      } catch {}
      try {
        window.localStorage.removeItem(STORAGE_KEY)
      } catch {}
    }
  },
  async request(path: string, init: RequestInit = {}) {
    const token = typeof window !== 'undefined' ? window.sessionStorage.getItem('access_token') : null
    const headers = new Headers(init.headers || {})
    if (token) headers.set('Authorization', `Bearer ${token}`)
    if (!headers.has('Content-Type')) headers.set('Content-Type', 'application/json')

    const isAbsolute = /^https?:\/\//i.test(path)
    const normalizedPath = path.startsWith('/') ? path : `/${path}`
    const base = isAbsolute ? '' : await resolveBase()
    const url = isAbsolute ? path : base ? `${base}${normalizedPath}` : normalizedPath
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
