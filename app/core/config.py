from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
    SECRET_KEY = os.getenv("SECRET_KEY")
    DB_URL = os.getenv("DB_URL")

    # Логин/пароль для веб-панели (проверка при POST /api/auth/login)
    ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
    ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "")

    # Discord OAuth2 для входа через Discord
    DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID", "")
    DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET", "")
    # Полный URL колбэка OAuth (например https://discord.rafaello.cc/api/auth/discord/callback)
    DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI", "")
    # URL фронта для редиректа после OAuth (например https://discord.rafaello.cc)
    FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

    # для Vue/Vite (или любого фронта)
    # пример: "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Статус бота в Discord: тип (playing / listening / watching) и текст
    BOT_STATUS_TYPE = os.getenv("BOT_STATUS_TYPE", "listening")
    BOT_STATUS_NAME = os.getenv("BOT_STATUS_NAME", "ALBLAK 52")

    # Хост для API (в Docker задать 0.0.0.0)
    API_HOST = os.getenv("API_HOST", "127.0.0.1")
    API_PORT = int(os.getenv("API_PORT", "4000"))

