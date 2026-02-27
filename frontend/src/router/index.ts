import { createRouter, createWebHistory } from 'vue-router'
import { TOKEN_KEY } from '@/api/auth'
import AuthView from '@/components/AuthView.vue'
import DashboardPlaceholder from '@/views/DashboardPlaceholder.vue'
import DashboardShell from '@/views/DashboardShell.vue'
import DashboardView from '@/views/DashboardView.vue'
import SettingsView from '@/views/SettingsView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/login',
      name: 'login',
      component: AuthView,
      meta: { title: 'Вход — Witrix Bot', guest: true },
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
          meta: { title: 'Панель — Witrix Bot' },
        },
        {
          path: 'servers',
          name: 'dashboard-servers',
          component: DashboardPlaceholder,
          meta: { title: 'Серверы — Witrix Bot' },
        },
        {
          path: 'settings',
          name: 'dashboard-settings',
          component: SettingsView,
          meta: { title: 'Настройки — Witrix Bot' },
        },
      ],
    },
    {
      path: '/',
      redirect: '/dashboard',
    },
  ],
})

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
})

router.afterEach((to) => {
  document.title = (to.meta.title as string) ?? 'Witrix Bot'
})

export default router
