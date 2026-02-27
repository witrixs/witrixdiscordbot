from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status

from app.api.deps import get_current_user_optional, require_auth_or_api_key
from app.api.schemas import (
    ChannelOut,
    GuildConfigOut,
    GuildConfigUpdate,
    GuildOut,
    RoleOut,
    UserLevelOut,
    UserLevelUpdate,
)
from app.core.guild_cache import get_guild_channels, get_guild_roles, get_guilds, get_guild_users, get_user_info, is_deleted_user
from app.db.database import Database
from app.db.models import GuildConfig, UserLevel


router = APIRouter(prefix="/api", tags=["guilds"], dependencies=[Depends(require_auth_or_api_key)])
db = Database()


def _parse_selectable_roles(raw: str | None) -> list[int]:
    if not raw:
        return []
    return [int(x) for x in raw.split(",") if x]


def _guild_out(g: dict) -> GuildOut:
    return GuildOut(id=str(g["id"]), name=g["name"], icon=g.get("icon"))


@router.get("/guilds", response_model=List[GuildOut])
async def list_guilds(user=Depends(get_current_user_optional)):
    """Список серверов: для админа/API — все с ботом; для Discord — только где пользователь участник."""
    all_guilds = get_guilds()
    if user and user.get("auth_type") == "discord":
        allowed = set(user.get("allowed_guild_ids") or [])
        all_guilds = [g for g in all_guilds if str(g["id"]) in allowed]
    return [_guild_out(g) for g in all_guilds]


@router.get("/guilds/{guild_id}/channels", response_model=List[ChannelOut])
async def list_guild_channels(guild_id: str):
    """Каналы сервера для выбора в настройках."""
    gid = int(guild_id)
    return [ChannelOut(id=str(c["id"]), name=c["name"], type=c.get("type", 0)) for c in get_guild_channels(gid)]


@router.get("/guilds/{guild_id}/roles", response_model=List[RoleOut])
async def list_guild_roles(guild_id: str):
    """Роли сервера для выбора в настройках."""
    gid = int(guild_id)
    return [RoleOut(id=str(r["id"]), name=r["name"]) for r in get_guild_roles(gid)]


def _config_to_out(config: GuildConfig | None, guild_id: int) -> GuildConfigOut:
    if not config:
        return GuildConfigOut(
            guild_id=str(guild_id),
            welcome_channel_id=None,
            welcome_role_id=None,
            level_channel_id=None,
            role_select_channel_id=None,
            selectable_roles=[],
        )
    return GuildConfigOut(
        guild_id=str(config.guild_id),
        welcome_channel_id=str(config.welcome_channel_id) if config.welcome_channel_id is not None else None,
        welcome_role_id=str(config.welcome_role_id) if config.welcome_role_id is not None else None,
        level_channel_id=str(config.level_channel_id) if config.level_channel_id is not None else None,
        role_select_channel_id=str(config.role_select_channel_id) if config.role_select_channel_id is not None else None,
        selectable_roles=[str(x) for x in _parse_selectable_roles(config.selectable_roles)],
    )


@router.get("/guilds/{guild_id}/config", response_model=GuildConfigOut)
async def get_guild_config(guild_id: str):
    gid = int(guild_id)
    session = db.Session()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=gid).first()
    finally:
        session.close()
    return _config_to_out(config, gid)


def _ensure_guild_admin(user, guild_id: str) -> None:
    """403 если пользователь Discord и не админ этого сервера."""
    if not user or user.get("auth_type") != "discord":
        return
    admin_ids = user.get("admin_guild_ids") or []
    if guild_id not in admin_ids:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You need to be a server admin to manage this guild",
        )


@router.put("/guilds/{guild_id}/config", response_model=GuildConfigOut)
async def update_guild_config(
    guild_id: str,
    payload: GuildConfigUpdate,
    user=Depends(get_current_user_optional),
):
    _ensure_guild_admin(user, guild_id)
    gid = int(guild_id)
    channel_id = int(payload.welcome_channel_id) if payload.welcome_channel_id is not None else None
    role_id = int(payload.welcome_role_id) if payload.welcome_role_id is not None else None
    level_channel_id = int(payload.level_channel_id) if payload.level_channel_id is not None else None
    role_select_channel_id = int(payload.role_select_channel_id) if payload.role_select_channel_id is not None else None
    selectable_roles = [int(x) for x in payload.selectable_roles] if payload.selectable_roles else None
    db.update_guild_config(
        guild_id=gid,
        channel_id=channel_id,
        role_id=role_id,
        level_channel_id=level_channel_id,
        role_select_channel_id=role_select_channel_id,
        selectable_roles=selectable_roles,
    )

    session = db.Session()
    try:
        config = session.query(GuildConfig).filter_by(guild_id=gid).first()
    finally:
        session.close()

    if not config:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Config not found")

    return _config_to_out(config, gid)


def _user_level_out(gid: int, u: UserLevel, info: dict | None) -> UserLevelOut:
    return UserLevelOut(
        guild_id=str(u.guild_id),
        user_id=str(u.user_id),
        message_count=u.message_count,
        level=u.level,
        xp=u.xp,
        days_on_server=u.days_on_server,
        display_name=info.get("name") if info else None,
        avatar_url=info.get("avatar") if info else None,
    )


@router.get("/guilds/{guild_id}/users/count")
async def get_users_count(guild_id: str):
    """Число участников сервера (из кэша бота, без удалённых аккаунтов)."""
    gid = int(guild_id)
    cached = get_guild_users(gid)
    if cached:
        count = sum(1 for _, info in cached.items() if not is_deleted_user(info.get("name")))
    else:
        count = db.get_users_in_guild_count(gid)
    return {"count": count}


@router.get("/guilds/{guild_id}/users", response_model=List[UserLevelOut])
async def list_users(
    guild_id: str,
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=10000),
    order_by: str = Query("level", description="level | xp | message_count | days_on_server"),
    order: str = Query("desc", description="desc | asc"),
):
    """Список всех участников сервера: из кэша + уровни из БД (нет в БД — уровень 0, можно выставить и сохранить)."""
    gid = int(guild_id)
    cached = get_guild_users(gid)
    if not cached:
        # Кэш пуст — отдаём только тех, кто есть в БД (как раньше), без deleted_user
        users = db.get_users_in_guild_paginated(
            gid, offset=offset, limit=limit, order_by=order_by, order=order
        )
        out_list = [_user_level_out(gid, u, get_user_info(gid, u.user_id)) for u in users]
        return [o for o in out_list if not is_deleted_user(o.display_name)]

    db_users = {u.user_id: u for u in db.get_users_in_guild(gid)}
    col = order_by if order_by in ("level", "xp", "message_count", "days_on_server") else "level"
    desc = order == "desc"

    result = []
    for user_id, info in cached.items():
        if is_deleted_user(info.get("name")):
            continue
        u = db_users.get(user_id)
        if u:
            result.append(_user_level_out(gid, u, info))
        else:
            result.append(
                UserLevelOut(
                    guild_id=str(gid),
                    user_id=str(user_id),
                    message_count=0,
                    level=0,
                    xp=0,
                    days_on_server=0,
                    display_name=info.get("name"),
                    avatar_url=info.get("avatar"),
                )
            )

    result.sort(key=lambda x: getattr(x, col), reverse=desc)
    return result[offset : offset + limit]


@router.get("/guilds/{guild_id}/users/{user_id}", response_model=UserLevelOut)
async def get_user(guild_id: str, user_id: str):
    gid, uid = int(guild_id), int(user_id)
    session = db.Session()
    try:
        user = session.query(UserLevel).filter_by(guild_id=gid, user_id=uid).first()
    finally:
        session.close()

    info = get_user_info(gid, uid)
    if user:
        out = _user_level_out(gid, user, info)
        if is_deleted_user(out.display_name):
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        return out
    if info and not is_deleted_user(info.get("name")):
        return UserLevelOut(
            guild_id=str(gid),
            user_id=str(uid),
            message_count=0,
            level=0,
            xp=0,
            days_on_server=0,
            display_name=info.get("name"),
            avatar_url=info.get("avatar"),
        )
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")


@router.put("/guilds/{guild_id}/users/{user_id}", response_model=UserLevelOut)
async def update_user(
    guild_id: str,
    user_id: str,
    payload: UserLevelUpdate,
    user=Depends(get_current_user_optional),
):
    _ensure_guild_admin(user, guild_id)
    gid, uid = int(guild_id), int(user_id)
    db.update_user_level(
        guild_id=gid,
        user_id=uid,
        message_count=payload.message_count,
        level=payload.level,
        xp=payload.xp,
        days_on_server=payload.days_on_server,
    )

    session = db.Session()
    try:
        user = session.query(UserLevel).filter_by(guild_id=gid, user_id=uid).first()
    finally:
        session.close()

    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    info = get_user_info(gid, user.user_id)
    return UserLevelOut(
        guild_id=str(user.guild_id),
        user_id=str(user.user_id),
        message_count=user.message_count,
        level=user.level,
        xp=user.xp,
        days_on_server=user.days_on_server,
        display_name=info.get("name") if info else None,
        avatar_url=info.get("avatar") if info else None,
    )

