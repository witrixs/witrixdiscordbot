import { shallowRef } from 'vue'

export interface ToastItem {
  id: number
  message: string
  progress: number
  createdAt: number
  duration: number
}

const toasts = shallowRef<ToastItem[]>([])
let nextId = 1
let tickInterval: ReturnType<typeof setInterval> | null = null
const TICK_MS = 50
const DEFAULT_DURATION = 4000

function tick() {
  const now = Date.now()
  toasts.value = toasts.value
    .map((t) => {
      const elapsed = now - t.createdAt
      const progress = Math.min(100, (elapsed / t.duration) * 100)
      return { ...t, progress }
    })
    .filter((t) => {
      const elapsed = now - t.createdAt
      return elapsed < t.duration
    })
  if (toasts.value.length === 0 && tickInterval) {
    clearInterval(tickInterval)
    tickInterval = null
  }
}

function ensureTick() {
  if (!tickInterval) {
    tickInterval = setInterval(tick, TICK_MS)
  }
}

export function useToast() {
  function toast(message: string, durationMs = DEFAULT_DURATION) {
    const id = nextId++
    const item: ToastItem = {
      id,
      message,
      progress: 0,
      createdAt: Date.now(),
      duration: durationMs,
    }
    toasts.value = [...toasts.value, item]
    ensureTick()
    return id
  }

  function dismiss(id: number) {
    toasts.value = toasts.value.filter((t) => t.id !== id)
  }

  return { toasts, toast, dismiss }
}
