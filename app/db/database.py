from __future__ import annotations

from typing import Iterable, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.core.config import Config
from app.db.base import Base
from app.db.models import AdminUser, GuildConfig, UserLevel


def _make_engine(db_url: str):
    # SQLite требует отдельного connect_args
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False},
            pool_pre_ping=True,
        )
    return create_engine(db_url, pool_pre_ping=True)


class Database:
    def __init__(self, db_url: Optional[str] = None):
        url = db_url or Config.DB_URL
        if not url:
            raise RuntimeError("DB_URL не задан в .env")

        # чтобы Postgres заводился “из коробки” с psycopg v3
        if url.startswith("postgresql://"):
            url = url.replace("postgresql://", "postgresql+psycopg://", 1)
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg://", 1)

        self.engine = _make_engine(url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine, autoflush=False, autocommit=False)

    def get_admin_by_username(self, username: str) -> AdminUser | None:
        session = self.Session()
        try:
            return session.query(AdminUser).filter_by(username=username).first()
        finally:
            session.close()

    def get_guild_config(self, guild_id: int):
        session = self.Session()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            if not config:
                return None
            return {
                "welcome_channel_id": config.welcome_channel_id,
                "welcome_role_id": config.welcome_role_id,
                "level_channel_id": config.level_channel_id,
                "role_select_channel_id": config.role_select_channel_id,
                "selectable_roles": (
                    [int(x) for x in config.selectable_roles.split(",") if x]
                    if config.selectable_roles
                    else []
                ),
            }
        finally:
            session.close()

    def update_guild_config(
        self,
        guild_id: int,
        channel_id: Optional[int] = None,
        role_id: Optional[int] = None,
        level_channel_id: Optional[int] = None,
        role_select_channel_id: Optional[int] = None,
        selectable_roles: Optional[list[int]] = None,
    ):
        session = self.Session()
        try:
            config = session.query(GuildConfig).filter_by(guild_id=guild_id).first()
            if not config:
                config = GuildConfig(guild_id=guild_id)
                session.add(config)

            # Всегда обновляем все переданные поля (фронт шлёт полный объект, null = сброс)
            config.welcome_channel_id = channel_id
            config.welcome_role_id = role_id
            config.level_channel_id = level_channel_id
            config.role_select_channel_id = role_select_channel_id
            config.selectable_roles = (
                ",".join(map(str, selectable_roles)) if selectable_roles else None
            )

            session.commit()
        finally:
            session.close()

    def get_user_level(self, guild_id: int, user_id: int) -> UserLevel:
        session = self.Session()
        try:
            user_level = session.query(UserLevel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if not user_level:
                user_level = UserLevel(guild_id=guild_id, user_id=user_id, level=1, message_count=0, xp=0, days_on_server=0)
                session.add(user_level)
                session.commit()
            # возвращаем объект с уже загруженными полями
            return user_level
        finally:
            session.close()

    def update_user_level(
        self,
        guild_id: int,
        user_id: int,
        message_count: Optional[int] = None,
        level: Optional[int] = None,
        xp: Optional[int] = None,
        days_on_server: Optional[int] = None,
    ) -> None:
        session = self.Session()
        try:
            user_level = session.query(UserLevel).filter_by(guild_id=guild_id, user_id=user_id).first()
            if not user_level:
                user_level = UserLevel(guild_id=guild_id, user_id=user_id, level=1, message_count=0, xp=0, days_on_server=0)
                session.add(user_level)

            if message_count is not None:
                user_level.message_count = message_count
            if level is not None:
                user_level.level = level
            if xp is not None:
                user_level.xp = xp
            if days_on_server is not None:
                user_level.days_on_server = days_on_server

            session.commit()
        finally:
            session.close()

    def get_users_in_guild(self, guild_id: int) -> list[UserLevel]:
        session = self.Session()
        try:
            return session.query(UserLevel).filter_by(guild_id=guild_id).all()
        finally:
            session.close()

    def add_all_users_to_guild(self, guild_id: int, members: Iterable) -> None:
        session = self.Session()
        try:
            for member in members:
                if getattr(member, "bot", False):
                    continue
                existing = session.query(UserLevel).filter_by(guild_id=guild_id, user_id=member.id).first()
                if not existing:
                    session.add(
                        UserLevel(guild_id=guild_id, user_id=member.id, level=1, message_count=0, xp=0, days_on_server=0)
                    )
            session.commit()
        finally:
            session.close()

