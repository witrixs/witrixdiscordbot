import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import * as authApi from '@/api/auth'
import { TOKEN_KEY } from '@/api/auth'

const token = ref<string | null>(localStorage.getItem(TOKEN_KEY))

export function useAuth() {
  const router = useRouter()

  const isAuthenticated = computed(() => !!token.value)

  function setToken(newToken: string | null) {
    token.value = newToken
    if (newToken) {
      localStorage.setItem(TOKEN_KEY, newToken)
    } else {
      localStorage.removeItem(TOKEN_KEY)
    }
  }

  async function login(username: string, password: string) {
    const data = await authApi.login({ username, password })
    setToken(data.access_token)
  }

  function logout() {
    setToken(null)
    router.push('/login')
  }

  return {
    token,
    isAuthenticated,
    login,
    logout,
    setToken,
  }
}
