import { ref, computed } from 'vue'
import type { GuildOut } from '@/api/guilds.types'
import { fetchGuilds } from '@/api/guilds'

const STORAGE_KEY = 'witrix_selected_guild_id'

function getStoredGuildId(): number | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return null
    const n = parseInt(raw, 10)
    return Number.isFinite(n) ? n : null
  } catch {
    return null
  }
}

const guilds = ref<GuildOut[]>([])
const selectedId = ref<number | null>(getStoredGuildId())

export function useGuild() {
  const selectedGuild = computed(() => guilds.value.find((g) => g.id === selectedId.value) ?? null)

  function setSelectedGuildId(id: number | null) {
    selectedId.value = id
    if (id !== null) {
      localStorage.setItem(STORAGE_KEY, String(id))
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function loadGuilds() {
    try {
      guilds.value = await fetchGuilds()
      if (guilds.value.length && selectedId.value === null) {
        setSelectedGuildId(guilds.value[0].id)
      }
      if (selectedId.value !== null && !guilds.value.some((g) => g.id === selectedId.value)) {
        setSelectedGuildId(guilds.value[0]?.id ?? null)
      }
    } catch {
      guilds.value = []
    }
  }

  return {
    guilds,
    selectedGuildId: selectedId,
    selectedGuild,
    setSelectedGuildId,
    loadGuilds,
  }
}
