<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import type { GuildOut } from '@/api/guilds.types'

const props = withDefaults(
  defineProps<{
    modelValue: string | null
    guilds: GuildOut[]
    placeholder?: string
    disabled?: boolean
  }>(),
  { placeholder: 'Нет серверов', disabled: false }
)

const emit = defineEmits<{ 'update:modelValue': [value: string | null] }>()

const open = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)
const dropdownStyle = ref({ top: '0px', left: '0px', width: '200px' })

const selectedGuild = computed(() =>
  props.modelValue ? props.guilds.find((g) => g.id === props.modelValue) ?? null : null
)

function updateDropdownPosition() {
  nextTick(() => {
    const trigger = triggerRef.value
    if (!trigger || !open.value) return
    const rect = trigger.getBoundingClientRect()
    const maxH = 240
    const gap = 4
    const spaceBelow = window.innerHeight - rect.bottom
    const openDown = spaceBelow >= maxH + gap || rect.top >= window.innerHeight / 2
    const top = openDown ? rect.bottom + gap : rect.top - maxH - gap
    dropdownStyle.value = {
      top: `${Math.max(8, top)}px`,
      left: `${rect.left}px`,
      width: `${rect.width}px`,
    }
  })
}

function toggle() {
  if (props.disabled) return
  open.value = !open.value
  if (open.value) updateDropdownPosition()
}

function select(guild: GuildOut | null) {
  emit('update:modelValue', guild?.id ?? null)
  open.value = false
}

function handleClickOutside(e: MouseEvent) {
  const el = e.target as Node
  if (triggerRef.value?.contains(el) || listRef.value?.contains(el)) return
  open.value = false
}

function closeOnScroll(e: Event) {
  const target = e.target as Node
  if (listRef.value?.contains(target)) return
  open.value = false
}

watch(open, (isOpen) => {
  if (isOpen) {
    updateDropdownPosition()
    document.addEventListener('scroll', closeOnScroll, true)
  } else {
    document.removeEventListener('scroll', closeOnScroll, true)
  }
})

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('scroll', closeOnScroll, true)
})
</script>

<template>
  <div class="server-select" :class="{ 'server-select--open': open, 'server-select--disabled': disabled }">
    <button
      ref="triggerRef"
      type="button"
      class="server-select-trigger"
      :disabled="disabled"
      aria-haspopup="listbox"
      :aria-expanded="open"
      @click="toggle"
    >
      <span class="server-select-avatar-wrap">
        <img
          v-if="selectedGuild?.icon"
          :src="selectedGuild.icon"
          :alt="selectedGuild.name"
          class="server-select-avatar-img"
        />
        <span v-else class="server-select-avatar-placeholder">
          {{ selectedGuild ? selectedGuild.name.charAt(0).toUpperCase() : '?' }}
        </span>
      </span>
      <span class="server-select-text">
        <span class="server-select-name-wrap">
          <span class="server-select-diamond" aria-hidden="true">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
          </span>
          <span class="server-select-name">{{ selectedGuild?.name ?? placeholder }}</span>
          <span class="server-select-diamond" aria-hidden="true">
            <svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
          </span>
        </span>
        <span class="server-select-label">Сервер</span>
      </span>
      <span class="server-select-chevron" aria-hidden="true">
        <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="6 9 12 15 18 9"/></svg>
      </span>
    </button>
    <Teleport to="body">
      <Transition name="server-drop">
        <div
          v-show="open"
          ref="listRef"
          class="server-select-dropdown"
          role="listbox"
          tabindex="-1"
          :style="dropdownStyle"
        >
          <button
            v-for="g in guilds"
            :key="g.id"
            type="button"
            role="option"
            class="server-select-option"
            :class="{ 'server-select-option--selected': g.id === modelValue }"
            :aria-selected="g.id === modelValue"
            @click="select(g)"
          >
            <span class="server-select-option-avatar">
              <img
                v-if="g.icon"
                :src="g.icon"
                :alt="g.name"
                class="server-select-option-avatar-img"
              />
              <span v-else class="server-select-option-avatar-ph">{{ g.name.charAt(0).toUpperCase() }}</span>
            </span>
            <span class="server-select-option-name-wrap">
              <span class="server-select-option-diamond" aria-hidden="true">
                <svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
              </span>
              <span class="server-select-option-name">{{ g.name }}</span>
              <span class="server-select-option-diamond" aria-hidden="true">
                <svg width="8" height="8" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2L15 9L22 12L15 15L12 22L9 15L2 12L9 9L12 2Z"/></svg>
              </span>
            </span>
          </button>
          <p v-if="!guilds.length" class="server-select-empty">{{ placeholder }}</p>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.server-select {
  position: relative;
  width: 100%;
  min-width: 0;
}

.server-select-trigger {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  text-align: left;
  min-height: 44px;
  box-sizing: border-box;
}

.server-select-trigger:hover:not(:disabled) {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.server-select--open .server-select-trigger {
  border-color: rgba(88, 101, 242, 0.5);
  background: var(--color-bg-elevated);
}

.server-select-trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.server-select-avatar-wrap {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-input-bg);
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0;
}

.server-select-avatar-img,
.server-select-option-avatar-img {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
  vertical-align: middle;
}

.server-select-avatar-placeholder {
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text-muted);
  line-height: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.server-select-text {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  justify-content: center;
  gap: 0.125rem;
}

.server-select-name-wrap {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  min-width: 0;
}

.server-select-diamond {
  flex-shrink: 0;
  color: #5b8def;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
}

.server-select-name {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.server-select-label {
  font-size: 0.6875rem;
  color: var(--color-text-muted);
}

.server-select-chevron {
  flex-shrink: 0;
  color: var(--color-text-muted);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.2s;
}

.server-select--open .server-select-chevron {
  transform: rotate(180deg);
}

.server-select-dropdown {
  position: fixed;
  z-index: 9999;
  max-height: 240px;
  overflow-y: auto;
  padding: 4px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-strong);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
  box-sizing: border-box;
}

.server-select-option {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  width: 100%;
  padding: 0.5rem 0.625rem;
  font-family: inherit;
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text);
  background: transparent;
  border: none;
  border-radius: 10px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
  box-sizing: border-box;
  min-height: 44px;
}

.server-select-option:hover {
  background: var(--color-surface-hover);
}

.server-select-option--selected {
  color: #fff;
  background: rgba(88, 101, 242, 0.35);
  border: 1px solid rgba(88, 101, 242, 0.5);
}

.server-select-option-avatar {
  flex-shrink: 0;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  overflow: hidden;
  background: var(--color-input-bg);
  display: flex;
  align-items: center;
  justify-content: center;
}

.server-select-option-avatar-ph {
  font-size: 0.875rem;
  font-weight: 600;
  color: var(--color-text-muted);
  line-height: 1;
}

.server-select-option-name-wrap {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.35rem;
}

.server-select-option-diamond {
  flex-shrink: 0;
  color: #5b8def;
  display: flex;
  align-items: center;
  justify-content: center;
  line-height: 0;
}

.server-select-option-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

.server-select-empty {
  margin: 0;
  padding: 0.5rem 0.5rem;
  font-size: 0.8125rem;
  color: var(--color-text-muted);
}

/* Мобильная: как на референсе — только круглый аватар и стрелка в триггере */
@media (max-width: 768px) {
  .server-select-text {
    display: none;
  }

  .server-select-trigger {
    padding: 0.25rem;
    min-width: 60px;
    width: 60px;
    height: 60px;
    min-height: 60px;
    justify-content: center;
    gap: 0.375rem;
    border-radius: 12px;
  }

  .server-select-avatar-wrap {
    width: 32px;
    height: 32px;
    border-radius: 50%;
  }

  /* Выпадающий список на мобильном — во всю ширину, пункты как на скрине */
  .server-select-dropdown {
    left: 50% !important;
    transform: translateX(-50%);
    width: calc(100vw - 2rem) !important;
    max-width: 320px;
  }

  .server-select-option {
    min-height: 52px;
    padding: 0.625rem 0.75rem;
  }

  .server-select-option-avatar {
    width: 40px;
    height: 40px;
  }
}

.server-drop-enter-active,
.server-drop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.server-drop-enter-from,
.server-drop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
