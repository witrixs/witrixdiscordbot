import { TOKEN_KEY } from './auth'

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''

function getToken(): string | null {
  return localStorage.getItem(TOKEN_KEY)
}

export async function apiFetch(path: string, options: RequestInit = {}): Promise<Response> {
  const token = getToken()
  const headers: HeadersInit = {
    ...options.headers,
  }
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`
  }
  const res = await fetch(`${API_BASE}${path}`, { ...options, credentials: 'include', headers })
  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY)
    window.location.href = '/login'
    throw new Error('Сессия истекла')
  }
  return res
}

export async function apiJson<T>(path: string, options: RequestInit = {}): Promise<T> {
  const res = await apiFetch(path, options)
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    throw new Error((data as { detail?: string }).detail ?? `Request failed: ${res.status}`)
  }
  return res.json()
}
