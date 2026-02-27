from typing import Annotated

import jwt
from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.core.config import Config

security_bearer = HTTPBearer(auto_error=False)


async def require_api_key(x_api_key: str = Header(default=None, alias="X-API-Key")) -> None:
    if not x_api_key or x_api_key != Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )


def _decode_token(token: str) -> dict:
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
) -> str:
    if not credentials or credentials.scheme.lower() != "bearer":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid Authorization header",
        )
    payload = _decode_token(credentials.credentials)
    username = payload.get("sub")
    if not username or not isinstance(username, str):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
        )
    return username


async def require_auth_or_api_key(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_bearer)],
    x_api_key: str = Header(default=None, alias="X-API-Key"),
) -> None:
    """Доступ по Bearer JWT (веб-панель) или по X-API-Key (скрипты)."""
    if credentials and credentials.scheme.lower() == "bearer":
        try:
            _decode_token(credentials.credentials)
            return
        except HTTPException:
            pass
    if x_api_key and x_api_key == Config.SECRET_KEY:
        return
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Invalid or missing auth (Bearer token or X-API-Key)",
    )

