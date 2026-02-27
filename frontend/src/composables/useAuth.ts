import type { UserMe } from '@/api/auth'
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import * as authApi from '@/api/auth'
import { TOKEN_KEY, getCachedUserMe, setCachedUserMe, clearCachedUserMe } from '@/api/auth'

function initFromCache(): { username: string | null; userMe: UserMe | null } {
  const cached = getCachedUserMe()
  if (!cached) return { username: null, userMe: null }
  return { username: cached.username, userMe: cached }
}

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))
const cached = token.value ? initFromCache() : { username: null as string | null, userMe: null as UserMe | null }
const username = ref<string | null>(cached.username)
const userMe = ref<UserMe | null>(cached.userMe)

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)
  const isDiscordUser = computed(() => !!userMe.value?.is_discord_user)
  /** Есть ли у пользователя права админа хотя бы на одном сервере (для Discord — admin_guild_ids.length > 0). */
  const hasGuildAdminAccess = computed(() => {
    const me = userMe.value
    if (!me) return true
    if (me.auth_type !== 'discord') return true
    return (me.admin_guild_ids?.length ?? 0) > 0
  })
  const defaultGuildId = computed(() => userMe.value?.default_guild_id ?? null)

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
      clearCachedUserMe()
      username.value = null
      userMe.value = null
    }
  }

  async function loadMe() {
    if (!token.value) return
    try {
      const me = await authApi.getMe(token.value)
      userMe.value = me
      username.value = me.username
      setCachedUserMe(me)
    } catch {
      username.value = null
      userMe.value = null
      clearCachedUserMe()
    }
  }

  async function login(loginUsername: string, password: string) {
    const data = await authApi.login({ username: loginUsername, password })
    setToken(data.access_token)
    await loadMe()
  }

  async function setDefaultGuild(guildId: string | null) {
    if (!token.value) return
    const me = await authApi.setDefaultGuild(token.value, guildId)
    userMe.value = me
    setCachedUserMe(me)
  }

  function logout() {
    setToken(null)
    router.push('/login')
  }

  return {
    token,
    username,
    userMe,
    isAuthenticated,
    isDiscordUser,
    hasGuildAdminAccess,
    defaultGuildId,
    login,
    logout,
    setToken,
    loadMe,
    setDefaultGuild,
  }
}
