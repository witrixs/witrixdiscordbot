import type { GuildConfigOut, GuildConfigUpdate } from './guilds.types'
import { apiJson } from './client'

export async function fetchGuilds() {
  return apiJson<import('./guilds.types').GuildOut[]>('/api/guilds')
}

export async function fetchGuildChannels(guildId: number) {
  return apiJson<import('./guilds.types').ChannelOut[]>(`/api/guilds/${guildId}/channels`)
}

export async function fetchGuildRoles(guildId: number) {
  return apiJson<import('./guilds.types').RoleOut[]>(`/api/guilds/${guildId}/roles`)
}

export async function fetchGuildConfig(guildId: number) {
  return apiJson<GuildConfigOut>(`/api/guilds/${guildId}/config`)
}

export async function updateGuildConfig(guildId: number, payload: GuildConfigUpdate) {
  return apiJson<GuildConfigOut>(`/api/guilds/${guildId}/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
