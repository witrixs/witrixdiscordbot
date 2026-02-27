<script setup lang="ts">
import { ref, watch, onMounted, computed, TransitionGroup } from 'vue'
import { useGuild } from '@/composables/useGuild'
import { useToast } from '@/composables/useToast'
import {
  fetchGuildUsers,
  fetchGuildUsersCount,
  updateUserLevel,
} from '@/api/guilds'
import type { UserLevelOut } from '@/api/guilds.types'
import AppLoader from '@/components/AppLoader.vue'
import SkeletonBlock from '@/components/SkeletonBlock.vue'

const PAGE_SIZE = 20
const { selectedGuildId } = useGuild()
const { toast } = useToast()
const loading = ref(true)
const error = ref('')
const totalCount = ref(0)
const page = ref(0)
const expandedId = ref<string | null>(null)
const editForm = ref({ level: 0, xp: 0 })
const searchQuery = ref('')
const loadedPages = ref<Record<number, UserLevelOut[]>>({})
const loadingPage = ref<number | null>(null)
let saveTimeout: ReturnType<typeof setTimeout> | null = null

function displayName(u: UserLevelOut) {
  return u.display_name || `Участник #${u.user_id}`
}

function matchesSearch(u: UserLevelOut, q: string): boolean {
  if (!q.trim()) return true
  const lower = q.trim().toLowerCase()
  const name = displayName(u).toLowerCase()
  const id = u.user_id.toLowerCase()
  return name.includes(lower) || id.includes(lower)
}

const mergedLoaded = computed(() => {
  const keys = Object.keys(loadedPages.value)
    .map(Number)
    .sort((a, b) => a - b)
  return keys.flatMap((k) => loadedPages.value[k] ?? [])
})

const filteredUsers = computed(() => {
  const q = searchQuery.value
  if (!q.trim()) return mergedLoaded.value
  return mergedLoaded.value.filter((u) => matchesSearch(u, q))
})

const totalPages = computed(() => {
  if (searchQuery.value.trim()) {
    return Math.max(1, Math.ceil(filteredUsers.value.length / PAGE_SIZE))
  }
  return Math.max(1, Math.ceil(totalCount.value / PAGE_SIZE))
})
const hasMore = computed(() => page.value + 1 < totalPages.value)
const canPrev = computed(() => page.value > 0)

const displayedUsers = computed(() => {
  const start = page.value * PAGE_SIZE
  return filteredUsers.value.slice(start, start + PAGE_SIZE)
})

const isPageLoading = computed(() => loadingPage.value === page.value && !(loadedPages.value[page.value]?.length))

const progressByUserId = computed(() => {
  const map: Record<string, { progress: number; label: string; nextThreshold: number }> = {}
  displayedUsers.value.forEach((u) => {
    const p = progressForUser(u)
    if (p) map[u.user_id] = p
  })
  return map
})

function avatarLetter(u: UserLevelOut) {
  const name = displayName(u)
  return name.charAt(0).toUpperCase()
}

// Пороги XP как в бэкенде (LEVEL_RULES.md)
function getMessageThreshold(level: number): number {
  if (level <= 1) return 0
  return Math.floor((5 * (level - 1) * level) / 2)
}
function getXpThreshold(level: number): number {
  if (level <= 5) return getMessageThreshold(level)
  return getMessageThreshold(5) + (level - 5) * 600
}

/** Уровень по XP (как на бэкенде), для подгонки уровня под XP при редактировании. */
function getLevelFromXp(xp: number): number {
  if (xp < getXpThreshold(5)) {
    for (let lvl = 2; lvl <= 5; lvl++) {
      if (xp < getMessageThreshold(lvl)) return lvl - 1
    }
    return 4
  }
  for (let lvl = 5; lvl < 1000; lvl++) {
    if (xp < getXpThreshold(lvl + 1)) return lvl
  }
  return 999
}

// Шкала только для уровня 5+: в рамках 600 XP до след. уровня (как в /level и LEVEL_RULES)
function progressForUser(u: UserLevelOut): { progress: number; label: string; nextThreshold: number } | null {
  if (u.level < 5) return null
  const currentThreshold = getXpThreshold(u.level)
  const nextThreshold = getXpThreshold(u.level + 1)
  const requiredInSegment = nextThreshold - currentThreshold // 600 XP
  const xpInSegment = Math.max(0, u.xp - currentThreshold)
  const progress = requiredInSegment > 0 ? Math.min(1, xpInSegment / requiredInSegment) : 1
  return { progress, label: `${Math.floor(u.xp)}/${nextThreshold} XP до след. ур.`, nextThreshold }
}

async function loadPage(pageIndex: number) {
  if (!selectedGuildId.value || loadedPages.value[pageIndex]?.length) return
  loadingPage.value = pageIndex
  try {
    const list = await fetchGuildUsers(selectedGuildId.value, {
      offset: pageIndex * PAGE_SIZE,
      limit: PAGE_SIZE,
      order_by: 'level',
      order: 'desc',
    })
    loadedPages.value = { ...loadedPages.value, [pageIndex]: list }
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loadingPage.value = null
  }
}

async function loadAll() {
  if (!selectedGuildId.value) return
  loading.value = true
  error.value = ''
  loadedPages.value = {}
  try {
    totalCount.value = await fetchGuildUsersCount(selectedGuildId.value)
    await loadPage(0)
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

function nextPage() {
  if (!hasMore.value) return
  const next = page.value + 1
  page.value = next
  loadPage(next)
}

function prevPage() {
  if (!canPrev.value) return
  page.value -= 1
}

function toggleExpand(u: UserLevelOut) {
  if (expandedId.value === u.user_id) {
    expandedId.value = null
    return
  }
  expandedId.value = u.user_id
  editForm.value = { level: u.level, xp: u.xp }
}

function scheduleSave(userId: string) {
  if (saveTimeout) clearTimeout(saveTimeout)
  const level = Math.max(1, editForm.value.level || 1)
  const xp = Math.max(0, editForm.value.xp || 0)
  saveTimeout = setTimeout(() => doSave(userId, level, xp), 600)
}

async function doSave(userId: string, level: number, xp: number) {
  if (!selectedGuildId.value) return
  error.value = ''
  try {
    const updated = await updateUserLevel(selectedGuildId.value, userId, {
      level,
      xp,
    })
    for (const [p, list] of Object.entries(loadedPages.value)) {
      const idx = list.findIndex((x) => x.user_id === userId)
      if (idx >= 0) {
        const newList = [...list]
        newList[idx] = { ...list[idx], ...updated }
        loadedPages.value = { ...loadedPages.value, [Number(p)]: newList }
        break
      }
    }
    const start = page.value * PAGE_SIZE
    const onPage = filteredUsers.value.slice(start, start + PAGE_SIZE).some((x) => x.user_id === userId)
    if (!onPage) expandedId.value = null
    toast('Уровень и XP обновлены')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка сохранения'
  }
}

function onLevelChange(userId: string) {
  const lvl = Math.max(1, editForm.value.level || 1)
  editForm.value.xp = getXpThreshold(lvl)
  scheduleSave(userId)
}

function onXpChange(userId: string) {
  const xp = Math.max(0, editForm.value.xp || 0)
  editForm.value.level = getLevelFromXp(xp)
  scheduleSave(userId)
}

watch(selectedGuildId, () => {
  page.value = 0
  expandedId.value = null
  searchQuery.value = ''
  loadAll()
})
watch(searchQuery, () => {
  page.value = 0
})
watch(page, (p) => {
  loadPage(p)
})
onMounted(() => {
  if (selectedGuildId.value) loadAll()
})
</script>

<template>
  <div class="users-page">
    <div v-if="!selectedGuildId" class="users-empty">
      <p>Выберите сервер сверху.</p>
    </div>

    <template v-else>
      <header class="users-header">
        <h1 class="users-title">Пользователи</h1>
        <p class="users-subtitle">Нажмите на участника, чтобы изменить уровень и XP (сохраняется автоматически)</p>
      </header>

      <p v-if="error" class="users-error">{{ error }}</p>

      <div v-if="loading" class="users-loading">
        <AppLoader size="lg" />
        <p>Загрузка…</p>
      </div>

      <template v-else>
        <div class="users-toolbar">
          <div class="users-search-wrap">
            <span class="users-search-icon" aria-hidden="true">🔍</span>
            <input
              v-model.trim="searchQuery"
              type="text"
              class="users-search-input"
              placeholder="Поиск по нику или ID…"
              autocomplete="off"
            />
            <button
              v-if="searchQuery"
              type="button"
              class="users-search-clear"
              aria-label="Очистить поиск"
              @click="searchQuery = ''"
            >
              ×
            </button>
          </div>
          <span class="users-total">
            <template v-if="searchQuery">
              Найдено: {{ filteredUsers.length }} из {{ totalCount }}
            </template>
            <template v-else>
              Всего на сервере: {{ totalCount }}
            </template>
          </span>
        </div>

        <ul v-if="isPageLoading" class="users-list">
          <li v-for="i in PAGE_SIZE" :key="'sk-' + i" class="users-item users-item--skeleton">
            <SkeletonBlock width="36px" height="36px" borderRadius="50%" />
            <div class="users-item-main">
              <SkeletonBlock height="0.875rem" width="60%" />
              <div class="users-skeleton-meta">
                <SkeletonBlock height="0.75rem" width="45%" />
              </div>
              <div class="users-skeleton-progress">
                <div class="users-skeleton-track">
                  <SkeletonBlock height="6px" borderRadius="3px" />
                </div>
                <SkeletonBlock height="0.6875rem" width="72px" borderRadius="4px" />
              </div>
            </div>
          </li>
        </ul>
        <TransitionGroup v-else name="users-list" tag="ul" class="users-list">
          <li
            v-for="u in displayedUsers"
            :key="u.user_id"
            class="users-item"
            :class="{ 'users-item--expanded': expandedId === u.user_id }"
            @click="toggleExpand(u)"
          >
            <span class="users-item-avatar">
              <img
                v-if="u.avatar_url"
                :src="u.avatar_url"
                :alt="displayName(u)"
                class="users-item-avatar-img"
              />
              <span v-else class="users-item-avatar-ph">{{ avatarLetter(u) }}</span>
            </span>
            <div class="users-item-main">
              <span class="users-item-name">{{ displayName(u) }}</span>
              <span class="users-item-meta">Ур. {{ u.level }} · {{ u.xp }} XP · {{ u.message_count }} сообщ.</span>
              <div v-if="progressByUserId[u.user_id]" class="users-item-progress-wrap">
                <div class="users-item-progress-track" role="progressbar" :aria-valuenow="((progressByUserId[u.user_id]?.progress) ?? 0) * 100" aria-valuemin="0" aria-valuemax="100">
                  <div class="users-item-progress-fill" :style="{ width: `${Math.round((progressByUserId[u.user_id]?.progress ?? 0) * 100)}%` }" />
                </div>
                <span class="users-item-progress-label">{{ progressByUserId[u.user_id]?.label ?? '' }}</span>
              </div>
              <Transition name="users-expand">
                <div v-if="expandedId === u.user_id" class="users-item-edit" @click.stop>
                  <label class="users-edit-label">
                    Уровень
                    <input
                      v-model.number="editForm.level"
                      type="number"
                      min="1"
                      class="users-input"
                      @input="onLevelChange(u.user_id)"
                    />
                  </label>
                  <label class="users-edit-label">
                    XP
                    <input
                      v-model.number="editForm.xp"
                      type="number"
                      min="0"
                      class="users-input"
                      @input="onXpChange(u.user_id)"
                    />
                  </label>
                </div>
              </Transition>
            </div>
            <span class="users-item-chevron" :class="{ 'users-item-chevron--open': expandedId === u.user_id }">▼</span>
          </li>
        </TransitionGroup>

        <div class="users-pagination-wrap">
          <div class="users-pagination">
            <button
              type="button"
              class="users-page-btn"
              :disabled="!canPrev"
              @click="prevPage"
            >
              Назад
            </button>
            <span class="users-page-info">Стр. {{ page + 1 }} из {{ totalPages }}</span>
            <button
              type="button"
              class="users-page-btn"
              :disabled="!hasMore"
              @click="nextPage"
            >
              Вперёд
            </button>
          </div>
        </div>
      </template>
    </template>
  </div>
</template>

<style scoped>
.users-page {
  min-height: 0;
  max-width: 560px;
  margin: 0 auto;
}

.users-empty {
  padding: 2rem;
  text-align: center;
  color: var(--color-text-muted);
}

.users-header {
  margin-bottom: 1rem;
}

.users-title {
  margin: 0 0 0.25rem;
  font-size: 1.375rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.users-subtitle {
  margin: 0;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.users-error {
  padding: 0.6rem 0.75rem;
  margin-bottom: 0.75rem;
  font-size: 0.8125rem;
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: 8px;
}

.users-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 1.5rem;
}

.users-loading p {
  margin: 0;
  color: var(--color-text-muted);
  font-size: 0.875rem;
}

.users-toolbar {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem 1rem;
  margin-bottom: 0.75rem;
}

.users-search-wrap {
  position: relative;
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 200px;
  max-width: 320px;
}

.users-search-icon {
  position: absolute;
  left: 0.75rem;
  pointer-events: none;
  font-size: 0.9375rem;
  opacity: 0.6;
}

.users-search-input {
  width: 100%;
  padding: 0.5rem 2rem 0.5rem 2.25rem;
  font-size: 0.875rem;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 10px;
  outline: none;
  transition: border-color 0.2s, background 0.2s;
}

.users-search-input::placeholder {
  color: var(--color-text-muted);
  opacity: 0.8;
}

.users-search-input:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.users-search-input:focus {
  border-color: rgba(88, 101, 242, 0.5);
  background: var(--color-bg-elevated);
  box-shadow: 0 0 0 2px rgba(88, 101, 242, 0.15);
}

.users-search-clear {
  position: absolute;
  right: 0.35rem;
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0;
  font-size: 1.1rem;
  line-height: 1;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: color 0.2s, background 0.2s;
}

.users-search-clear:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.users-total {
  font-size: 0.8125rem;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.users-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}

/* Плавное перемещение при изменении порядка после сохранения уровня/XP */
.users-list-move {
  transition: transform 0.4s ease;
}

.users-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.5rem 0.65rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  backdrop-filter: blur(8px);
  -webkit-backdrop-filter: blur(8px);
}

.users-item:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.users-item--expanded {
  border-color: rgba(88, 101, 242, 0.35);
  background: var(--color-bg-elevated);
}

.users-item--skeleton {
  pointer-events: none;
}

.users-skeleton-meta {
  margin-top: 0.25rem;
}

.users-skeleton-progress {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
}

.users-skeleton-track {
  flex: 1;
  min-width: 0;
}

.users-item-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background: linear-gradient(135deg, #5865f2, #7289da);
  display: flex;
  align-items: center;
  justify-content: center;
}

.users-item-avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
  display: block;
}

.users-item-avatar-ph {
  font-size: 0.875rem;
  font-weight: 600;
  color: #fff;
}

.users-item-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 0.125rem;
}

.users-item-name {
  font-size: 0.875rem;
  font-weight: 500;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.users-item-meta {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}

.users-item-progress-wrap {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.35rem;
  min-height: 0.75rem;
}

.users-item-progress-track {
  flex: 1;
  min-width: 0;
  height: 6px;
  border-radius: 3px;
  background: var(--color-input-bg);
  overflow: hidden;
}

.users-item-progress-fill {
  height: 100%;
  border-radius: 3px;
  background: linear-gradient(90deg, #5865f2, #9b59b6);
  transition: width 0.25s ease;
  min-width: 0;
}

.users-item-progress-label {
  flex-shrink: 0;
  font-size: 0.6875rem;
  color: var(--color-text-muted);
  max-width: 45%;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 420px) {
  .users-item-progress-wrap {
    flex-wrap: wrap;
    gap: 0.25rem;
  }
  .users-item-progress-track {
    width: 100%;
    order: 1;
  }
  .users-item-progress-label {
    max-width: 100%;
    order: 2;
    font-size: 0.65rem;
  }
}

.users-item-edit {
  margin-top: 0.5rem;
  padding-top: 0.5rem;
  border-top: 1px solid var(--color-border);
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: 0.75rem;
}

.users-edit-label {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

.users-input {
  width: 4rem;
  padding: 0.3rem 0.45rem;
  font-size: 0.8125rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 6px;
}

.users-item-chevron {
  flex-shrink: 0;
  font-size: 0.5rem;
  color: var(--color-text-muted);
  transition: transform 0.2s;
}

.users-item-chevron--open {
  transform: rotate(180deg);
}

.users-expand-enter-active,
.users-expand-leave-active {
  transition: opacity 0.2s ease, transform 0.2s ease;
}

.users-expand-enter-from,
.users-expand-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}

.users-pagination-wrap {
  display: flex;
  justify-content: center;
  margin-top: 1rem;
  padding-top: 0.75rem;
  border-top: 1px solid var(--color-border);
}

.users-pagination {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.users-page-btn {
  padding: 0.35rem 0.65rem;
  font-size: 0.8125rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s;
}

.users-page-btn:hover:not(:disabled) {
  background: var(--color-surface-hover);
}

.users-page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.users-page-info {
  font-size: 0.75rem;
  color: var(--color-text-muted);
}
</style>
