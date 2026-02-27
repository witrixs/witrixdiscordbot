from typing import List, Optional

from pydantic import BaseModel, Field


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserMeOut(BaseModel):
    username: str
    auth_type: str = "admin"  # "admin" | "discord"
    avatar_url: Optional[str] = None
    is_discord_user: bool = False
    allowed_guild_ids: List[str] = Field(default_factory=list)  # сервера, где есть бот и пользователь
    admin_guild_ids: List[str] = Field(default_factory=list)   # сервера, где пользователь админ
    default_guild_id: Optional[str] = None  # выбранный по умолчанию сервер (для Discord)


class GuildOut(BaseModel):
    id: str  # Discord snowflake as string (JS safe)
    name: str
    icon: Optional[str] = None


class ChannelOut(BaseModel):
    id: str
    name: str
    type: int = 0


class RoleOut(BaseModel):
    id: str
    name: str


class GuildConfigOut(BaseModel):
    guild_id: str
    welcome_channel_id: Optional[str] = None
    welcome_role_id: Optional[str] = None
    level_channel_id: Optional[str] = None
    role_select_channel_id: Optional[str] = None
    selectable_roles: List[str] = Field(default_factory=list)


class GuildConfigUpdate(BaseModel):
    welcome_channel_id: Optional[str] = None
    welcome_role_id: Optional[str] = None
    level_channel_id: Optional[str] = None
    role_select_channel_id: Optional[str] = None
    selectable_roles: Optional[List[str]] = None


class UserLevelOut(BaseModel):
    guild_id: str
    user_id: str
    message_count: int
    level: int
    xp: int
    days_on_server: int
    display_name: Optional[str] = None
    avatar_url: Optional[str] = None


class UserLevelUpdate(BaseModel):
    message_count: Optional[int] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    days_on_server: Optional[int] = None


class DefaultGuildUpdate(BaseModel):
    guild_id: Optional[str] = None  # null = сброс

