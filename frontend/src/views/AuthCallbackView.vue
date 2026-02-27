<script setup lang="ts">
import { onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { setToken, loadMe } = useAuth()

onMounted(() => {
  const hash = window.location.hash.slice(1)
  const params = new URLSearchParams(hash)
  const accessToken = params.get('access_token')
  const error = new URLSearchParams(window.location.search).get('error')

  if (error) {
    router.replace({ path: '/login', query: { error: error === 'discord_denied' ? 'discord_denied' : 'discord_error' } })
    return
  }

  if (accessToken) {
    setToken(accessToken)
    loadMe().then(() => {
      router.replace('/dashboard')
    }).catch(() => {
      setToken(null)
      router.replace('/login')
    })
  } else {
    router.replace('/login')
  }
})
</script>

<template>
  <div class="auth-callback">
    <div class="auth-callback-card">
      <span class="auth-callback-spinner" />
      <p>Вход через Discord…</p>
    </div>
  </div>
</template>

<style scoped>
.auth-callback {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--auth-bg, #0d0f14);
}
.auth-callback-card {
  text-align: center;
  padding: 2rem;
}
.auth-callback-spinner {
  display: inline-block;
  width: 40px;
  height: 40px;
  border: 3px solid rgba(88, 101, 242, 0.3);
  border-top-color: #5865f2;
  border-radius: 50%;
  animation: auth-callback-spin 0.8s linear infinite;
}
.auth-callback p {
  margin-top: 1rem;
  color: var(--auth-text-muted, #94a3b8);
}
@keyframes auth-callback-spin {
  to { transform: rotate(360deg); }
}
</style>
