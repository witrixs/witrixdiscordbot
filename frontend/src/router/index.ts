import { createRouter, createWebHistory } from 'vue-router'
import { TOKEN_KEY, getCachedUserMe } from '@/api/auth'
import AuthView from '@/components/AuthView.vue'
import AuthCallbackView from '@/views/AuthCallbackView.vue'
import DashboardShell from '@/views/DashboardShell.vue'
import DashboardView from '@/views/DashboardView.vue'
import SettingsView from '@/views/SettingsView.vue'
import UsersView from '@/views/UsersView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: AuthView,
      meta: { title: 'Вход // witrix Discord Bot', guest: true },
    },
    {
      path: '/auth/callback',
      name: 'auth-callback',
      component: AuthCallbackView,
      meta: { title: 'Вход…', guest: true },
    },
    {
      path: '/dashboard',
      component: DashboardShell,
      meta: { requiresAuth: true },
      children: [
        {
          path: '',
          name: 'dashboard',
          component: DashboardView,
          meta: { title: 'Панель // witrix Discord Bot' },
        },
        {
          path: 'users',
          name: 'dashboard-users',
          component: UsersView,
          meta: { title: 'Пользователи // witrix Discord Bot' },
        },
        {
          path: 'settings',
          name: 'dashboard-settings',
          component: SettingsView,
          meta: { title: 'Настройки // witrix Discord Bot' },
        },
      ],
    },
    {
      path: '/',
      redirect: '/dashboard',
    },
  ],
})

const routesRequireGuildAdmin = ['/dashboard/users', '/dashboard/settings']

router.beforeEach((to) => {
  const token = localStorage.getItem(TOKEN_KEY)

  // / без авторизации → /login, с авторизацией → /dashboard (без лишнего в URL)
  if (to.path === '/') {
    return token ? { path: '/dashboard' } : { path: '/login' }
  }

  const requiresAuth = to.matched.some((r) => r.meta.requiresAuth)
  const guestOnly = to.matched.some((r) => r.meta.guest)

  if (requiresAuth && !token) {
    return { path: '/login' }
  }
  if (guestOnly && token) {
    return { path: '/dashboard' }
  }

  // Discord без прав админа не может заходить в Пользователи и Настройки
  if (token && routesRequireGuildAdmin.includes(to.path)) {
    const cached = getCachedUserMe()
    if (cached?.is_discord_user && (cached.admin_guild_ids?.length ?? 0) === 0) {
      return { path: '/dashboard' }
    }
  }
})

router.afterEach((to) => {
  document.title = (to.meta.title as string) ?? 'Witrix Bot'
})

export default router
