import type {
  GuildConfigOut,
  GuildConfigUpdate,
  UserLevelOut,
  UserLevelUpdate,
} from './guilds.types'
import { apiJson } from './client'

export async function fetchGuilds() {
  return apiJson<import('./guilds.types').GuildOut[]>('/api/guilds')
}

export async function fetchGuildChannels(guildId: string) {
  return apiJson<import('./guilds.types').ChannelOut[]>(`/api/guilds/${guildId}/channels`)
}

export async function fetchGuildRoles(guildId: string) {
  return apiJson<import('./guilds.types').RoleOut[]>(`/api/guilds/${guildId}/roles`)
}

export async function fetchGuildConfig(guildId: string) {
  return apiJson<GuildConfigOut>(`/api/guilds/${guildId}/config`)
}

export async function updateGuildConfig(guildId: string, payload: GuildConfigUpdate) {
  return apiJson<GuildConfigOut>(`/api/guilds/${guildId}/config`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}

export async function fetchGuildUsersCount(guildId: string) {
  const res = await apiJson<{ count: number }>(`/api/guilds/${guildId}/users/count`)
  return res.count
}

export async function fetchGuildUsers(
  guildId: string,
  params: { offset?: number; limit?: number; order_by?: string; order?: string } = {}
) {
  const sp = new URLSearchParams()
  if (params.offset != null) sp.set('offset', String(params.offset))
  if (params.limit != null) sp.set('limit', String(params.limit))
  if (params.order_by) sp.set('order_by', params.order_by)
  if (params.order) sp.set('order', params.order)
  const q = sp.toString()
  return apiJson<UserLevelOut[]>(`/api/guilds/${guildId}/users${q ? `?${q}` : ''}`)
}

export async function updateUserLevel(
  guildId: string,
  userId: string,
  payload: UserLevelUpdate
) {
  return apiJson<UserLevelOut>(`/api/guilds/${guildId}/users/${userId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
}
