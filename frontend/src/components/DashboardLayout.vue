<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '@/composables/useAuth'
import { useGuild } from '@/composables/useGuild'

const { logout } = useAuth()
const { guilds, selectedGuildId, setSelectedGuildId, loadGuilds } = useGuild()
const route = useRoute()
const sidebarOpen = ref(false)
const accountOpen = ref(false)

const navItems = [
  { path: '/dashboard', label: 'Панель управления', icon: 'dashboard' },
  { path: '/dashboard/servers', label: 'Серверы', icon: 'servers' },
  { path: '/dashboard/settings', label: 'Настройки', icon: 'settings' },
]

function closeSidebar() {
  sidebarOpen.value = false
  accountOpen.value = false
}

function handleLogout() {
  accountOpen.value = false
  closeSidebar()
  logout()
}

onMounted(() => {
  loadGuilds()
})
watch(() => route.path, closeSidebar)
</script>

<template>
  <div class="layout" :class="{ 'layout--sidebar-visible': sidebarOpen }">
    <div class="layout-backdrop" aria-hidden="true" @click="closeSidebar" />

    <!-- Сайдбар слева -->
    <aside class="layout-sidebar" :class="{ 'layout-sidebar--open': sidebarOpen }">
      <div class="layout-sidebar-inner">
        <div class="layout-sidebar-head">
          <span class="layout-sidebar-logo">W</span>
          <span class="layout-sidebar-brand">Witrix Bot</span>
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
          <router-link
            v-for="item in navItems"
            :key="item.path"
            :to="item.path"
            class="layout-nav-item"
            :class="{ 'layout-nav-item--active': route.path === item.path }"
          >
            <span class="layout-nav-icon">
              <template v-if="item.icon === 'dashboard'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="9"/><rect x="14" y="3" width="7" height="5"/><rect x="14" y="12" width="7" height="9"/><rect x="3" y="16" width="7" height="5"/></svg>
              </template>
              <template v-else-if="item.icon === 'servers'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><ellipse cx="12" cy="5" rx="9" ry="3"/><path d="M3 5v14c0 1.66 4 3 9 3s9-1.34 9-3V5"/><path d="M3 12c0 1.66 4 3 9 3s9-1.34 9-3"/></svg>
              </template>
              <template v-else-if="item.icon === 'settings'">
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="3"/><path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1 0 2.83 2 2 0 0 1-2.83 0l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-2 2 2 2 0 0 1-2-2v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83 0 2 2 0 0 1 0-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1-2-2 2 2 0 0 1 2-2h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 0-2.83 2 2 0 0 1 2.83 0l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 2-2 2 2 0 0 1 2 2v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 0 2 2 0 0 1 0 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 2 2 2 2 0 0 1-2 2h-.09a1.65 1.65 0 0 0-1.51 1z"/></svg>
              </template>
            </span>
            <span class="layout-nav-label">{{ item.label }}</span>
          </router-link>
        </nav>
        <div class="layout-sidebar-footer">
          <div class="layout-account">
            <button
              type="button"
              class="layout-account-trigger"
              :class="{ 'layout-account-trigger--open': accountOpen }"
              @click="accountOpen = !accountOpen"
            >
              <span class="layout-account-avatar">U</span>
              <span class="layout-account-name">Аккаунт</span>
              <span class="layout-account-status">Online</span>
              <svg class="layout-account-chevron" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
            </button>
            <Transition name="dropdown">
              <div v-if="accountOpen" class="layout-account-dropdown">
                <button type="button" class="layout-account-item layout-account-item--logout" @click="handleLogout">
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
          <span class="layout-burger-line" />
          <span class="layout-burger-line" />
          <span class="layout-burger-line" />
        </button>
        <h1 class="layout-page-title"><slot name="title">Панель</slot></h1>
        <div class="layout-server">
          <select
            :value="selectedGuildId ?? ''"
            class="layout-server-select"
            @change="(e) => setSelectedGuildId(Number((e.target as HTMLSelectElement).value))"
          >
            <option v-for="g in guilds" :key="g.id" :value="g.id">{{ g.name }}</option>
            <option v-if="!guilds.length" value="" disabled>Нет серверов</option>
          </select>
          <span class="layout-server-label">Сервер</span>
        </div>
      </header>
      <main class="layout-content">
        <slot />
      </main>
    </div>
  </div>
</template>

<style scoped>
.layout {
  min-height: 100vh;
  display: flex;
  position: relative;
}

.layout-backdrop {
  display: none;
  position: fixed;
  inset: 0;
  z-index: 40;
  background: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
  opacity: 0;
  transition: opacity 0.25s ease;
}

.layout--sidebar-visible .layout-backdrop {
  display: block;
  opacity: 1;
}

/* Сайдбар слева */
.layout-sidebar {
  width: 260px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(18, 20, 26, 0.98);
  backdrop-filter: blur(12px);
}

.layout-sidebar-inner {
  display: flex;
  flex-direction: column;
  min-height: 100%;
  padding: 1rem 0;
}

.layout-sidebar-head {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0 1.25rem 1rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
}

.layout-sidebar-logo {
  width: 36px;
  height: 36px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.125rem;
  font-weight: 700;
  color: #fff;
  background: linear-gradient(135deg, #5865f2, #7289da);
  border-radius: 10px;
}

.layout-sidebar-brand {
  font-size: 1rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
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
  background: rgba(255, 255, 255, 0.06);
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
  background: rgba(255, 255, 255, 0.06);
}

.layout-nav-item--active {
  color: #22c55e;
  background: rgba(34, 197, 94, 0.12);
}

.layout-nav-item--active .layout-nav-icon {
  color: #22c55e;
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
  padding: 0.75rem 0.75rem 0;
  border-top: 1px solid rgba(255, 255, 255, 0.06);
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
  background: rgba(255, 255, 255, 0.06);
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
  background: rgba(24, 26, 32, 0.98);
  border: 1px solid rgba(255, 255, 255, 0.08);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.4);
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
  background: rgba(255, 255, 255, 0.06);
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

/* Основная область */
.layout-main {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  min-height: 100vh;
  position: relative;
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
  background-image:
    linear-gradient(rgba(255, 255, 255, 0.02) 1px, transparent 1px),
    linear-gradient(90deg, rgba(255, 255, 255, 0.02) 1px, transparent 1px);
  background-size: 64px 64px;
}

.layout-header {
  position: sticky;
  top: 0;
  z-index: 10;
  display: flex;
  align-items: center;
  gap: 1rem;
  padding: 0.875rem 1.25rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.06);
  background: rgba(13, 15, 20, 0.9);
  backdrop-filter: blur(12px);
}

.layout-burger {
  display: none;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  align-items: center;
  justify-content: center;
  padding: 0;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  color: var(--color-text);
  cursor: pointer;
}

.layout-burger:hover {
  background: rgba(255, 255, 255, 0.1);
}

.layout-burger-line {
  position: absolute;
  width: 18px;
  height: 2px;
  background: currentColor;
  border-radius: 1px;
}

.layout-burger-line:nth-child(1) { top: 13px; }
.layout-burger-line:nth-child(2) { top: 19px; }
.layout-burger-line:nth-child(3) { bottom: 13px; }

.layout-burger {
  position: relative;
}

.layout-page-title {
  flex: 1;
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
  letter-spacing: -0.02em;
  color: var(--color-text);
}

.layout-server {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 2px;
}

.layout-server-select {
  padding: 0.4rem 0.75rem;
  font-size: 0.875rem;
  font-family: inherit;
  color: var(--color-text);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  min-width: 140px;
}

.layout-server-select:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.14);
}

.layout-server-label {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.layout-content {
  flex: 1;
  position: relative;
  z-index: 1;
  padding: 1.5rem;
}

/* Мобильная: сайдбар выезжает слева */
@media (max-width: 1023px) {
  .layout-burger {
    display: flex;
  }

  .layout-sidebar {
    position: fixed;
    top: 0;
    left: 0;
    bottom: 0;
    z-index: 50;
    width: 280px;
    max-width: 85vw;
    transform: translateX(-100%);
    transition: transform 0.3s cubic-bezier(0.22, 1, 0.36, 1);
    box-shadow: 8px 0 32px rgba(0, 0, 0, 0.3);
  }

  .layout-sidebar--open {
    transform: translateX(0);
  }

  .layout-sidebar-close {
    display: flex;
  }
}
</style>
