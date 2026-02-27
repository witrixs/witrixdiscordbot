<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'
import { useGuild } from '@/composables/useGuild'
import {
  fetchGuildConfig,
  fetchGuildChannels,
  fetchGuildRoles,
  updateGuildConfig,
} from '@/api/guilds'
import type { GuildConfigOut } from '@/api/guilds.types'
import AppLoader from '@/components/AppLoader.vue'

const { selectedGuildId } = useGuild()
const loading = ref(true)
const saving = ref(false)
const error = ref('')
const config = ref<GuildConfigOut | null>(null)
const channels = ref<{ id: number; name: string; type: number }[]>([])
const roles = ref<{ id: number; name: string }[]>([])

const form = ref({
  welcome_channel_id: null as number | null,
  welcome_role_id: null as number | null,
  level_channel_id: null as number | null,
  role_select_channel_id: null as number | null,
  selectable_roles: [] as number[],
})

async function load() {
  if (selectedGuildId.value == null) {
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
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка загрузки'
  } finally {
    loading.value = false
  }
}

async function save() {
  if (selectedGuildId.value == null) return
  saving.value = true
  error.value = ''
  try {
    config.value = await updateGuildConfig(selectedGuildId.value, {
      welcome_channel_id: form.value.welcome_channel_id,
      welcome_role_id: form.value.welcome_role_id,
      level_channel_id: form.value.level_channel_id,
      role_select_channel_id: form.value.role_select_channel_id,
      selectable_roles: form.value.selectable_roles,
    })
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Ошибка сохранения'
  } finally {
    saving.value = false
  }
}

function toggleRole(id: number) {
  const idx = form.value.selectable_roles.indexOf(id)
  if (idx >= 0) {
    form.value.selectable_roles = form.value.selectable_roles.filter((r) => r !== id)
  } else {
    form.value.selectable_roles = [...form.value.selectable_roles, id]
  }
}

watch(selectedGuildId, load)
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

      <div v-else class="settings-form">
        <section class="settings-section">
          <h2 class="settings-section-title">Приветствие</h2>
          <div class="settings-field">
            <label>Канал приветствия</label>
            <select v-model="form.welcome_channel_id" class="settings-select">
              <option :value="null">— Не выбран —</option>
              <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="settings-field">
            <label>Роль при входе</label>
            <select v-model="form.welcome_role_id" class="settings-select">
              <option :value="null">— Не выбрана —</option>
              <option v-for="r in roles" :key="r.id" :value="r.id">{{ r.name }}</option>
            </select>
          </div>
        </section>

        <section class="settings-section">
          <h2 class="settings-section-title">Уровни</h2>
          <div class="settings-field">
            <label>Канал объявлений об уровне</label>
            <select v-model="form.level_channel_id" class="settings-select">
              <option :value="null">— Не выбран —</option>
              <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
        </section>

        <section class="settings-section">
          <h2 class="settings-section-title">Выбор ролей</h2>
          <div class="settings-field">
            <label>Канал выбора ролей</label>
            <select v-model="form.role_select_channel_id" class="settings-select">
              <option :value="null">— Не выбран —</option>
              <option v-for="c in channels" :key="c.id" :value="c.id">{{ c.name }}</option>
            </select>
          </div>
          <div class="settings-field">
            <label>Роли, которые можно выбрать</label>
            <div class="settings-roles">
              <label
                v-for="r in roles"
                :key="r.id"
                class="settings-role-chip"
                :class="{ 'settings-role-chip--on': form.selectable_roles.includes(r.id) }"
              >
                <input
                  type="checkbox"
                  :checked="form.selectable_roles.includes(r.id)"
                  @change="toggleRole(r.id)"
                />
                <span>{{ r.name }}</span>
              </label>
            </div>
          </div>
        </section>

        <div class="settings-actions">
          <button type="button" class="settings-save" :disabled="saving" @click="save">
            {{ saving ? 'Сохранение…' : 'Сохранить' }}
          </button>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.settings {
  max-width: 560px;
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

.settings-section {
  margin-bottom: 1.5rem;
}

.settings-section-title {
  margin: 0 0 0.75rem;
  font-size: 1rem;
  font-weight: 600;
  color: var(--color-text);
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

.settings-select {
  width: 100%;
  max-width: 320px;
  padding: 0.5rem 0.75rem;
  font-size: 0.9375rem;
  font-family: inherit;
  color: var(--color-text);
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}

.settings-select:hover {
  background: rgba(255, 255, 255, 0.08);
  border-color: rgba(255, 255, 255, 0.14);
}

.settings-roles {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.settings-role-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.375rem;
  padding: 0.375rem 0.75rem;
  font-size: 0.875rem;
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 8px;
  cursor: pointer;
  transition: background 0.2s, border-color 0.2s;
}

.settings-role-chip:hover {
  background: rgba(255, 255, 255, 0.08);
}

.settings-role-chip--on {
  background: rgba(34, 197, 94, 0.15);
  border-color: rgba(34, 197, 94, 0.3);
  color: #22c55e;
}

.settings-role-chip input {
  margin: 0;
}

.settings-actions {
  margin-top: 1.5rem;
}

.settings-save {
  padding: 0.625rem 1.25rem;
  font-size: 0.9375rem;
  font-weight: 600;
  font-family: inherit;
  color: #fff;
  background: linear-gradient(135deg, #5865f2, #4752c4);
  border: none;
  border-radius: 10px;
  cursor: pointer;
  transition: opacity 0.2s;
}

.settings-save:hover:not(:disabled) {
  opacity: 0.95;
}

.settings-save:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}
</style>
