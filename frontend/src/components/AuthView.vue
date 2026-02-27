<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '@/composables/useAuth'

const router = useRouter()
const { login } = useAuth()

const username = ref('')
const password = ref('')
const loading = ref(false)
const errorMessage = ref('')
const cardVisible = ref(false)
const formVisible = ref(false)

async function handleSubmit() {
  errorMessage.value = ''
  loading.value = true
  try {
    await login(username.value, password.value)
    router.push('/dashboard')
  } catch (e) {
    errorMessage.value = e instanceof Error ? e.message : 'Ошибка входа'
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  requestAnimationFrame(() => {
    cardVisible.value = true
  })
  setTimeout(() => {
    formVisible.value = true
  }, 200)
})
</script>

<template>
  <div class="auth-page">
    <!-- Animated background -->
    <div class="auth-bg">
      <div class="auth-bg-gradient" />
      <div class="auth-bg-grid" />
      <div class="auth-bg-orb auth-bg-orb-1" />
      <div class="auth-bg-orb auth-bg-orb-2" />
      <div class="auth-bg-orb auth-bg-orb-3" />
      <div class="auth-bg-noise" />
    </div>

    <!-- Glass card -->
    <div class="auth-card" :class="{ 'auth-card--visible': cardVisible }">
      <div class="auth-card-glow" />
      <div class="auth-card-inner">
        <header class="auth-header">
          <div class="auth-logo">
            <span class="auth-logo-icon">W</span>
            <span class="auth-logo-text">Witrix Bot</span>
          </div>
          <p class="auth-tagline">Панель управления</p>
        </header>

        <form class="auth-form" :class="{ 'auth-form--visible': formVisible }" @submit.prevent="handleSubmit">
          <p v-if="errorMessage" class="auth-error">{{ errorMessage }}</p>
          <div class="auth-field">
            <label for="username">Логин</label>
            <input
              id="username"
              v-model="username"
              type="text"
              autocomplete="username"
              placeholder="admin"
              required
            />
          </div>
          <div class="auth-field">
            <label for="password">Пароль</label>
            <input
              id="password"
              v-model="password"
              type="password"
              autocomplete="current-password"
              placeholder="••••••••"
              required
            />
          </div>
          <button type="submit" class="auth-submit" :disabled="loading">
            <span v-if="!loading">Войти</span>
            <span v-else class="auth-submit-loading">
              <span class="auth-spinner" /> Вход…
            </span>
          </button>
        </form>

        <div class="auth-divider">
          <span>или</span>
        </div>

        <a href="#" class="auth-discord" @click.prevent>
          <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M20.317 4.37a19.791 19.791 0 0 0-4.885-1.515.074.074 0 0 0-.079.037c-.21.375-.444.864-.608 1.25a18.27 18.27 0 0 0-5.487 0 12.64 12.64 0 0 0-.617-1.25.077.077 0 0 0-.079-.037A19.736 19.736 0 0 0 3.677 4.37a.07.07 0 0 0-.032.027C.533 9.046-.32 13.58.099 18.057a.082.082 0 0 0 .031.057 19.9 19.9 0 0 0 5.993 3.03.078.078 0 0 0 .084-.028 14.09 14.09 0 0 0 1.226-1.994.076.076 0 0 0-.041-.106 13.107 13.107 0 0 1-1.872-.892.077.077 0 0 1-.008-.128 10.2 10.2 0 0 0 .372-.292.074.074 0 0 1 .077-.01c3.928 1.793 8.18 1.793 12.062 0a.074.074 0 0 1 .078.01c.12.098.246.198.373.292a.077.077 0 0 1-.006.127 12.299 12.299 0 0 1-1.873.892.077.077 0 0 0-.041.107c.36.698.772 1.362 1.225 1.993a.076.076 0 0 0 .084.028 19.839 19.839 0 0 0 6.002-3.03.077.077 0 0 0 .032-.054c.5-5.177-.838-9.674-3.549-13.66a.061.061 0 0 0-.031-.03zM8.02 15.33c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.956-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.956 2.418-2.157 2.418zm7.975 0c-1.183 0-2.157-1.085-2.157-2.419 0-1.333.955-2.419 2.157-2.419 1.21 0 2.176 1.096 2.157 2.42 0 1.333-.946 2.418-2.157 2.418z"/>
          </svg>
          Войти через Discord
        </a>

        <p class="auth-footer">
          Нет аккаунта? <a href="#">Связаться с администратором</a>
        </p>
      </div>
    </div>
  </div>
</template>

<style scoped>
.auth-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1.5rem;
  position: relative;
  overflow: hidden;
}

/* Background */
.auth-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
}

.auth-bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(88, 101, 242, 0.25), transparent),
    radial-gradient(ellipse 60% 40% at 100% 50%, rgba(88, 101, 242, 0.12), transparent),
    radial-gradient(ellipse 50% 30% at 0% 80%, rgba(114, 137, 218, 0.1), transparent);
  animation: auth-bg-pulse 12s ease-in-out infinite;
}

.auth-bg-grid {
  position: absolute;
  inset: 0;
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 64px 64px;
  mask-image: radial-gradient(ellipse 70% 70% at 50% 50%, black, transparent 80%);
}

.auth-bg-orb {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: auth-bg-orb 20s ease-in-out infinite;
}

.auth-bg-orb-1 {
  width: 400px;
  height: 400px;
  background: rgba(88, 101, 242, 0.3);
  top: -15%;
  left: -10%;
  animation-delay: 0s;
}

.auth-bg-orb-2 {
  width: 300px;
  height: 300px;
  background: rgba(114, 137, 218, 0.25);
  bottom: -10%;
  right: -5%;
  animation-delay: -7s;
}

.auth-bg-orb-3 {
  width: 200px;
  height: 200px;
  background: rgba(88, 101, 242, 0.2);
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-delay: -14s;
}

.auth-bg-noise {
  position: absolute;
  inset: 0;
  opacity: 0.03;
  background-image: url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)'/%3E%3C/svg%3E");
  pointer-events: none;
}

@keyframes auth-bg-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.85; }
}

@keyframes auth-bg-orb {
  0%, 100% { transform: translate(0, 0) scale(1); }
  33% { transform: translate(2%, -3%) scale(1.05); }
  66% { transform: translate(-2%, 2%) scale(0.98); }
}

/* Glass card */
.auth-card {
  position: relative;
  z-index: 1;
  width: 100%;
  max-width: 400px;
  opacity: 0;
  transform: translateY(24px);
  transition: opacity 0.6s cubic-bezier(0.22, 1, 0.36, 1), transform 0.6s cubic-bezier(0.22, 1, 0.36, 1);
}

.auth-card--visible {
  opacity: 1;
  transform: translateY(0);
}

.auth-card-glow {
  position: absolute;
  inset: -1px;
  border-radius: 24px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255,255,255,0.2), rgba(255,255,255,0.02));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.auth-card-inner {
  position: relative;
  padding: 2rem 2rem 1.75rem;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 22px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.2) inset,
    0 24px 48px -12px rgba(0, 0, 0, 0.4);
}

.auth-header {
  text-align: center;
  margin-bottom: 1.75rem;
}

.auth-logo {
  display: inline-flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}

.auth-logo-icon {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #5865f2, #7289da);
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(88, 101, 242, 0.4);
}

.auth-logo-text {
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--auth-text);
}

.auth-tagline {
  font-size: 0.875rem;
  color: var(--auth-text-muted);
  margin: 0;
}

/* Form */
.auth-form {
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.4s ease 0.1s, transform 0.4s ease 0.1s;
}

.auth-form--visible {
  opacity: 1;
  transform: translateY(0);
}

.auth-error {
  margin: 0 0 1rem;
  padding: 0.75rem 1rem;
  font-size: 0.875rem;
  color: #f87171;
  background: rgba(248, 113, 113, 0.12);
  border: 1px solid rgba(248, 113, 113, 0.25);
  border-radius: 12px;
}

.auth-field {
  margin-bottom: 1rem;
}

.auth-field label {
  display: block;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--auth-text-muted);
  margin-bottom: 0.375rem;
}

.auth-field input {
  width: 100%;
  padding: 0.75rem 1rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--auth-text);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  outline: none;
  transition: border-color 0.2s, box-shadow 0.2s, background 0.2s;
  box-sizing: border-box;
}

.auth-field input::placeholder {
  color: var(--auth-text-muted);
  opacity: 0.7;
}

.auth-field input:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.14);
}

.auth-field input:focus {
  border-color: rgba(88, 101, 242, 0.6);
  box-shadow: 0 0 0 3px rgba(88, 101, 242, 0.15);
}

.auth-submit {
  width: 100%;
  margin-top: 0.5rem;
  padding: 0.875rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  color: #fff;
  background: linear-gradient(135deg, #5865f2, #4752c4);
  border: none;
  border-radius: 12px;
  cursor: pointer;
  transition: transform 0.15s, box-shadow 0.2s, opacity 0.2s;
  box-shadow: 0 4px 14px rgba(88, 101, 242, 0.4);
}

.auth-submit:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 6px 20px rgba(88, 101, 242, 0.45);
}

.auth-submit:active:not(:disabled) {
  transform: translateY(0);
}

.auth-submit:disabled {
  opacity: 0.8;
  cursor: not-allowed;
}

.auth-submit-loading {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
}

.auth-spinner {
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: #fff;
  border-radius: 50%;
  animation: auth-spin 0.8s linear infinite;
}

@keyframes auth-spin {
  to { transform: rotate(360deg); }
}

.auth-divider {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin: 1.5rem 0 1rem;
}

.auth-divider::before,
.auth-divider::after {
  content: '';
  flex: 1;
  height: 1px;
  background: rgba(255, 255, 255, 0.1);
}

.auth-divider span {
  font-size: 0.75rem;
  font-weight: 500;
  color: var(--auth-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.auth-discord {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.75rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  font-family: inherit;
  color: var(--auth-text);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  text-decoration: none;
  transition: background 0.2s, border-color 0.2s, transform 0.15s;
}

.auth-discord:hover {
  background: rgba(255, 255, 255, 0.1);
  border-color: rgba(255, 255, 255, 0.15);
  transform: translateY(-1px);
}

.auth-discord svg {
  flex-shrink: 0;
}

.auth-footer {
  margin: 1.25rem 0 0;
  font-size: 0.8125rem;
  color: var(--auth-text-muted);
  text-align: center;
}

.auth-footer a {
  color: #5865f2;
  text-decoration: none;
  font-weight: 500;
}

.auth-footer a:hover {
  text-decoration: underline;
}

@media (prefers-color-scheme: light) {
  .auth-card-inner {
    background: rgba(255, 255, 255, 0.75);
    border-color: rgba(0, 0, 0, 0.06);
    box-shadow:
      0 0 0 1px rgba(0, 0, 0, 0.04) inset,
      0 24px 48px -12px rgba(0, 0, 0, 0.12);
  }
  .auth-card-glow {
    background: linear-gradient(135deg, rgba(255,255,255,0.9), rgba(255,255,255,0.4));
  }
  .auth-field input {
    background: rgba(0, 0, 0, 0.04);
    border-color: rgba(0, 0, 0, 0.08);
    color: var(--auth-text);
  }
  .auth-field input:hover {
    background: rgba(0, 0, 0, 0.06);
    border-color: rgba(0, 0, 0, 0.12);
  }
  .auth-discord {
    background: rgba(0, 0, 0, 0.04);
    border-color: rgba(0, 0, 0, 0.08);
    color: var(--auth-text);
  }
  .auth-discord:hover {
    background: rgba(0, 0, 0, 0.08);
    border-color: rgba(0, 0, 0, 0.12);
  }
  .auth-bg-grid {
    background-image:
      linear-gradient(rgba(0, 0, 0, 0.04) 1px, transparent 1px),
      linear-gradient(90deg, rgba(0, 0, 0, 0.04) 1px, transparent 1px);
  }
}
</style>
