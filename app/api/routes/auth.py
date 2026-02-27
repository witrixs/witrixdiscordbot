from datetime import UTC, datetime, timedelta

import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from passlib.context import CryptContext
from werkzeug.security import check_password_hash as werkzeug_check

from app.api.deps import get_current_user
from app.api.schemas import LoginRequest, TokenResponse, UserMeOut
from app.core.config import Config
from app.db.database import Database

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = Database()

router = APIRouter(prefix="/api", tags=["auth"])


def _verify_password(plain: str, hashed: str) -> bool:
    # Werkzeug (scrypt, pbkdf2 и др.) — например scrypt:32768:8:1$...
    if hashed.startswith("scrypt:") or hashed.startswith("pbkdf2:"):
        return werkzeug_check(hashed, plain)
    # Bcrypt — $2b$... / $2a$...
    try:
        return pwd_ctx.verify(plain, hashed)
    except Exception:
        return False


@router.post("/auth/login", response_model=TokenResponse)
async def login(payload: LoginRequest):
    username_for_token: str | None = None

    # 1) Пробуем по БД (admin_users)
    admin = db.get_admin_by_username(payload.username)
    if admin and _verify_password(payload.password, admin.password_hash):
        username_for_token = admin.username

    # 2) Fallback: логин/пароль из .env
    if username_for_token is None and Config.ADMIN_PASSWORD:
        if payload.username == Config.ADMIN_USERNAME and payload.password == Config.ADMIN_PASSWORD:
            username_for_token = Config.ADMIN_USERNAME

    if username_for_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
        )
    if not Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY not configured",
        )
    expires = datetime.now(UTC) + timedelta(days=7)
    token = jwt.encode(
        {"sub": username_for_token, "exp": expires},
        Config.SECRET_KEY,
        algorithm="HS256",
    )
    return TokenResponse(access_token=token)


@router.get("/auth/me", response_model=UserMeOut)
async def me(username: str = Depends(get_current_user)):
    return UserMeOut(username=username)
