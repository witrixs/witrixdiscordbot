<script setup lang="ts">
import { ref, onMounted } from 'vue'
import AppLoader from '@/components/AppLoader.vue'

const loading = ref(true)
const contentVisible = ref(false)
const statsVisible = ref(false)

onMounted(() => {
  // Имитация загрузки данных
  const t = setTimeout(() => {
    loading.value = false
    requestAnimationFrame(() => {
      contentVisible.value = true
    })
    setTimeout(() => {
      statsVisible.value = true
    }, 100)
  }, 800)
  return () => clearTimeout(t)
})
</script>

<template>
  <div class="dashboard-page">
    <!-- Загрузка -->
    <div v-if="loading" class="dashboard-loading">
      <AppLoader size="lg" />
      <p class="dashboard-loading-text">Загрузка панели…</p>
    </div>

    <!-- Контент после загрузки -->
    <div v-else class="dashboard-content" :class="{ 'dashboard-content--visible': contentVisible }">
      <header class="dashboard-page-header">
        <h1 class="dashboard-page-title">Панель управления</h1>
        <p class="dashboard-page-subtitle">
          Управление ботом и настройки серверов Discord
        </p>
      </header>

      <!-- Карточки-статистики (заглушки) -->
      <div class="dashboard-stats" :class="{ 'dashboard-stats--visible': statsVisible }">
        <div class="dashboard-stat">
          <span class="dashboard-stat-value">—</span>
          <span class="dashboard-stat-label">Серверов</span>
        </div>
        <div class="dashboard-stat">
          <span class="dashboard-stat-value">—</span>
          <span class="dashboard-stat-label">Пользователей</span>
        </div>
        <div class="dashboard-stat">
          <span class="dashboard-stat-value">—</span>
          <span class="dashboard-stat-label">Активность</span>
        </div>
      </div>

      <!-- Основная карточка успеха -->
      <div class="dashboard-card" :class="{ 'dashboard-card--visible': contentVisible }">
        <div class="dashboard-card-glow" />
        <div class="dashboard-card-inner">
          <div class="dashboard-success">
            <span class="dashboard-success-icon" aria-hidden="true">✓</span>
            <h2 class="dashboard-success-title">Вы успешно авторизованы</h2>
            <p class="dashboard-success-text">
              Панель управления в разработке. Скоро здесь появятся настройки бота, серверов и статистика.
            </p>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.dashboard-page {
  min-height: 0;
  animation: dashboard-fadeIn 0.4s ease;
}

@keyframes dashboard-fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

.dashboard-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  gap: 1.25rem;
}

.dashboard-loading-text {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.dashboard-content {
  opacity: 0;
  transform: translateY(12px);
  transition: opacity 0.45s cubic-bezier(0.22, 1, 0.36, 1), transform 0.45s cubic-bezier(0.22, 1, 0.36, 1);
}

.dashboard-content--visible {
  opacity: 1;
  transform: translateY(0);
}

.dashboard-page-header {
  margin-bottom: 1.5rem;
}

.dashboard-page-title {
  margin: 0 0 0.25rem;
  font-size: 1.5rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.dashboard-page-subtitle {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.dashboard-stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 1rem;
  margin-bottom: 1.5rem;
  opacity: 0;
  transform: translateY(8px);
  transition: opacity 0.4s ease 0.05s, transform 0.4s ease 0.05s;
}

.dashboard-stats--visible {
  opacity: 1;
  transform: translateY(0);
}

.dashboard-stat {
  padding: 1rem 1.25rem;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 14px;
  transition: background 0.2s, border-color 0.2s;
}

.dashboard-stat:hover {
  background: rgba(255, 255, 255, 0.07);
  border-color: rgba(255, 255, 255, 0.1);
}

.dashboard-stat-value {
  display: block;
  font-size: 1.5rem;
  font-weight: 700;
  letter-spacing: -0.02em;
  color: var(--color-text);
  margin-bottom: 0.25rem;
}

.dashboard-stat-label {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.dashboard-card {
  opacity: 0;
  transform: translateY(16px);
  transition: opacity 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.1s, transform 0.5s cubic-bezier(0.22, 1, 0.36, 1) 0.1s;
}

.dashboard-card--visible {
  opacity: 1;
  transform: translateY(0);
}

.dashboard-card-glow {
  position: absolute;
  inset: -1px;
  border-radius: 18px;
  padding: 1px;
  background: linear-gradient(135deg, rgba(255, 255, 255, 0.12), rgba(255, 255, 255, 0.02));
  -webkit-mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  mask: linear-gradient(#fff 0 0) content-box, linear-gradient(#fff 0 0);
  -webkit-mask-composite: xor;
  mask-composite: exclude;
  pointer-events: none;
}

.dashboard-card-inner {
  position: relative;
  padding: 2rem 1.75rem;
  background: rgba(255, 255, 255, 0.06);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border-radius: 16px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  box-shadow:
    0 0 0 1px rgba(0, 0, 0, 0.2) inset,
    0 20px 40px -12px rgba(0, 0, 0, 0.3);
}

.dashboard-success {
  text-align: center;
}

.dashboard-success-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 56px;
  height: 56px;
  margin-bottom: 1rem;
  font-size: 1.75rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #22c55e, #16a34a);
  border-radius: 50%;
  box-shadow: 0 6px 20px rgba(34, 197, 94, 0.35);
}

.dashboard-success-title {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.dashboard-success-text {
  margin: 0;
  font-size: 0.9375rem;
  line-height: 1.6;
  color: var(--color-text-muted);
}

@media (max-width: 639px) {
  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}
</style>
