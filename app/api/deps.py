from __future__ import annotations

from typing import Annotated, TypedDict

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Config

security_bearer = HTTPBearer(auto_error=False)


class CurrentUser(TypedDict, total=False):
    username: str
    auth_type: str
    discord_id: int | None
    avatar: str | None  # Discord avatar hash
    allowed_guild_ids: list[str] | None  # None = все (админ)
    admin_guild_ids: list[str] | None     # None = все (админ)


async def require_api_key(x_api_key: str = Header(default=None, alias="X-API-Key")) -> None:
    if not x_api_key or x_api_key != Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def decode_token(token: str) -> dict:
    if not Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY not configured",
        )
    try:
        payload = jwt.decode(
            token,
            Config.SECRET_KEY,
            algorithms=["HS256"],
        )
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
        )


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
) -> CurrentUser:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    payload = decode_token(credentials.credentials)
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    auth_type = payload.get("auth_type") or "admin"
    if auth_type == "discord" and sub.startswith("discord:"):
        discord_id = payload.get("discord_id")
        username = payload.get("username") or sub
        return CurrentUser(
            username=username,
            auth_type="discord",
            discord_id=discord_id,
            avatar=payload.get("avatar"),
            allowed_guild_ids=payload.get("allowed_guild_ids") or [],
            admin_guild_ids=payload.get("admin_guild_ids") or [],
        )
    return CurrentUser(
        username=sub,
        auth_type="admin",
        discord_id=None,
        allowed_guild_ids=None,
        admin_guild_ids=None,
    )


async def get_current_user_optional(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
) -> CurrentUser | None:
    """Текущий пользователь по Bearer или None (если нет токена / используется X-API-Key)."""
    if not credentials or credentials.scheme.lower() != "bearer":
        return None
    try:
        payload = decode_token(credentials.credentials)
    except HTTPException:
        return None
    sub = payload.get("sub")
    if not sub or not isinstance(sub, str):
        return None
    auth_type = payload.get("auth_type") or "admin"
    if auth_type == "discord" and sub.startswith("discord:"):
        return CurrentUser(
            username=payload.get("username") or sub,
            auth_type="discord",
            discord_id=payload.get("discord_id"),
            avatar=payload.get("avatar"),
            allowed_guild_ids=payload.get("allowed_guild_ids") or [],
            admin_guild_ids=payload.get("admin_guild_ids") or [],
        )
    return CurrentUser(
        username=sub,
        auth_type="admin",
        discord_id=None,
        allowed_guild_ids=None,
        admin_guild_ids=None,
    )


async def require_auth_or_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
    x_api_key: str = Header(default=None, alias="X-API-Key"),
) -> None:
    """Доступ по Bearer JWT (веб-панель) или по X-API-Key (скрипты)."""
    if credentials and credentials.scheme.lower() == "bearer":
        try:
            decode_token(credentials.credentials)
            return
        except HTTPException:
            pass
    if x_api_key and x_api_key == Config.SECRET_KEY:
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing auth (Bearer token or X-API-Key)",
    )

