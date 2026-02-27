const API_BASE = import.meta.env.VITE_API_BASE_URL ?? ''
export const TOKEN_KEY = 'witrix_token'
export const USER_CACHE_KEY = 'witrix_user_cache'
const CACHE_EXPIRY_DAYS = 7

interface CachedUserMe extends UserMe {
  expires_at: number
}

export function getCachedUserMe(): UserMe | null {
  try {
    const raw = localStorage.getItem(USER_CACHE_KEY)
    if (!raw) return null
    const data = JSON.parse(raw) as CachedUserMe
    if (data.expires_at && Date.now() > data.expires_at) {
      localStorage.removeItem(USER_CACHE_KEY)
      return null
    }
    return {
      username: data.username ?? '',
      auth_type: data.auth_type ?? 'admin',
      avatar_url: data.avatar_url ?? null,
      is_discord_user: !!data.is_discord_user,
      allowed_guild_ids: Array.isArray(data.allowed_guild_ids) ? data.allowed_guild_ids : [],
      admin_guild_ids: Array.isArray(data.admin_guild_ids) ? data.admin_guild_ids : [],
      default_guild_id: data.default_guild_id ?? null,
    }
  } catch {
    return null
  }
}

export function setCachedUserMe(me: UserMe): void {
  try {
    const cached: CachedUserMe = {
      ...me,
      expires_at: Date.now() + CACHE_EXPIRY_DAYS * 24 * 60 * 60 * 1000,
    }
    localStorage.setItem(USER_CACHE_KEY, JSON.stringify(cached))
  } catch {
    // ignore
  }
}

export function clearCachedUserMe(): void {
  try {
    localStorage.removeItem(USER_CACHE_KEY)
  } catch {
    // ignore
  }
}

export interface LoginRequest {
  username: string
  password: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
}

export interface UserMe {
  username: string
  auth_type: string
  avatar_url?: string | null
  is_discord_user: boolean
  allowed_guild_ids: string[]
  admin_guild_ids: string[]
  default_guild_id: string | null
}

export async function login(body: LoginRequest): Promise<TokenResponse> {
  const res = await fetch(`${API_BASE}/api/auth/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
    credentials: 'include',
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const msg = typeof data.detail === 'string' ? data.detail : data.detail?.[0]?.msg ?? data.detail?.msg
    throw new Error(msg ?? `Ошибка входа: ${res.status}`)
  }
  return res.json()
}

export async function getMe(token: string): Promise<UserMe> {
  const res = await fetch(`${API_BASE}/api/auth/me`, {
    headers: { Authorization: `Bearer ${token}` },
    credentials: 'include',
  })
  if (res.status === 401) {
    localStorage.removeItem(TOKEN_KEY)
    clearCachedUserMe()
    window.location.href = '/login'
    throw new Error('Сессия истекла')
  }
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const msg = typeof data.detail === 'string' ? data.detail : data.detail?.[0]?.msg ?? data.detail?.msg
    throw new Error(msg ?? `Ошибка проверки авторизации: ${res.status}`)
  }
  const data = await res.json()
  return {
    username: data.username,
    auth_type: data.auth_type ?? 'admin',
    avatar_url: data.avatar_url ?? null,
    is_discord_user: !!data.is_discord_user,
    allowed_guild_ids: Array.isArray(data.allowed_guild_ids) ? data.allowed_guild_ids : [],
    admin_guild_ids: Array.isArray(data.admin_guild_ids) ? data.admin_guild_ids : [],
    default_guild_id: data.default_guild_id ?? null,
  }
}

/** URL для редиректа на вход через Discord (бэкенд). */
export function getDiscordLoginUrl(): string {
  return `${API_BASE}/api/auth/discord`
}

export async function setDefaultGuild(token: string, guildId: string | null): Promise<UserMe> {
  const res = await fetch(`${API_BASE}/api/auth/me/default-guild`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      Authorization: `Bearer ${token}`,
    },
    credentials: 'include',
    body: JSON.stringify({ guild_id: guildId }),
  })
  if (!res.ok) {
    const data = await res.json().catch(() => ({}))
    const msg = typeof data.detail === 'string' ? data.detail : data.detail?.msg
    throw new Error(msg ?? `Ошибка: ${res.status}`)
  }
  const data = await res.json()
  return {
    username: data.username,
    auth_type: data.auth_type ?? 'admin',
    avatar_url: data.avatar_url ?? null,
    is_discord_user: !!data.is_discord_user,
    allowed_guild_ids: Array.isArray(data.allowed_guild_ids) ? data.allowed_guild_ids : [],
    admin_guild_ids: Array.isArray(data.admin_guild_ids) ? data.admin_guild_ids : [],
    default_guild_id: data.default_guild_id ?? null,
  }
}
