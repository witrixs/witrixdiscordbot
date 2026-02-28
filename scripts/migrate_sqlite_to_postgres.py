#!/usr/bin/env python3
"""
Миграция данных из SQLite в PostgreSQL с корректным маппингом типов.

Маппинг типов (по моделям app.db.models):
- BigInteger → PostgreSQL BIGINT (Discord snowflake ID, user_levels.id)
- Integer → INTEGER (счётчики, level, xp и т.д.)
- String(255) → VARCHAR(255), Text → TEXT

После копирования сбрасываются последовательности (SERIAL/BIGSERIAL), чтобы
новые записи получали корректные id.

Важно: целевая БД PostgreSQL должна быть пустой (без этих таблиц) или таблицы
нужно предварительно удалить, иначе возможны дубликаты ключей.

Использование:
  # Источник — DB_URL из .env (sqlite), цель — POSTGRES_URL из .env
  python scripts/migrate_sqlite_to_postgres.py

  # Или явно указать URL
  python scripts/migrate_sqlite_to_postgres.py sqlite:///bot.db postgresql://user:pass@host/dbname

После миграции замените в .env: DB_URL=postgresql://user:pass@host:5432/dbname
"""
from __future__ import annotations

import os
import sys

# корень проекта в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from dotenv import load_dotenv

load_dotenv()

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

from app.db.base import Base
from app.db.models import AdminUser, DiscordUserPrefs, GuildConfig, UserLevel


# Таблицы в порядке создания (нет FK между ними, порядок не критичен)
TABLES = [
    "admin_users",
    "guild_config",
    "user_levels",
    "discord_user_prefs",
]

# Таблицы с автоинкрементом PK — после копирования сбрасываем sequence
TABLES_WITH_SERIAL = [
    ("admin_users", "id"),
    ("user_levels", "id"),
]


def _pg_url(url: str) -> str:
    if url.startswith("postgresql://"):
        return url.replace("postgresql://", "postgresql+psycopg://", 1)
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg://", 1)
    return url


def _sqlite_engine(url: str) -> Engine:
    return create_engine(
        url,
        connect_args={"check_same_thread": False},
        pool_pre_ping=True,
    )


def _pg_engine(url: str) -> Engine:
    return create_engine(_pg_url(url), pool_pre_ping=True)


def _normalize_row(row: dict, table_name: str) -> dict:
    """Приводит значения к типам, подходящим для PostgreSQL (bigint и т.д.)."""
    out = {}
    for k, v in row.items():
        if v is None:
            out[k] = None
            continue
        # В SQLite всё приходит как int/str/float; для BIGINT нужен int
        if isinstance(v, float) and v.is_integer():
            out[k] = int(v)
        elif isinstance(v, str) and k in (
            "guild_id", "welcome_channel_id", "welcome_role_id",
            "level_channel_id", "role_select_channel_id",
            "user_id", "discord_id", "default_guild_id", "id"
        ):
            try:
                out[k] = int(v)
            except ValueError:
                out[k] = v
        else:
            out[k] = v
    return out


def copy_table(sqlite_engine: Engine, pg_engine: Engine, table_name: str) -> int:
    table = Base.metadata.tables[table_name]
    select_sql = table.select()

    with sqlite_engine.connect() as src:
        rows = src.execute(select_sql).mappings().all()
    if not rows:
        return 0

    rows_normalized = [_normalize_row(dict(r), table_name) for r in rows]
    insert_sql = table.insert()

    with pg_engine.connect() as dst:
        dst.execute(insert_sql, rows_normalized)
        dst.commit()

    return len(rows_normalized)


def reset_pg_sequences(pg_engine: Engine) -> None:
    # Имена из константы TABLES_WITH_SERIAL — не пользовательский ввод
    for table_name, id_column in TABLES_WITH_SERIAL:
        with pg_engine.connect() as conn:
            # Сбрасываем sequence для SERIAL/BIGSERIAL после ручной вставки с явными id
            sql = (
                f"SELECT setval(pg_get_serial_sequence('{table_name}', '{id_column}'), "
                f"(SELECT COALESCE(MAX({id_column}), 1) FROM {table_name}))"
            )
            conn.execute(text(sql))
            conn.commit()


def main() -> None:
    if len(sys.argv) >= 3:
        sqlite_url = sys.argv[1]
        postgres_url = sys.argv[2]
    else:
        sqlite_url = os.getenv("DB_URL")
        postgres_url = os.getenv("POSTGRES_URL")
        if not sqlite_url or not postgres_url:
            print("Задайте DB_URL (SQLite) и POSTGRES_URL (PostgreSQL) в .env или аргументами:")
            print("  python scripts/migrate_sqlite_to_postgres.py <sqlite_url> <postgres_url>")
            sys.exit(1)
        if not sqlite_url.strip().lower().startswith("sqlite"):
            print("DB_URL должен указывать на SQLite (sqlite:///...).")
            sys.exit(1)

    sqlite_engine = _sqlite_engine(sqlite_url)
    pg_engine = _pg_engine(postgres_url)

    print("Создание таблиц в PostgreSQL по текущим моделям (BIGINT, INTEGER, TEXT и т.д.)...")
    Base.metadata.create_all(pg_engine)

    for name in TABLES:
        n = copy_table(sqlite_engine, pg_engine, name)
        print(f"  {name}: перенесено строк: {n}")

    print("Сброс последовательностей (SERIAL/BIGSERIAL)...")
    reset_pg_sequences(pg_engine)
    print("Миграция завершена. Можно переключить DB_URL на PostgreSQL.")
    sqlite_engine.dispose()
    pg_engine.dispose()


if __name__ == "__main__":
    main()
