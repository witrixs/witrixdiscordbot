from datetime import UTC, datetime, timedelta
from urllib.parse import urlencode

import aiohttp
import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import RedirectResponse
from passlib.context import CryptContext
from werkzeug.security import check_password_hash as werkzeug_check

from app.api.deps import CurrentUser, get_current_user
from app.api.schemas import DefaultGuildUpdate, LoginRequest, TokenResponse, UserMeOut
from app.core.config import Config
from app.core.guild_cache import get_guilds
from app.db.database import Database

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")
db = Database()

router = APIRouter(prefix="/api", tags=["auth"])

# Discord permission bits: ADMINISTRATOR=8, MANAGE_GUILD=0x20
DISCORD_ADMIN_PERMISSIONS = 8 | 0x20


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
        {"sub": username_for_token, "exp": expires, "auth_type": "admin"},
        Config.SECRET_KEY,
        algorithm="HS256",
    )
    return TokenResponse(access_token=token)


def _build_user_me_out(user: CurrentUser) -> UserMeOut:
    username = user.get("username") or ""
    auth_type = user.get("auth_type") or "admin"
    is_discord = auth_type == "discord"
    default_guild_id = None
    avatar_url = None
    if is_discord and user.get("discord_id") is not None:
        gid = db.get_discord_default_guild(int(user["discord_id"]))
        default_guild_id = str(gid) if gid is not None else None
        avatar_hash = user.get("avatar")
        if avatar_hash:
            avatar_url = f"https://cdn.discordapp.com/avatars/{user['discord_id']}/{avatar_hash}.png?size=64"
    return UserMeOut(
        username=username,
        auth_type=auth_type,
        avatar_url=avatar_url,
        is_discord_user=is_discord,
        allowed_guild_ids=user.get("allowed_guild_ids") or [],
        admin_guild_ids=user.get("admin_guild_ids") or [],
        default_guild_id=default_guild_id,
    )


@router.get("/auth/me", response_model=UserMeOut)
async def me(user: CurrentUser = Depends(get_current_user)):
    return _build_user_me_out(user)


@router.put("/auth/me/default-guild", response_model=UserMeOut)
async def set_default_guild(
    payload: DefaultGuildUpdate,
    user: CurrentUser = Depends(get_current_user),
):
    if user.get("auth_type") != "discord" or user.get("discord_id") is None:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only Discord users can set default guild",
        )
    discord_id = int(user["discord_id"])
    guild_id = int(payload.guild_id) if payload.guild_id else None
    if payload.guild_id and discord_id:
        allowed = user.get("allowed_guild_ids") or []
        if payload.guild_id not in allowed:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Guild not in your allowed list",
            )
    db.set_discord_default_guild(discord_id, guild_id)
    return _build_user_me_out(user)


# --- Discord OAuth ---


@router.get("/auth/discord")
async def discord_redirect():
    """Редирект на Discord OAuth2."""
    if not Config.DISCORD_CLIENT_ID or not Config.DISCORD_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth not configured",
        )
    params = {
        "client_id": Config.DISCORD_CLIENT_ID,
        "redirect_uri": Config.DISCORD_REDIRECT_URI,
        "response_type": "code",
        "scope": "identify guilds",
    }
    url = "https://discord.com/api/oauth2/authorize?" + urlencode(params)
    return RedirectResponse(url=url, status_code=302)


@router.get("/auth/discord/callback")
async def discord_callback(code: str | None = None, error: str | None = None):
    """Обмен code на токен, получение пользователя и гильдий, выдача JWT, редирект на фронт."""
    if error or not code:
        frontend = (Config.FRONTEND_URL or "").rstrip("/") + "/login"
        return RedirectResponse(url=f"{frontend}?error=discord_denied", status_code=302)
    if not Config.DISCORD_CLIENT_ID or not Config.DISCORD_CLIENT_SECRET or not Config.DISCORD_REDIRECT_URI:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Discord OAuth not configured",
        )
    if not Config.SECRET_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="SECRET_KEY not configured",
        )

    async with aiohttp.ClientSession() as session:
        # Обмен code на access_token
        async with session.post(
            "https://discord.com/api/oauth2/token",
            data={
                "client_id": Config.DISCORD_CLIENT_ID,
                "client_secret": Config.DISCORD_CLIENT_SECRET,
                "grant_type": "authorization_code",
                "code": code,
                "redirect_uri": Config.DISCORD_REDIRECT_URI,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
        ) as resp:
            if resp.status != 200:
                text = await resp.text()
                frontend = (Config.FRONTEND_URL or "").rstrip("/") + "/login"
                return RedirectResponse(url=f"{frontend}?error=discord_token", status_code=302)
            data = await resp.json()
    access_token = data.get("access_token")
    if not access_token:
        frontend = (Config.FRONTEND_URL or "").rstrip("/") + "/login"
        return RedirectResponse(url=f"{frontend}?error=discord_token", status_code=302)

    async with aiohttp.ClientSession() as session:
        # Текущий пользователь Discord
        async with session.get(
            "https://discord.com/api/users/@me",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status != 200:
                frontend = (Config.FRONTEND_URL or "").rstrip("/") + "/login"
                return RedirectResponse(url=f"{frontend}?error=discord_user", status_code=302)
            user_data = await resp.json()
        # Гильдии пользователя (с permissions)
        async with session.get(
            "https://discord.com/api/users/@me/guilds",
            headers={"Authorization": f"Bearer {access_token}"},
        ) as resp:
            if resp.status != 200:
                frontend = (Config.FRONTEND_URL or "").rstrip("/") + "/login"
                return RedirectResponse(url=f"{frontend}?error=discord_guilds", status_code=302)
            user_guilds = await resp.json()

    discord_id = int(user_data["id"])
    username = user_data.get("global_name") or user_data.get("username") or str(discord_id)
    avatar_hash = user_data.get("avatar")
    # Сервера, на которых есть бот
    bot_guild_ids = {str(g["id"]) for g in get_guilds()}
    # Сервера, где пользователь участник и есть бот
    allowed_guild_ids: list[str] = []
    admin_guild_ids: list[str] = []
    for g in user_guilds:
        gid = str(g["id"])
        if gid not in bot_guild_ids:
            continue
        allowed_guild_ids.append(gid)
        perms = int(g.get("permissions", 0))
        if perms & DISCORD_ADMIN_PERMISSIONS:
            admin_guild_ids.append(gid)

    expires = datetime.now(UTC) + timedelta(days=7)
    token = jwt.encode(
        {
            "sub": f"discord:{discord_id}",
            "exp": expires,
            "auth_type": "discord",
            "discord_id": discord_id,
            "username": username,
            "avatar": avatar_hash,
            "allowed_guild_ids": allowed_guild_ids,
            "admin_guild_ids": admin_guild_ids,
        },
        Config.SECRET_KEY,
        algorithm="HS256",
    )
    frontend = (Config.FRONTEND_URL or "").rstrip("/")
    redirect_url = f"{frontend}/auth/callback#access_token={token}"
    return RedirectResponse(url=redirect_url, status_code=302)
