import { ref, computed } from 'vue'
import type { GuildOut } from '@/api/guilds.types'
import { fetchGuilds } from '@/api/guilds'

const STORAGE_KEY = 'witrix_selected_guild_id'

function getStoredGuildId(): string | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw || null
  } catch {
    return null
  }
}

const guilds = ref<GuildOut[]>([])
const selectedId = ref<string | null>(getStoredGuildId())

export function useGuild() {
  const selectedGuild = computed(() => guilds.value.find((g) => g.id === selectedId.value) ?? null)

  function setSelectedGuildId(id: string | null) {
    selectedId.value = id
    if (id !== null) {
      localStorage.setItem(STORAGE_KEY, id)
    } else {
      localStorage.removeItem(STORAGE_KEY)
    }
  }

  async function loadGuilds() {
    try {
      guilds.value = await fetchGuilds()
      const firstGuild = guilds.value[0]
      if (firstGuild && selectedId.value === null) {
        setSelectedGuildId(firstGuild.id)
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
