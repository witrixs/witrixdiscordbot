import asyncio
import threading

import uvicorn

from app.bot.bot import bot
from app.core.config import Config


def run_api():
    """Запуск API в отдельном потоке (блокирующий)."""
    uvicorn.run(
        "app.main:app",
        host="127.0.0.1",
        port=4000,
        log_level="info",
    )


async def start_bot():
    if not Config.DISCORD_TOKEN:
        raise RuntimeError("DISCORD_TOKEN не задан в .env")
    print(f"Starting bot with token: {Config.DISCORD_TOKEN[:10]}...")
    try:
        await bot.start(Config.DISCORD_TOKEN)
    except Exception as e:
        print(f"Ошибка при запуске бота: {e}")
        raise
    finally:
        await bot.close()


if __name__ == "__main__":
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

    try:
        asyncio.run(start_bot())
    except Exception as e:
        print(f"Ошибка в главном цикле: {e}")
