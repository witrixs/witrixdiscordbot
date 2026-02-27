from typing import List

from fastapi import APIRouter, Depends, HTTPException, status

from app.api.deps import require_auth_or_api_key
from app.api.schemas import (
    ChannelOut,
    GuildConfigOut,
    GuildConfigUpdate,
    GuildOut,
    RoleOut,
    UserLevelOut,
    UserLevelUpdate,
)
from app.core.guild_cache import get_guild_channels, get_guild_roles, get_guilds
from app.db.database import Database
from app.db.models import GuildConfig, UserLevel


router = APIRouter(prefix="/api", tags=["guilds"], dependencies=[Depends(require_auth_or_api_key)])
db = Database()


def _parse_selectable_roles(raw: str | None) -> list[int]:
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x]


@router.get("/guilds", response_model=List[GuildOut])
async def list_guilds():
    """Список серверов Discord, на которых есть бот (из кэша бота)."""
    return [GuildOut(**g) for g in get_guilds()]


@router.get("/guilds/{guild_id}/channels", response_model=List[ChannelOut])
async def list_guild_channels(guild_id: int):
    """Каналы сервера для выбора в настройках."""
    return [ChannelOut(**c) for c in get_guild_channels(guild_id)]


@router.get("/guilds/{guild_id}/roles", response_model=List[RoleOut])
async def list_guild_roles(guild_id: int):
    """Роли сервера для выбора в настройках."""
    return [RoleOut(**r) for r in get_guild_roles(guild_id)]


@router.get("/guilds/{guild_id}/config", response_model=GuildConfigOut)
async def get_guild_config(guild_id: int):
    session = db.Session()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    finally:
        session.close()

    if not config:
        return GuildConfigOut(
            guild_id=guild_id,
            welcome_channel_id=None,
            welcome_role_id=None,
            level_channel_id=None,
            role_select_channel_id=None,
            selectable_roles=[],
        )

    return GuildConfigOut(
        guild_id=config.guild_id,
        welcome_channel_id=config.welcome_channel_id,
        welcome_role_id=config.welcome_role_id,
        level_channel_id=config.level_channel_id,
        role_select_channel_id=config.role_select_channel_id,
        selectable_roles=_parse_selectable_roles(config.selectable_roles),
    )


@router.put("/guilds/{guild_id}/config", response_model=GuildConfigOut)
async def update_guild_config(guild_id: int, payload: GuildConfigUpdate):
    db.update_guild_config(
        guild_id=guild_id,
        channel_id=payload.welcome_channel_id,
        role_id=payload.welcome_role_id,
        level_channel_id=payload.level_channel_id,
        role_select_channel_id=payload.role_select_channel_id,
        selectable_roles=payload.selectable_roles,
    )

    session = db.Session()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
    finally:
        session.close()

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    return GuildConfigOut(
        guild_id=config.guild_id,
        welcome_channel_id=config.welcome_channel_id,
        welcome_role_id=config.welcome_role_id,
        level_channel_id=config.level_channel_id,
        role_select_channel_id=config.role_select_channel_id,
        selectable_roles=_parse_selectable_roles(config.selectable_roles),
    )


@router.get("/guilds/{guild_id}/users", response_model=List[UserLevelOut])
async def list_users(guild_id: int):
    users = db.get_users_in_guild(guild_id)
    return [
        UserLevelOut(
            guild_id=u.guild_id,
            user_id=u.user_id,
            message_count=u.message_count,
            level=u.level,
            xp=u.xp,
            days_on_server=u.days_on_server,
        )
        for u in users
    ]


@router.get("/guilds/{guild_id}/users/{user_id}", response_model=UserLevelOut)
async def get_user(guild_id: int, user_id: int):
    session = db.Session()
    try:
        user = session.query(UserLevel).filter_by(guild_id=guild_id, user_id=user_id).first()
    finally:
        session.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserLevelOut(
        guild_id=user.guild_id,
        user_id=user.user_id,
        message_count=user.message_count,
        level=user.level,
        xp=user.xp,
        days_on_server=user.days_on_server,
    )


@router.put("/guilds/{guild_id}/users/{user_id}", response_model=UserLevelOut)
async def update_user(guild_id: int, user_id: int, payload: UserLevelUpdate):
    db.update_user_level(
        guild_id=guild_id,
        user_id=user_id,
        message_count=payload.message_count,
        level=payload.level,
        xp=payload.xp,
        days_on_server=payload.days_on_server,
    )

    session = db.Session()
    try:
        user = session.query(UserLevel).filter_by(guild_id=guild_id, user_id=user_id).first()
    finally:
        session.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    return UserLevelOut(
        guild_id=user.guild_id,
        user_id=user.user_id,
        message_count=user.message_count,
        level=user.level,
        xp=user.xp,
        days_on_server=user.days_on_server,
    )

