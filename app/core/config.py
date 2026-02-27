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

    # для Vue/Vite (или любого фронта)
    # пример: "http://localhost:5173,http://127.0.0.1:5173"
    CORS_ORIGINS = os.getenv("CORS_ORIGINS", "*")

    # Статус бота в Discord: тип (playing / listening / watching) и текст
    BOT_STATUS_TYPE = os.getenv("BOT_STATUS_TYPE", "listening")
    BOT_STATUS_NAME = os.getenv("BOT_STATUS_NAME", "ALBLAK 52")

