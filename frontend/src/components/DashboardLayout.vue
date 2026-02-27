<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useGuild } from '@/composables/useGuild'
import { useTheme } from '@/composables/useTheme'
import ServerSelect from '@/components/ServerSelect.vue'

const {
  logout,
  username,
  userMe,
  loadMe,
  isDiscordUser,
  hasGuildAdminAccess,
  defaultGuildId,
  setDefaultGuild,
} = useAuth()
const { guilds, selectedGuildId, setSelectedGuildId, loadGuilds } = useGuild()
const { effectiveTheme, setTheme } = useTheme()
const route = useRoute()
const sidebarOpen = ref(false)
const accountOpen = ref(false)
const logoutModalOpen = ref(false)
const firstServerModalOpen = ref(false)

const serverPlaceholder = computed(() =>
  guilds.value.length ? 'Выберите сервер' : 'Нет серверов'
)

const showNoAdminBanner = computed(
  () => isDiscordUser.value && !hasGuildAdminAccess.value
)

const navItems = computed(() => {
  const noAdmin = showNoAdminBanner.value
  return [
    { path: '/dashboard', label: 'Панель управления', icon: 'dashboard', disabled: false },
    { path: '/dashboard/users', label: 'Пользователи', icon: 'users', disabled: noAdmin },
    { path: '/dashboard/settings', label: 'Настройки', icon: 'settings', disabled: noAdmin },
  ]
})

function closeSidebar() {
  sidebarOpen.value = false
  accountOpen.value = false
}

function openLogoutModal() {
  accountOpen.value = false
  logoutModalOpen.value = true
}

function cancelLogout() {
  logoutModalOpen.value = false
}

function confirmLogout() {
  logoutModalOpen.value = false
  closeSidebar()
  logout()
}

async function pickFirstServer(guildId: string) {
  await setDefaultGuild(guildId)
  setSelectedGuildId(guildId)
  firstServerModalOpen.value = false
}

function onSelectGuild(id: string | null) {
  setSelectedGuildId(id)
  if (isDiscordUser.value && id) {
    setDefaultGuild(id)
  }
}

onMounted(async () => {
  await Promise.all([loadGuilds(), loadMe()])
  if (isDiscordUser.value && guilds.value.length > 1 && !defaultGuildId.value) {
    firstServerModalOpen.value = true
  }
  if (isDiscordUser.value && defaultGuildId.value && guilds.value.some((g) => g.id === defaultGuildId.value)) {
    setSelectedGuildId(defaultGuildId.value)
  }
})
watch(() => route.path, closeSidebar)
watch([defaultGuildId, guilds], () => {
  if (isDiscordUser.value && defaultGuildId.value && guilds.value.some((g) => g.id === defaultGuildId.value)) {
    if (!selectedGuildId.value || !guilds.value.some((g) => g.id === selectedGuildId.value)) {
      setSelectedGuildId(defaultGuildId.value)
    }
  }
}, { immediate: true })
</script>

<template>
  <div class="layout" :class="{ 'layout--sidebar-visible': sidebarOpen }">
    <div class="layout-backdrop" aria-hidden="true" @click="closeSidebar" />

    <!-- Сайдбар слева -->
    <aside class="layout-sidebar" :class="{ 'layout-sidebar--open': sidebarOpen }">
      <div class="layout-sidebar-inner">
        <div class="layout-sidebar-head">
          <span class="layout-sidebar-logo" aria-hidden="true">
            <svg viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
              <defs>
                <linearGradient id="layout-logo-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                  <stop offset="0%" stop-color="#5865f2"/>
                  <stop offset="100%" stop-color="#7289da"/>
                </linearGradient>
              </defs>
              <rect width="32" height="32" rx="8" fill="url(#layout-logo-grad)"/>
              <path d="M8 9l5 10 3-6 3 6 5-10" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
              <path d="M8 23 Q 16 28 24 23" stroke="#fff" stroke-width="2" stroke-linecap="round" fill="none"/>
            </svg>
          </span>
          <span class="layout-sidebar-brand">Discord Bot</span>
          <button
            type="button"
            class="layout-sidebar-close"
            aria-label="Закрыть меню"
            @click="closeSidebar"
          >
            <span class="layout-sidebar-close-icon">×</span>
          </button>
        </div>
        <nav class="layout-nav">
          <span class="layout-nav-section">ПЛАТФОРМА</span>
          <template v-for="item in navItems" :key="item.path">
            <router-link
              v-if="!item.disabled"
              :to="item.path"
              class="layout-nav-item"
              :class="{ 'layout-nav-item--active': route.path === item.path }"
            >
              <span class="layout-nav-icon">
                <template v-if="item.icon === 'dashboard'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
                </template>
                <template v-else-if="item.icon === 'users'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </template>
                <template v-else-if="item.icon === 'settings'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </template>
              </span>
              <span class="layout-nav-label">{{ item.label }}</span>
            </router-link>
            <span
              v-else
              class="layout-nav-item layout-nav-item--disabled"
              :title="'Нужны права администратора на сервере'"
            >
              <span class="layout-nav-icon">
                <template v-if="item.icon === 'dashboard'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
                </template>
                <template v-else-if="item.icon === 'users'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/><circle cx="9" cy="7" r="4"/><path d="M23 21v-2a4 4 0 0 0-3-3.87"/><path d="M16 3.13a4 4 0 0 1 0 7.75"/></svg>
                </template>
                <template v-else-if="item.icon === 'settings'">
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
                </template>
              </span>
              <span class="layout-nav-label">{{ item.label }}</span>
            </span>
          </template>
        </nav>
        <div class="layout-sidebar-footer">
          <div class="layout-theme-toggle" role="group" aria-label="Тема оформления">
            <button
              type="button"
              class="layout-theme-option"
              :class="{ 'layout-theme-option--active': effectiveTheme === 'dark' }"
              :aria-pressed="effectiveTheme === 'dark'"
              title="Тёмная тема"
              @click="setTheme('dark')"
            >
              <span class="layout-theme-icon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>
              </span>
              <span class="layout-theme-label">Тёмная</span>
            </button>
            <button
              type="button"
              class="layout-theme-option"
              :class="{ 'layout-theme-option--active': effectiveTheme === 'light' }"
              :aria-pressed="effectiveTheme === 'light'"
              title="Светлая тема"
              @click="setTheme('light')"
            >
              <span class="layout-theme-icon" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>
              </span>
              <span class="layout-theme-label">Светлая</span>
            </button>
          </div>
          <div class="layout-account">
            <button
              type="button"
              class="layout-account-trigger"
              :class="{ 'layout-account-trigger--open': accountOpen }"
              @click="accountOpen = !accountOpen"
            >
              <img
                v-if="userMe?.avatar_url"
                :src="userMe.avatar_url"
                :alt="username || 'Аккаунт'"
                class="layout-account-avatar layout-account-avatar--img"
              />
              <span v-else class="layout-account-avatar">{{ (username || 'А').charAt(0).toUpperCase() }}</span>
              <span class="layout-account-name">{{ username || 'Аккаунт' }}</span>
              <span class="layout-account-status">Online</span>
              <svg class="layout-account-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <Transition name="dropdown">
              <div v-if="accountOpen" class="layout-account-dropdown">
                <button type="button" class="layout-account-item layout-account-item--logout" @click="openLogoutModal">
                  Выйти
                </button>
              </div>
            </Transition>
          </div>
        </div>
      </div>
    </aside>

    <!-- Основная область -->
    <div class="layout-main">
      <div class="layout-bg" aria-hidden="true">
        <div class="layout-bg-gradient" />
        <div class="layout-bg-grid" />
      </div>
      <header class="layout-header">
        <button
          type="button"
          class="layout-burger"
          aria-label="Открыть меню"
          @click="sidebarOpen = true"
        >
          <svg class="layout-burger-icon" width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
            <line x1="4" y1="7" x2="20" y2="7" />
            <line x1="4" y1="12" x2="20" y2="12" />
            <line x1="4" y1="17" x2="20" y2="17" />
          </svg>
        </button>
        <h1 class="layout-page-title"><slot name="title">Панель</slot></h1>
        <div class="layout-server">
          <div class="layout-server-select-wrap">
            <ServerSelect
              :model-value="selectedGuildId ?? null"
              :guilds="guilds"
              :placeholder="serverPlaceholder"
              @update:model-value="onSelectGuild"
            />
          </div>
        </div>
      </header>
      <div v-if="showNoAdminBanner" class="layout-banner" role="alert">
        <span class="layout-banner-icon" aria-hidden="true">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"/><line x1="12" y1="9" x2="12" y2="13"/><line x1="12" y1="17" x2="12.01" y2="17"/></svg>
        </span>
        <span class="layout-banner-text">Для управления ботом нужны права администратора на сервере Discord. Доступны только просмотр панели и серверов, где вы состоите.</span>
      </div>
      <main class="layout-content">
        <slot />
      </main>
    </div>

    <!-- Модальное окно выбора первого сервера (Discord, первый вход) -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="firstServerModalOpen" class="logout-modal-backdrop" @click.self="firstServerModalOpen = false">
          <div class="logout-modal first-server-modal" role="dialog" aria-modal="true" aria-labelledby="first-server-modal-title">
            <h2 id="first-server-modal-title" class="logout-modal-title">Выберите сервер по умолчанию</h2>
            <p class="logout-modal-text">У вас несколько серверов с ботом. Выберите, какой открывать первым. Позже можно сменить в выпадающем списке.</p>
            <ul class="first-server-list">
              <li v-for="g in guilds" :key="g.id">
                <button type="button" class="first-server-btn" @click="pickFirstServer(g.id)">
                  <span class="first-server-name">{{ g.name }}</span>
                </button>
              </li>
            </ul>
          </div>
        </div>
      </Transition>
    </Teleport>

    <!-- Модальное окно подтверждения выхода -->
    <Teleport to="body">
      <Transition name="modal">
        <div v-if="logoutModalOpen" class="logout-modal-backdrop" @click.self="cancelLogout">
          <div class="logout-modal" role="dialog" aria-modal="true" aria-labelledby="logout-modal-title">
            <h2 id="logout-modal-title" class="logout-modal-title">Выйти из аккаунта?</h2>
            <p class="logout-modal-text">Вы будете перенаправлены на страницу входа.</p>
            <div class="logout-modal-actions">
              <button type="button" class="logout-modal-btn logout-modal-btn--cancel" @click="cancelLogout">Отмена</button>
              <button type="button" class="logout-modal-btn logout-modal-btn--confirm" @click="confirmLogout">Выйти</button>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.layout {
  height: 100vh;
  display: flex;
  position: relative;
  overflow: hidden;
}

.layout-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 40;
  background: var(--layout-backdrop);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.layout--sidebar-visible .layout-backdrop {
  display: block;
  opacity: 1;
}

/* Сайдбар слева — без скролла, всегда виден */
.layout-sidebar {
  width: 260px;
  flex-shrink: 0;
  height: 100vh;
  overflow: hidden;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--layout-sidebar-border);
  background: var(--layout-sidebar-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
}

.layout-sidebar-inner {
  display: flex;
  flex-direction: column;
  min-height: 100%;
}

.layout-sidebar-head {
  display: flex;
  align-items: center;
  justify-content: flex-start;
  gap: 0.625rem;
  padding: 1.075rem 1.25rem;
  border-bottom: 1px solid var(--layout-sidebar-border);
  flex-shrink: 0;
  box-sizing: border-box;
}

.layout-sidebar-logo {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 10px;
  overflow: hidden;
}

.layout-sidebar-logo svg {
  width: 100%;
  height: 100%;
  display: block;
}

.layout-sidebar-brand {
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1;
  color: var(--color-text);
  display: flex;
  align-items: center;
}

.layout-sidebar-close {
  display: none;
  margin-left: auto;
  width: 36px;
  height: 36px;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 8px;
  color: var(--color-text-muted);
  cursor: pointer;
}

.layout-sidebar-close:hover {
  color: var(--color-text);
  background: var(--layout-nav-hover);
}

.layout-sidebar-close-icon {
  font-size: 1.5rem;
  line-height: 1;
}

.layout-nav {
  flex: 1;
  padding: 1rem 0.75rem;
}

.layout-nav-section {
  display: block;
  padding: 0 0.5rem 0.5rem;
  font-size: 0.6875rem;
  font-weight: 600;
  letter-spacing: 0.06em;
  color: var(--color-text-muted);
}

.layout-nav-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.625rem 0.75rem;
  margin-bottom: 2px;
  border-radius: 10px;
  color: var(--color-text-muted);
  text-decoration: none;
  font-size: 0.9375rem;
  font-weight: 500;
  transition: color 0.2s, background 0.2s;
}

.layout-nav-item:hover {
  color: var(--color-text);
  background: var(--layout-nav-hover);
}

.layout-nav-item--active {
  color: #5865f2;
  background: rgba(88, 101, 242, 0.15);
}

.layout-nav-item--active .layout-nav-icon {
  color: #5865f2;
}

.layout-nav-item--disabled {
  cursor: not-allowed;
  opacity: 0.55;
  pointer-events: none;
}

.layout-nav-item--disabled .layout-nav-icon,
.layout-nav-item--disabled .layout-nav-label {
  color: var(--color-text-muted);
}

.layout-nav-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-muted);
}

.layout-nav-label {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.layout-sidebar-footer {
  padding: 0.75rem 0.75rem 1rem;
  border-top: 1px solid var(--layout-sidebar-border);
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

/* Переключатель темы в стиле iOS 26 glass */
.layout-theme-toggle {
  display: flex;
  align-items: stretch;
  gap: 0;
  padding: 4px;
  border-radius: 999px;
  background: var(--theme-toggle-track);
  backdrop-filter: blur(20px);
  -webkit-backdrop-filter: blur(20px);
  border: 1px solid var(--theme-toggle-border);
  box-shadow: 0 0 0 1px rgba(0, 0, 0, 0.03) inset;
  min-height: 40px;
}

.layout-theme-option {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.4rem 0.75rem;
  font-size: 0.8125rem;
  font-weight: 500;
  font-family: inherit;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 999px;
  cursor: pointer;
  transition: color 0.25s ease, background 0.3s cubic-bezier(0.22, 1, 0.36, 1), box-shadow 0.3s ease;
}

.layout-theme-option:hover {
  color: var(--color-text);
}

.layout-theme-option--active {
  color: var(--color-text);
  background: var(--theme-toggle-thumb);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
}

.layout-theme-icon {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0.9;
}

.layout-theme-option--active .layout-theme-icon {
  opacity: 1;
}

.layout-theme-label {
  white-space: nowrap;
}

@media (max-width: 380px) {
  .layout-theme-label {
    display: none;
  }
  .layout-theme-option {
    padding: 0.5rem;
  }
}

.layout-account {
  position: relative;
}

.layout-account-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.75rem;
  background: transparent;
  border: none;
  border-radius: 10px;
  color: var(--color-text);
  font-size: 0.875rem;
  cursor: pointer;
  transition: background 0.2s;
}

.layout-account-trigger:hover,
.layout-account-trigger--open {
  background: var(--layout-account-hover);
}

.layout-account-avatar {
  width: 32px;
  height: 32px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: 600;
  font-size: 0.875rem;
  color: #fff;
  background: linear-gradient(135deg, #5865f2, #7289da);
  border-radius: 50%;
}

.layout-account-avatar--img {
  display: block;
  object-fit: cover;
}

.layout-account-name {
  flex: 1;
  text-align: left;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.layout-account-status {
  font-size: 0.75rem;
  color: #22c55e;
}

.layout-account-chevron {
  flex-shrink: 0;
  color: var(--color-text-muted);
  transition: transform 0.2s;
}

.layout-account-trigger--open .layout-account-chevron {
  transform: rotate(180deg);
}

.layout-account-dropdown {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  margin-bottom: 4px;
  padding: 4px;
  background: var(--layout-account-dropdown-bg);
  border: 1px solid var(--layout-account-dropdown-border);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.layout-account-item {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  text-align: left;
  font-size: 0.875rem;
  color: var(--color-text);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: background 0.2s;
}

.layout-account-item:hover {
  background: var(--layout-account-item-hover);
}

.layout-account-item--logout:hover {
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
}

.dropdown-enter-active,
.dropdown-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.dropdown-enter-from,
.dropdown-leave-to {
  opacity: 0;
  transform: translateY(4px);
}

/* Модальное окно выхода */
.logout-modal-backdrop {
  position: fixed;
  inset: 0;
  z-index: 100;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 1rem;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(6px);
  -webkit-backdrop-filter: blur(6px);
}

.logout-modal {
  width: 100%;
  max-width: 380px;
  padding: 1.5rem;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-strong);
  border-radius: 16px;
  box-shadow: 0 24px 48px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.logout-modal-title {
  margin: 0 0 0.5rem;
  font-size: 1.25rem;
  font-weight: 600;
  color: var(--color-text);
}

.logout-modal-text {
  margin: 0 0 1.25rem;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.logout-modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

.logout-modal-btn {
  padding: 0.5rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 500;
  font-family: inherit;
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.logout-modal-btn--cancel {
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
}

.logout-modal-btn--cancel:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.logout-modal-btn--confirm {
  color: #fff;
  background: #e53e3e;
  border: 1px solid #c53030;
}

.logout-modal-btn--confirm:hover {
  background: #c53030;
}

.first-server-modal .logout-modal-text {
  margin-bottom: 1rem;
}

.first-server-list {
  list-style: none;
  margin: 0;
  padding: 0;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.first-server-btn {
  display: block;
  width: 100%;
  padding: 0.75rem 1rem;
  text-align: left;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.first-server-btn:hover {
  background: var(--color-surface-hover);
  border-color: rgba(88, 101, 242, 0.4);
}

.first-server-name {
  font-weight: 500;
}

.layout-banner {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  padding: 0.875rem 1.25rem;
  margin: 0 1.25rem;
  margin-top: 0.5rem;
  font-size: 0.9375rem;
  line-height: 1.4;
  color: #b45309;
  background: rgba(245, 158, 11, 0.12);
  border: 1px solid rgba(245, 158, 11, 0.3);
  border-radius: 12px;
  position: relative;
  z-index: 1;
}

.layout-banner-icon {
  flex-shrink: 0;
  width: 20px;
  height: 20px;
  color: #f59e0b;
  display: flex;
  align-items: center;
  justify-content: center;
}

.layout-banner-text {
  flex: 1;
  min-width: 0;
}

.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.2s ease;
}
.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

/* Основная область — только правая часть, скролл внутри неё */
.layout-main {
  flex: 1;
  min-width: 0;
  min-height: 0;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.layout-bg {
  position: absolute;
  inset: 0;
  z-index: 0;
  pointer-events: none;
}

.layout-bg-gradient {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 80% 50% at 50% -20%, rgba(88, 101, 242, 0.1), transparent),
    radial-gradient(ellipse 60% 40% at 100% 0%, rgba(88, 101, 242, 0.05), transparent);
}

.layout-bg-grid {
  position: absolute;
  inset: 0;
  background-image: var(--layout-bg-grid);
  background-size: 64px 64px;
}

.layout-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: .5rem 1.25rem;
  border-bottom: 1px solid var(--layout-header-border);
  background: var(--layout-header-bg);
  backdrop-filter: blur(14px);
  -webkit-backdrop-filter: blur(14px);
  flex-shrink: 0;
  box-sizing: border-box;
}

.layout-burger {
  display: none;
  flex-shrink: 0;
  width: 44px;
  height: 44px;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: var(--layout-burger-bg);
  border: 1px solid var(--layout-burger-border);
  border-radius: 12px;
  color: var(--color-text);
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s;
}

.layout-burger:hover {
  background: var(--layout-burger-hover-bg);
  border-color: var(--layout-burger-hover-border);
  color: var(--color-text);
}

.layout-burger:active {
  background: var(--layout-nav-hover);
}

.layout-burger-icon {
  display: block;
}

.layout-page-title {
  flex: 1;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1;
  display: flex;
  align-items: center;
  color: var(--color-text);
}

.layout-server {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.layout-server-select-wrap {
  min-width: 160px;
  max-width: 260px;
}

@media (max-width: 768px) {
  .layout-server-select-wrap {
    width: 60px;
    min-width: 60px;
    max-width: 60px;
  }
}

.layout-content {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  position: relative;
  z-index: 1;
  padding: 1.5rem;
}

/* Мобильная: сайдбар выезжает слева, один общий скролл страницы */
@media (max-width: 1023px) {
  .layout {
    min-height: 100vh;
    height: auto;
    overflow-x: hidden;
    overflow-y: visible;
  }

  .layout-main {
    overflow: visible;
    min-height: 100vh;
    /* Отступ под фиксированный хедер: паддинги (0.875rem*2) + контент (~44px) + зазор */
    padding-top: calc(80px + env(safe-area-inset-top, 0px));
  }

  .layout-content {
    overflow-y: visible;
    min-height: 0;
  }

  /* Хедер фиксирован сверху (бургер + заголовок + сервер) — отступы по краям */
  .layout-header {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    z-index: 15;
    padding-top: calc(0.875rem + env(safe-area-inset-top, 0px));
    padding-bottom: 0.875rem;
    padding-left: calc(1rem + env(safe-area-inset-left, 0px));
    padding-right: calc(1rem + env(safe-area-inset-right, 0px));
  }

  .layout-burger {
    display: flex;
  }

  /* Сайдбар: фиксированная высота, скролл внутри .layout-sidebar-inner */
  .layout-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 50;
    width: 280px;
    max-width: 85vw;
    height: 100vh;
    height: 100dvh;
    max-height: 100vh;
    max-height: 100dvh;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);
    display: flex;
    flex-direction: column;
    overflow: hidden;
    padding-top: env(safe-area-inset-top, 0px);
  }

  .layout-sidebar-inner {
    flex: 1;
    min-height: 0;
    overflow-y: auto;
    overflow-x: hidden;
    -webkit-overflow-scrolling: touch;
    touch-action: pan-y;
    overscroll-behavior: contain;
  }

  .layout-sidebar--open {
    transform: translateX(0);
  }

  /* При открытом меню блокируем скролл основной области (только фон) */
  .layout--sidebar-visible {
    overflow: hidden;
    height: 100vh;
  }

  .layout--sidebar-visible .layout-main {
    overflow: hidden;
  }

  .layout-sidebar-close {
    display: flex;
  }
}
</style>
