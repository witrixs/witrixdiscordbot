<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useGuild } from '@/composables/useGuild'
import { fetchGuildUsersCount, fetchGuildUsers } from '@/api/guilds'
import type { UserLevelOut } from '@/api/guilds.types'
import AppLoader from '@/components/AppLoader.vue'

const { selectedGuildId } = useGuild()
const loading = ref(true)
const contentVisible = ref(false)
const statsVisible = ref(false)
const userCount = ref(0)
const topUsers = ref<UserLevelOut[]>([])

function getMessageThreshold(level: number): number {
  if (level <= 1) return 0
  return Math.floor((5 * (level - 1) * level) / 2)
}
function getXpThreshold(level: number): number {
  if (level <= 5) return getMessageThreshold(level)
  return getMessageThreshold(5) + (level - 5) * 600
}

function progressForUser(u: UserLevelOut): { progress: number; label: string } | null {
  if (u.level < 5) return null
  const currentThreshold = getXpThreshold(u.level)
  const nextThreshold = getXpThreshold(u.level + 1)
  const requiredInSegment = nextThreshold - currentThreshold
  const xpInSegment = Math.max(0, u.xp - currentThreshold)
  const progress = requiredInSegment > 0 ? Math.min(1, xpInSegment / requiredInSegment) : 1
  return { progress, label: `${Math.floor(u.xp)}/${nextThreshold} XP до след. ур.` }
}

const progressByUserId = computed(() => {
  const map: Record<string, { progress: number; label: string }> = {}
  topUsers.value.forEach((u) => {
    const p = progressForUser(u)
    if (p) map[u.user_id] = p
  })
  return map
})

async function load() {
  if (!selectedGuildId.value) {
    loading.value = false
    userCount.value = 0
    topUsers.value = []
    return
  }
  loading.value = true
  contentVisible.value = false
  statsVisible.value = false
  try {
    const [count, list] = await Promise.all([
      fetchGuildUsersCount(selectedGuildId.value),
      fetchGuildUsers(selectedGuildId.value, {
        offset: 0,
        limit: 10,
        order_by: 'level',
        order: 'desc',
      }),
    ])
    userCount.value = count
    topUsers.value = list
  } finally {
    loading.value = false
    requestAnimationFrame(() => {
      contentVisible.value = true
    })
    setTimeout(() => {
      statsVisible.value = true
    }, 100)
  }
}

function displayName(u: UserLevelOut) {
  return u.display_name || `Участник #${u.user_id}`
}

function avatarLetter(u: UserLevelOut) {
  return displayName(u).charAt(0).toUpperCase()
}

watch(selectedGuildId, load)
onMounted(load)
</script>

<template>
  <div class="dashboard-page">
    <div v-if="loading" class="dashboard-loading">
      <AppLoader size="lg" />
      <p class="dashboard-loading-text">Загрузка панели…</p>
    </div>

    <template v-else>
      <div v-if="!selectedGuildId" class="dashboard-empty">
        <p>Выберите сервер в шапке, чтобы увидеть статистику.</p>
      </div>

      <div v-else class="dashboard-content" :class="{ 'dashboard-content--visible': contentVisible }">
        <header class="dashboard-page-header">
          <h1 class="dashboard-page-title">Панель управления</h1>
          <p class="dashboard-page-subtitle">
            Статистика сервера и топ участников по уровням
          </p>
        </header>

        <div class="dashboard-stats" :class="{ 'dashboard-stats--visible': statsVisible }">
          <div class="dashboard-stat">
            <span class="dashboard-stat-value">{{ userCount }}</span>
            <span class="dashboard-stat-label">Участников на сервере</span>
          </div>
        </div>

        <section class="dashboard-top">
          <h2 class="dashboard-top-title">Топ 10 по уровню</h2>
          <div v-if="!topUsers.length" class="dashboard-top-empty">
            <p>Пока нет данных об участниках.</p>
          </div>
          <ul v-else class="dashboard-top-list">
            <li
              v-for="(u, index) in topUsers"
              :key="u.user_id"
              class="dashboard-top-item"
              :class="{
                'dashboard-top-item--gold': index === 0,
                'dashboard-top-item--silver': index === 1,
                'dashboard-top-item--bronze': index === 2,
              }"
            >
              <span class="dashboard-top-rank">{{ index + 1 }}</span>
              <span class="dashboard-top-avatar">
                <img
                  v-if="u.avatar_url"
                  :src="u.avatar_url"
                  :alt="displayName(u)"
                  class="dashboard-top-avatar-img"
                />
                <span v-else class="dashboard-top-avatar-ph">{{ avatarLetter(u) }}</span>
              </span>
              <div class="dashboard-top-info">
                <span class="dashboard-top-name-wrap">
                  <span class="dashboard-top-name">{{ displayName(u) }}</span>
                  <span v-if="index === 0" class="dashboard-top-crown" aria-hidden="true" title="1 место">👑</span>
                </span>
                <span class="dashboard-top-meta">Ур. {{ u.level }} · {{ u.xp }} XP</span>
                <div v-if="progressByUserId[u.user_id]" class="dashboard-top-progress-wrap">
                  <div class="dashboard-top-progress-track" role="progressbar" :aria-valuenow="(progressByUserId[u.user_id]?.progress ?? 0) * 100" aria-valuemin="0" aria-valuemax="100">
                    <div class="dashboard-top-progress-fill" :style="{ width: `${Math.round((progressByUserId[u.user_id]?.progress ?? 0) * 100)}%` }" />
                  </div>
                  <span class="dashboard-top-progress-label">{{ progressByUserId[u.user_id]?.label ?? '' }}</span>
                </div>
              </div>
            </li>
          </ul>
        </section>
      </div>
    </template>
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

.dashboard-empty {
  padding: 2rem;
  text-align: center;
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
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  transition: background 0.2s, border-color 0.2s;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.dashboard-stat:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
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

.dashboard-top {
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 1.25rem;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.dashboard-top-title {
  margin: 0 0 1rem;
  font-size: 1.125rem;
  font-weight: 600;
  color: var(--color-text);
}

.dashboard-top-empty {
  padding: 1rem 0;
  text-align: center;
  color: var(--color-text-muted);
  font-size: 0.9375rem;
}

.dashboard-top-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.dashboard-top-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.75rem;
  background: var(--color-background-muted);
  border-radius: 10px;
  transition: background 0.2s;
}

.dashboard-top-item:hover {
  background: var(--color-surface-hover);
}

.dashboard-top-item--gold {
  border: 2px solid #d4af37;
  box-shadow: 0 0 0 1px rgba(212, 175, 55, 0.3), 0 4px 12px rgba(212, 175, 55, 0.15);
  background: linear-gradient(135deg, rgba(212, 175, 55, 0.08), rgba(212, 175, 55, 0.02));
}

.dashboard-top-item--silver {
  border: 2px solid #c0c0c0;
  box-shadow: 0 0 0 1px rgba(192, 192, 192, 0.3), 0 4px 12px rgba(192, 192, 192, 0.12);
  background: linear-gradient(135deg, rgba(192, 192, 192, 0.08), rgba(192, 192, 192, 0.02));
}

.dashboard-top-item--bronze {
  border: 2px solid #cd7f32;
  box-shadow: 0 0 0 1px rgba(205, 127, 50, 0.3), 0 4px 12px rgba(205, 127, 50, 0.12);
  background: linear-gradient(135deg, rgba(205, 127, 50, 0.08), rgba(205, 127, 50, 0.02));
}

.dashboard-top-rank {
  flex-shrink: 0;
  width: 24px;
  font-size: 0.875rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-align: center;
}

.dashboard-top-avatar {
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #5865f2, #7289da);
  display: flex;
  align-items: center;
  justify-content: center;
}

.dashboard-top-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.dashboard-top-avatar-ph {
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
}

.dashboard-top-info {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.dashboard-top-name-wrap {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  min-width: 0;
}

.dashboard-top-name {
  font-size: 0.9375rem;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dashboard-top-crown {
  flex-shrink: 0;
  display: inline-flex;
  align-items: center;
  font-size: 1.125rem;
  line-height: 1;
}

.dashboard-top-meta {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.dashboard-top-progress-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
  min-height: 0.75rem;
}

.dashboard-top-progress-track {
  flex: 1;
  min-width: 0;
  height: 6px;
  border-radius: 3px;
  background: var(--color-input-bg);
  overflow: hidden;
}

.dashboard-top-progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #5865f2, #9b59b6);
  transition: width 0.25s ease;
  min-width: 0;
}

.dashboard-top-progress-label {
  flex-shrink: 0;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  max-width: 45%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 639px) {
  .dashboard-stats {
    grid-template-columns: 1fr;
  }
}
</style>
