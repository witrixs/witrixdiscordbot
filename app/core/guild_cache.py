"""
Кэш гильдий/каналов/ролей для веб-API. Обновляется ботом в on_ready и on_guild_join/remove.
"""
from __future__ import annotations

import threading
from typing import Any

_lock = threading.Lock()
_guilds: list[dict[str, Any]] = []
_channels: dict[int, list[dict[str, Any]]] = {}
_roles: dict[int, list[dict[str, Any]]] = {}
_users: dict[int, dict[int, dict[str, Any]]] = {}  # guild_id -> user_id -> {name, avatar}


def set_guilds(guilds: list[dict[str, Any]]) -> None:
    with _lock:
        global _guilds
        _guilds = list(guilds)


def set_guild_channels(guild_id: int, channels: list[dict[str, Any]]) -> None:
    with _lock:
        _channels[guild_id] = list(channels)


def set_guild_roles(guild_id: int, roles: list[dict[str, Any]]) -> None:
    with _lock:
        _roles[guild_id] = list(roles)


def get_guilds() -> list[dict[str, Any]]:
    with _lock:
        return list(_guilds)


def get_guild_channels(guild_id: int) -> list[dict[str, Any]]:
    with _lock:
        return list(_channels.get(guild_id, []))


def get_guild_roles(guild_id: int) -> list[dict[str, Any]]:
    with _lock:
        return list(_roles.get(guild_id, []))


def is_deleted_user(name: str | None) -> bool:
    """Удалённый аккаунт Discord (deleted_user_...). Таких не показываем нигде."""
    if not name or not isinstance(name, str):
        return False
    return name.strip().lower().startswith("deleted_user")


def get_user_info(guild_id: int, user_id: int) -> dict[str, Any] | None:
    """Имя и аватар участника из кэша бота."""
    with _lock:
        return _users.get(guild_id, {}).get(user_id)


def set_user_info(guild_id: int, user_id: int, name: str, avatar: str | None = None) -> None:
    """Добавить/обновить имя и аватар участника в кэше (для тех, кого нет в guild.members)."""
    with _lock:
        global _users
        if guild_id not in _users:
            _users[guild_id] = {}
        _users[guild_id][user_id] = {"name": name, "avatar": avatar or _users[guild_id].get(user_id, {}).get("avatar")}


def get_guild_users(guild_id: int) -> dict[int, dict[str, Any]]:
    """Все участники гильдии из кэша: user_id -> {name, avatar}."""
    with _lock:
        return dict(_users.get(guild_id, {}))


def update_guild(
    guild_data: dict[str, Any],
    channels: list[dict[str, Any]],
    roles: list[dict[str, Any]],
    users: dict[int, dict[str, Any]] | None = None,
) -> None:
    """Добавить/обновить одну гильдию (on_guild_join или при синхронизации)."""
    with _lock:
        global _guilds, _channels, _roles, _users
        gid = guild_data.get("id")
        if gid is None:
            return
        existing = [g for g in _guilds if g.get("id") == gid]
        if existing:
            idx = _guilds.index(existing[0])
            _guilds[idx] = guild_data
        else:
            _guilds.append(guild_data)
        _channels[gid] = list(channels)
        _roles[gid] = list(roles)
        if users is not None:
            _users[gid] = dict(users)


def remove_guild(guild_id: int) -> None:
    with _lock:
        global _guilds, _channels, _roles, _users
        _guilds = [g for g in _guilds if g.get("id") != guild_id]
        _channels.pop(guild_id, None)
        _roles.pop(guild_id, None)
        _users.pop(guild_id, None)


def sync_all(
    guilds: list[dict[str, Any]],
    channels: dict[int, list[dict[str, Any]]],
    roles: dict[int, list[dict[str, Any]]],
    users: dict[int, dict[int, dict[str, Any]]] | None = None,
) -> None:
    """Полная перезапись кэша (вызов из бота on_ready)."""
    with _lock:
        global _guilds, _channels, _roles, _users
        _guilds = list(guilds)
        _channels = {k: list(v) for k, v in channels.items()}
        _roles = {k: list(v) for k, v in roles.items()}
        if users is not None:
            _users = {k: dict(v) for k, v in users.items()}
