<script setup lang="ts">
import { ref, watch, onMounted, computed } from 'vue'
import { useAuth } from '@/composables/useAuth'
import { useGuild } from '@/composables/useGuild'
import { useToast } from '@/composables/useToast'
import {
  fetchGuildConfig,
  fetchGuildChannels,
  fetchGuildRoles,
  updateGuildConfig,
} from '@/api/guilds'
import type { GuildConfigOut } from '@/api/guilds.types'
import AppLoader from '@/components/AppLoader.vue'
import AppSelect from '@/components/AppSelect.vue'
import type { SelectOption } from '@/components/AppSelect.vue'

const { hasGuildAdminAccess } = useAuth()
const { selectedGuildId } = useGuild()

const canEditSettings = computed(() => hasGuildAdminAccess.value)
const { toast } = useToast()
const loading = ref(true)
const error = ref('')
const skipNextSave = ref(false)
const config = ref<GuildConfigOut | null>(null)
const channels = ref<{ id: string; name: string; type: number }[]>([])
const roles = ref<{ id: string; name: string }[]>([])

const form = ref({
  welcome_channel_id: null as string | null,
  welcome_role_id: null as string | null,
  level_channel_id: null as string | null,
  role_select_channel_id: null as string | null,
  selectable_roles: [] as string[],
})

const channelOptions = computed<SelectOption[]>(() =>
  channels.value.map((c) => ({ value: c.id, label: c.name }))
)
const roleOptions = computed<SelectOption[]>(() =>
  roles.value.map((r) => ({ value: r.id, label: r.name }))
)

const sectionOpen = ref<Record<string, boolean>>({
  greeting: false,
  levels: false,
  roles: false,
})

function toggleSection(key: string) {
  sectionOpen.value[key] = !sectionOpen.value[key]
}

async function load() {
  if (selectedGuildId.value == null || !canEditSettings.value) {
    loading.value = false
    return
  }
  loading.value = true
  error.value = ''
  try {
    const [cfg, ch, rl] = await Promise.all([
      fetchGuildConfig(selectedGuildId.value),
      fetchGuildChannels(selectedGuildId.value),
      fetchGuildRoles(selectedGuildId.value),
    ])
    config.value = cfg
    channels.value = ch
    roles.value = rl
    form.value = {
      welcome_channel_id: cfg.welcome_channel_id ?? null,
      welcome_role_id: cfg.welcome_role_id ?? null,
      level_channel_id: cfg.level_channel_id ?? null,
      role_select_channel_id: cfg.role_select_channel_id ?? null,
      selectable_roles: [...(cfg.selectable_roles ?? [])],
    }
    skipNextSave.value = true
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

let saveTimeout: ReturnType<typeof setTimeout> | null = null
async function save() {
  if (selectedGuildId.value == null) return
  if (skipNextSave.value) {
    skipNextSave.value = false
    return
  }
  error.value = ''
  try {
    config.value = await updateGuildConfig(selectedGuildId.value, {
      welcome_channel_id: form.value.welcome_channel_id,
      welcome_role_id: form.value.welcome_role_id,
      level_channel_id: form.value.level_channel_id,
      role_select_channel_id: form.value.role_select_channel_id,
      selectable_roles: form.value.selectable_roles,
    })
    toast('Настройки сохранены')
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка сохранения'
  }
}

function scheduleSave() {
  if (saveTimeout) clearTimeout(saveTimeout)
  saveTimeout = setTimeout(save, 400)
}

function toggleRole(id: string) {
  const idx = form.value.selectable_roles.indexOf(id)
  if (idx >= 0) {
    form.value.selectable_roles = form.value.selectable_roles.filter((r) => r !== id)
  } else {
    form.value.selectable_roles = [...form.value.selectable_roles, id]
  }
  scheduleSave()
}

watch(selectedGuildId, load)
watch(form, () => scheduleSave(), { deep: true })
onMounted(load)
</script>

<template>
  <div class="settings">
    <div v-if="loading" class="settings-loading">
      <AppLoader size="lg" />
      <p>Загрузка настроек…</p>
    </div>

    <template v-else>
      <p v-if="error" class="settings-error">{{ error }}</p>
      <p v-if="selectedGuildId == null" class="settings-empty">Выберите сервер сверху.</p>
      <p v-else-if="!canEditSettings" class="settings-empty settings-no-access">
        Для доступа к настройкам нужны права администратора на сервере Discord.
      </p>

      <div v-else class="settings-form">
        <section class="settings-section settings-section--collapsible">
          <button
            type="button"
            class="settings-section-head"
            :class="{ 'settings-section-head--open': sectionOpen.greeting }"
            :aria-expanded="sectionOpen.greeting"
            @click="toggleSection('greeting')"
          >
            <span class="settings-section-title">Приветствие</span>
            <span class="settings-section-chevron" aria-hidden="true">▼</span>
          </button>
          <Transition name="section-body">
            <div v-show="sectionOpen.greeting" class="settings-section-body">
              <div class="settings-field">
                <label>Канал приветствия</label>
                <AppSelect
                  v-model="form.welcome_channel_id"
                  :options="channelOptions"
                  placeholder="— Не выбран —"
                />
              </div>
              <div class="settings-field">
                <label>Роль при входе</label>
                <AppSelect
                  v-model="form.welcome_role_id"
                  :options="roleOptions"
                  placeholder="— Не выбрана —"
                />
              </div>
            </div>
          </Transition>
        </section>

        <section class="settings-section settings-section--collapsible">
          <button
            type="button"
            class="settings-section-head"
            :class="{ 'settings-section-head--open': sectionOpen.levels }"
            :aria-expanded="sectionOpen.levels"
            @click="toggleSection('levels')"
          >
            <span class="settings-section-title">Уровни</span>
            <span class="settings-section-chevron" aria-hidden="true">▼</span>
          </button>
          <Transition name="section-body">
            <div v-show="sectionOpen.levels" class="settings-section-body">
              <div class="settings-field">
                <label>Канал объявлений об уровне</label>
                <AppSelect
                  v-model="form.level_channel_id"
                  :options="channelOptions"
                  placeholder="— Не выбран —"
                />
              </div>
            </div>
          </Transition>
        </section>

        <section class="settings-section settings-section--collapsible">
          <button
            type="button"
            class="settings-section-head"
            :class="{ 'settings-section-head--open': sectionOpen.roles }"
            :aria-expanded="sectionOpen.roles"
            @click="toggleSection('roles')"
          >
            <span class="settings-section-title">Выбор ролей</span>
            <span class="settings-section-chevron" aria-hidden="true">▼</span>
          </button>
          <Transition name="section-body">
            <div v-show="sectionOpen.roles" class="settings-section-body">
              <div class="settings-field">
                <label>Канал выбора ролей</label>
                <AppSelect
                  v-model="form.role_select_channel_id"
                  :options="channelOptions"
                  placeholder="— Не выбран —"
                />
              </div>
              <div class="settings-field">
                <label>Роли, которые можно выбрать</label>
                <p class="settings-roles-hint">Нажмите на роль, чтобы разрешить или запретить её выбор на сервере</p>
                <div class="settings-roles-wrap">
                  <div class="settings-roles">
                    <button
                      v-for="r in roles"
                      :key="r.id"
                      type="button"
                      class="settings-role-chip"
                      :class="{ 'settings-role-chip--on': form.selectable_roles.includes(r.id) }"
                      :aria-pressed="form.selectable_roles.includes(r.id)"
                      @click="toggleRole(r.id)"
                    >
                      <span class="settings-role-chip-text">{{ r.name }}</span>
                    </button>
                  </div>
                </div>
              </div>
            </div>
          </Transition>
        </section>
      </div>
    </template>
  </div>
</template>

<style scoped>
.settings {
  max-width: 560px;
  margin: 0 auto;
  padding: 0 0.5rem;
}

.settings-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 1rem;
  padding: 2rem 0;
}

.settings-loading p {
  margin: 0;
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.settings-error {
  padding: 0.75rem 1rem;
  margin: 0 0 1rem;
  font-size: 0.875rem;
  color: #f87171;
  background: rgba(248, 113, 113, 0.1);
  border: 1px solid rgba(248, 113, 113, 0.2);
  border-radius: 10px;
}

.settings-empty {
  font-size: 0.9375rem;
  color: var(--color-text-muted);
}

.settings-form {
  display: flex;
  flex-direction: column;
  align-items: center;
}

/* Collapsible section */
.settings-section {
  width: 100%;
  margin-bottom: 0.75rem;
  background: var(--color-surface);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  overflow: hidden;
  backdrop-filter: blur(12px);
  -webkit-backdrop-filter: blur(12px);
}

.settings-section-head {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  padding: 0.875rem 1rem;
  font-family: inherit;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
  background: transparent;
  border: none;
  cursor: pointer;
  transition: background 0.2s;
  text-align: left;
}

.settings-section-head:hover {
  background: var(--color-surface-hover);
}

.settings-section-chevron {
  flex-shrink: 0;
  font-size: 0.625rem;
  color: var(--color-text-muted);
  transition: transform 0.25s ease;
}

.settings-section-head--open .settings-section-chevron {
  transform: rotate(180deg);
}

.settings-section-body {
  padding: 0 1rem 1rem;
}

.settings-section-body .settings-field:last-child {
  margin-bottom: 0;
}

/* Vue transition for section body: height is auto, use opacity + slight slide */
.section-body-enter-active,
.section-body-leave-active {
  transition: opacity 0.25s ease, transform 0.25s ease;
}

.section-body-enter-from,
.section-body-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.settings-section-title {
  margin: 0;
}

.settings-field {
  margin-bottom: 1rem;
}

.settings-field label {
  display: block;
  margin-bottom: 0.375rem;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text-muted);
}

.settings-field :deep(.app-select) {
  max-width: 100%;
}

/* Roles: ровная сетка без галочек, адаптивно */
.settings-roles-hint {
  margin: 0 0 0.5rem;
  font-size: 0.75rem;
  color: var(--color-text-muted);
  opacity: 0.9;
}

.settings-roles-wrap {
  max-height: 220px;
  overflow-y: auto;
  padding: 0.5rem;
  border-radius: 12px;
  background: var(--color-background-muted);
  border: 1px solid var(--color-border);
}

.settings-roles {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
  gap: 0.5rem;
}

.settings-role-chip {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 40px;
  padding: 0.5rem 0.75rem;
  font-family: inherit;
  font-size: 0.8125rem;
  font-weight: 500;
  color: var(--color-text);
  background: var(--color-input-bg);
  border: 1px solid var(--color-input-border);
  border-radius: 10px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s, color 0.2s, transform 0.1s;
  text-align: center;
}

.settings-role-chip:hover {
  background: var(--color-surface-hover);
  border-color: var(--color-border-strong);
}

.settings-role-chip:active {
  transform: scale(0.98);
}

.settings-role-chip--on {
  background: rgba(34, 197, 94, 0.14);
  border-color: rgba(34, 197, 94, 0.35);
  color: #22c55e;
}

.settings-role-chip--on:hover {
  background: rgba(34, 197, 94, 0.2);
  border-color: rgba(34, 197, 94, 0.45);
}

.settings-role-chip-text {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 100%;
}

/* Адаптив: на узких экранах меньше колонок, ровные ячейки */
@media (max-width: 480px) {
  .settings-roles {
    grid-template-columns: 1fr;
    gap: 0.5rem;
  }

  .settings-role-chip {
    min-height: 44px;
    padding: 0.625rem 0.875rem;
    font-size: 0.875rem;
  }
}

@media (min-width: 481px) and (max-width: 600px) {
  .settings-roles {
    grid-template-columns: repeat(2, 1fr);
  }
}
</style>
