<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'

export interface SelectOption {
  value: string | null
  label: string
}

const props = withDefaults(
  defineProps<{
    modelValue: string | null
    options: SelectOption[]
    placeholder?: string
    disabled?: boolean
  }>(),
  { placeholder: '— Не выбран —', disabled: false }
)

const emit = defineEmits<{ 'update:modelValue': [value: string | null] }>()

const open = ref(false)
const triggerRef = ref<HTMLElement | null>(null)
const listRef = ref<HTMLElement | null>(null)
const dropdownStyle = ref({ top: '0px', left: '0px', width: '200px' })

const selectedLabel = computed(() => {
  if (props.modelValue == null) return props.placeholder
  const opt = props.options.find((o) => o.value === props.modelValue)
  return opt?.label ?? props.placeholder
})

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

function select(option: SelectOption) {
  emit('update:modelValue', option.value)
  open.value = false
}

function handleClickOutside(e: MouseEvent) {
  const el = e.target as Node
  if (triggerRef.value?.contains(el) || listRef.value?.contains(el)) return
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

function closeOnScroll(e: Event) {
  const target = e.target as Node
  if (listRef.value?.contains(target)) return
  open.value = false
}

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
})
onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('scroll', closeOnScroll, true)
})
</script>

<template>
  <div class="app-select" :class="{ 'app-select--open': open, 'app-select--disabled': disabled }">
    <button
      ref="triggerRef"
      type="button"
      class="app-select-trigger"
      :disabled="disabled"
      aria-haspopup="listbox"
      :aria-expanded="open"
      @click="toggle"
    >
      <span class="app-select-value">{{ selectedLabel }}</span>
      <span class="app-select-chevron" aria-hidden="true">▼</span>
    </button>
    <Teleport to="body">
      <Transition name="select-drop">
        <div
          v-show="open"
          ref="listRef"
          class="app-select-dropdown app-select-dropdown--fixed"
          role="listbox"
          tabindex="-1"
          :style="dropdownStyle"
        >
          <button
            type="button"
            role="option"
            class="app-select-option"
            :class="{ 'app-select-option--selected': modelValue == null }"
            :aria-selected="modelValue == null"
            @click="select({ value: null, label: placeholder })"
          >
            {{ placeholder }}
          </button>
          <button
            v-for="opt in options"
            :key="opt.value ?? '_empty'"
            type="button"
            role="option"
            class="app-select-option"
            :class="{ 'app-select-option--selected': opt.value === modelValue }"
            :aria-selected="opt.value === modelValue"
            @click="select(opt)"
          >
            {{ opt.label }}
          </button>
        </div>
      </Transition>
    </Teleport>
  </div>
</template>

<style scoped>
.app-select {
  position: relative;
  width: 100%;
  max-width: 320px;
}

.app-select-trigger {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
  text-align: left;
}

.app-select-trigger:hover:not(:disabled) {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.app-select--open .app-select-trigger {
  border-color: rgba(88, 101, 242, 0.5);
  background: var(--color-bg-elevated);
}

.app-select-trigger:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.app-select-value {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.app-select-chevron {
  flex-shrink: 0;
  margin-left: 0.5rem;
  font-size: 0.625rem;
  color: var(--color-text-muted);
  transition: transform 0.2s;
}

.app-select--open .app-select-chevron {
  transform: rotate(180deg);
}

.app-select-dropdown {
  max-height: 240px;
  overflow-y: auto;
  padding: 4px;
  background: var(--color-bg-elevated);
  border: 1px solid var(--color-border-strong);
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.25);
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.app-select-dropdown--fixed {
  position: fixed;
  z-index: 9999;
  min-width: 120px;
}

.app-select-option {
  display: block;
  width: 100%;
  padding: 0.5rem 0.75rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text);
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  text-align: left;
  transition: background 0.15s;
}

.app-select-option:hover {
  background: var(--color-surface-hover);
}

.app-select-option--selected {
  color: #5865f2;
  background: rgba(88, 101, 242, 0.12);
}

.select-drop-enter-active,
.select-drop-leave-active {
  transition: opacity 0.15s ease, transform 0.15s ease;
}

.select-drop-enter-from,
.select-drop-leave-to {
  opacity: 0;
  transform: translateY(-4px);
}
</style>
