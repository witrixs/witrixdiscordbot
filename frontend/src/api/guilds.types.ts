export interface GuildOut {
  id: string
  name: string
  icon: string | null
}

export interface ChannelOut {
  id: string
  name: string
  type: number
}

export interface RoleOut {
  id: string
  name: string
}

export interface GuildConfigOut {
  guild_id: string
  welcome_channel_id: string | null
  welcome_role_id: string | null
  level_channel_id: string | null
  role_select_channel_id: string | null
  selectable_roles: string[]
}

export interface GuildConfigUpdate {
  welcome_channel_id?: string | null
  welcome_role_id?: string | null
  level_channel_id?: string | null
  role_select_channel_id?: string | null
  selectable_roles?: string[] | null
}

export interface UserLevelOut {
  guild_id: string
  user_id: string
  message_count: number
  level: number
  xp: number
  days_on_server: number
  display_name?: string | null
  avatar_url?: string | null
}

export interface UserLevelUpdate {
  message_count?: number
  level?: number
  xp?: number
  days_on_server?: number
}
