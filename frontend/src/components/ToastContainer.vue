<script setup lang="ts">
import { useToast } from '@/composables/useToast'

const { toasts, dismiss } = useToast()
</script>

<template>
  <Teleport to="body">
    <div class="toast-container" aria-live="polite">
      <TransitionGroup name="toast" tag="div" class="toast-list">
        <div
          v-for="t in toasts"
          :key="t.id"
          class="toast"
          @mouseenter="($event.currentTarget as HTMLElement).classList.add('toast--hover')"
          @mouseleave="($event.currentTarget as HTMLElement).classList.remove('toast--hover')"
        >
          <div class="toast-body">
            <p class="toast-message">{{ t.message }}</p>
            <button
              type="button"
              class="toast-close"
              aria-label="Закрыть"
              @click="dismiss(t.id)"
            >
              ×
            </button>
          </div>
          <div class="toast-progress-wrap">
            <div class="toast-progress-bar" :style="{ width: `${100 - t.progress}%` }" />
          </div>
        </div>
      </TransitionGroup>
    </div>
  </Teleport>
</template>

<style scoped>
.toast-container {
  position: fixed;
  bottom: 0;
  right: 0;
  z-index: 9999;
  padding: 1.25rem;
  padding-bottom: calc(1.25rem + env(safe-area-inset-bottom, 0px));
  padding-right: calc(1.25rem + env(safe-area-inset-right, 0px));
  max-width: 100%;
  pointer-events: none;
}

.toast-list {
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
  align-items: flex-end;
  pointer-events: auto;
}

.toast {
  position: relative;
  display: flex;
  flex-direction: column;
  min-width: 320px;
  max-width: 420px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-strong);
  border-radius: 8px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  overflow: hidden;
  pointer-events: auto;
}

.toast-body {
  position: relative;
  flex: 1;
  padding: 1rem 2.5rem 1.25rem 1.25rem;
}

.toast-message {
  margin: 0;
  font-size: 1rem;
  line-height: 1.45;
  color: var(--color-text);
}

.toast-close {
  position: absolute;
  top: 50%;
  right: 0.75rem;
  transform: translateY(-50%);
  width: 2rem;
  height: 2rem;
  padding: 0;
  font-size: 1.35rem;
  line-height: 1;
  color: var(--color-text-muted);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  opacity: 0;
  transition: opacity 0.2s, color 0.2s, background 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toast--hover .toast-close {
  opacity: 1;
}

.toast-close:hover {
  color: var(--color-text);
  background: var(--color-surface-hover);
}

.toast-progress-wrap {
  flex-shrink: 0;
  height: 4px;
  background: var(--color-background-muted);
  overflow: hidden;
}

.toast-progress-bar {
  height: 100%;
  margin-left: auto;
  background: #5865f2;
  transition: width 0.05s linear;
}

.toast-enter-active,
.toast-leave-active {
  transition: opacity 0.3s ease, transform 0.3s ease;
}

.toast-enter-from,
.toast-leave-to {
  opacity: 0;
  transform: translateX(100%);
}

.toast-move {
  transition: transform 0.3s ease;
}
</style>
