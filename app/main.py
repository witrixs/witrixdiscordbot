from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from app.api.router import api_router
from app.core.config import Config

# Корень проекта (папка witrix-discordbot)
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIST = BASE_DIR / "frontend" / "dist"


def _parse_cors_origins(raw: str) -> list[str]:
    raw = (raw or "").strip()
    if not raw or raw == "*":
        return ["*"]
    return [x.strip() for x in raw.split(",") if x.strip()]


def create_app() -> FastAPI:
    app = FastAPI(title="Discord Bot API", version="0.9.5")

    origins = _parse_cors_origins(Config.CORS_ORIGINS)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(api_router)

    # Статика из frontend/dist (после сборки: yarn build)
    if FRONTEND_DIST.is_dir():

        @app.get("/{full_path:path}")
        async def serve_spa(full_path: str):
            if full_path.startswith("api/"):
                raise HTTPException(404)
            path = FRONTEND_DIST / full_path
            if path.is_file():
                return FileResponse(path)
            index = FRONTEND_DIST / "index.html"
            if index.is_file():
                return FileResponse(index)
            raise HTTPException(404)

    return app


app = create_app()

