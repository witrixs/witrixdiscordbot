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


class GuildOut(BaseModel):
    id: int
    name: str
    icon: Optional[str] = None


class ChannelOut(BaseModel):
    id: int
    name: str
    type: int = 0


class RoleOut(BaseModel):
    id: int
    name: str


class GuildConfigOut(BaseModel):
    guild_id: int
    welcome_channel_id: Optional[int] = None
    welcome_role_id: Optional[int] = None
    level_channel_id: Optional[int] = None
    role_select_channel_id: Optional[int] = None
    selectable_roles: List[int] = Field(default_factory=list)


class GuildConfigUpdate(BaseModel):
    welcome_channel_id: Optional[int] = None
    welcome_role_id: Optional[int] = None
    level_channel_id: Optional[int] = None
    role_select_channel_id: Optional[int] = None
    selectable_roles: Optional[List[int]] = None


class UserLevelOut(BaseModel):
    guild_id: int
    user_id: int
    message_count: int
    level: int
    xp: int
    days_on_server: int


class UserLevelUpdate(BaseModel):
    message_count: Optional[int] = None
    level: Optional[int] = None
    xp: Optional[int] = None
    days_on_server: Optional[int] = None

