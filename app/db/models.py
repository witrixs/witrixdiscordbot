from sqlalchemy import BigInteger, Column, Integer, String, Text, UniqueConstraint

from app.db.base import Base


class AdminUser(Base):
    __tablename__ = "admin_users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(255), nullable=False, unique=True)
    password_hash = Column(String(255), nullable=False)


class GuildConfig(Base):
    __tablename__ = "guild_config"

    # Discord Snowflake IDs -> BIGINT (PostgreSQL)
    guild_id = Column(BigInteger, primary_key=True)
    welcome_channel_id = Column(BigInteger, nullable=True)
    welcome_role_id = Column(BigInteger, nullable=True)
    level_channel_id = Column(BigInteger, nullable=True)
    role_select_channel_id = Column(BigInteger, nullable=True)

    # кросс-БД вариант: храним "1,2,3" (в будущем можно мигрировать на JSON/ARRAY)
    selectable_roles = Column(Text, nullable=True)


class UserLevel(Base):
    __tablename__ = "user_levels"
    __table_args__ = (UniqueConstraint("guild_id", "user_id", name="uq_user_levels_guild_user"),)

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    guild_id = Column(BigInteger, nullable=False, index=True)
    user_id = Column(BigInteger, nullable=False, index=True)

    message_count = Column(Integer, default=0, nullable=False)
    level = Column(Integer, default=1, nullable=False)
    xp = Column(Integer, default=0, nullable=False)
    days_on_server = Column(Integer, default=0, nullable=False)

