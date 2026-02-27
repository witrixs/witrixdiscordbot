import { ref, watch, onMounted } from 'vue'

const STORAGE_KEY = 'witrix-theme'

export type ThemeMode = 'light' | 'dark'

function getStoredTheme(): ThemeMode | null {
  try {
    const v = localStorage.getItem(STORAGE_KEY)
    if (v === 'light' || v === 'dark') return v
  } catch {
    /* ignore */
  }
  return null
}

function getSystemDark(): boolean {
  if (typeof window === 'undefined' || !window.matchMedia) return true
  return window.matchMedia('(prefers-color-scheme: dark)').matches
}

function applyTheme(mode: ThemeMode | null) {
  const html = document.documentElement
  if (mode) {
    html.setAttribute('data-theme', mode)
  } else {
    html.removeAttribute('data-theme')
  }
  const meta = document.querySelector('meta[name="theme-color"]')
  if (meta) {
    meta.setAttribute('content', mode === 'light' ? '#eef1f6' : '#0d0f14')
  }
}

const theme = ref<ThemeMode | null>(getStoredTheme())

function getEffectiveTheme(): ThemeMode {
  const t = theme.value
  if (t) return t
  return getSystemDark() ? 'dark' : 'light'
}

/** Текущая эффективная тема (выбранная или системная) */
const effectiveTheme = ref<ThemeMode>(getEffectiveTheme())

export function useTheme() {
  function setTheme(mode: ThemeMode) {
    theme.value = mode
    effectiveTheme.value = mode
    try {
      localStorage.setItem(STORAGE_KEY, mode)
    } catch {
      /* ignore */
    }
    applyTheme(mode)
  }

  onMounted(() => {
    applyTheme(theme.value)
    effectiveTheme.value = getEffectiveTheme()
    const mq = window.matchMedia('(prefers-color-scheme: dark)')
    function updateEffective() {
      if (!theme.value) effectiveTheme.value = mq.matches ? 'dark' : 'light'
    }
    mq.addEventListener('change', updateEffective)
  })

  watch(theme, (v) => {
    effectiveTheme.value = v ?? (getSystemDark() ? 'dark' : 'light')
  })

  return { theme, effectiveTheme, setTheme }
}

/** Вызвать до монтирования приложения, чтобы не было мигания темы */
export function initTheme() {
  const stored = getStoredTheme()
  applyTheme(stored)
}
