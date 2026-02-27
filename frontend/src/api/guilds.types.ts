export interface GuildOut {
  id: number
  name: string
  icon: string | null
}

export interface ChannelOut {
  id: number
  name: string
  type: number
}

export interface RoleOut {
  id: number
  name: string
}

export interface GuildConfigOut {
  guild_id: number
  welcome_channel_id: number | null
  welcome_role_id: number | null
  level_channel_id: number | null
  role_select_channel_id: number | null
  selectable_roles: number[]
}

export interface GuildConfigUpdate {
  welcome_channel_id?: number | null
  welcome_role_id?: number | null
  level_channel_id?: number | null
  role_select_channel_id?: number | null
  selectable_roles?: number[] | null
}
