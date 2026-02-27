from __future__ import annotations

import io
import os
from typing import Optional

# Шрифт: сначала папка fonts в корне проекта, затем системные (для кириллицы)
_FONTS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fonts"))
_FONT_CANDIDATES = ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "dejavu.ttf")
# Запас: системные шрифты с кириллицей (если в проекте нет fonts/)
_WINDOWS_FONTS = (
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "arial.ttf"),
    os.path.join(os.environ.get("WINDIR", "C:\\Windows"), "Fonts", "Arial.ttf"),
)
_LINUX_MAC_FONTS = (
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/usr/share/fonts/TTF/DejaVuSans.ttf",
    "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/Library/Fonts/Arial.ttf",
)


def _get_font_path():
    """Путь к ttf-шрифту: сначала fonts в проекте, потом системный (Arial и т.д.)."""
    for name in _FONT_CANDIDATES:
        path = os.path.normpath(os.path.join(_FONTS_DIR, name))
        if os.path.isfile(path):
            return path
    # Если точных имён нет — ищем любой .ttf в папке (на случай другого имени/регистра)
    if os.path.isdir(_FONTS_DIR):
        try:
            for name in os.listdir(_FONTS_DIR):
                if name.lower().endswith(".ttf"):
                    path = os.path.join(_FONTS_DIR, name)
                    if os.path.isfile(path):
                        return path
        except OSError:
            pass
    for path in _WINDOWS_FONTS:
        if os.path.isfile(path):
            return path
    for path in _LINUX_MAC_FONTS:
        if os.path.isfile(path):
            return path
    return None


# При первом запуске без папки fonts — создаём её (без вывода в консоль)
if not os.path.isdir(_FONTS_DIR):
    try:
        os.makedirs(_FONTS_DIR, exist_ok=True)
    except OSError:
        pass


def _load_font(size: int):
    """Загружает шрифт для размера size. Читает файл в память, чтобы путь не мешал на Windows."""
    path = _get_font_path()
    if not path:
        return ImageFont.load_default()
    try:
        with open(path, "rb") as f:
            font_bytes = f.read()
        return ImageFont.truetype(io.BytesIO(font_bytes), size, encoding="unic")
    except Exception:
        return ImageFont.load_default()

import aiohttp
import discord
from discord import Activity, ActivityType, app_commands
from discord.ext import commands, tasks
from PIL import Image, ImageDraw, ImageFont

from app.core.config import Config
from app.core.guild_cache import sync_all as guild_cache_sync
from app.core.levels import calculate_level, get_message_threshold, get_xp_threshold
from app.db.database import Database


class Bot(commands.Bot):
    def __init__(self):
        intents = discord.Intents.default()
        intents.members = True
        intents.message_content = True
        intents.presences = True
        super().__init__(command_prefix="!", intents=intents)
        self.db = Database()
        self.token = Config.DISCORD_TOKEN

    async def setup_hook(self):
        # guilds может быть пустым на старте — но логика у тебя уже обкатана
        for guild in self.guilds:
            print(f"Инициализация пользователей на сервере: {guild.name}")
            self.db.add_all_users_to_guild(guild.id, guild.members)
        self.add_view(RoleSelectView())
        self.update_days.start()

    def _build_guild_cache(self):
        """Собрать кэш гильдий/каналов/ролей для веб-API."""
        guilds = []
        channels = {}
        roles = {}
        for guild in self.guilds:
            guilds.append({
                "id": guild.id,
                "name": guild.name,
                "icon": str(guild.icon.url) if guild.icon else None,
            })
            channels[guild.id] = [
                {"id": c.id, "name": c.name, "type": getattr(c.type, "value", 0)}
                for c in guild.channels
            ]
            roles[guild.id] = [
                {"id": r.id, "name": r.name}
                for r in guild.roles
                if not r.is_default()
            ]
        guild_cache_sync(guilds, channels, roles)

    async def on_ready(self):
        status_type = getattr(ActivityType, Config.BOT_STATUS_TYPE, ActivityType.listening)
        status_name = Config.BOT_STATUS_NAME or "ALBLAK 52"
        await self.change_presence(activity=Activity(type=status_type, name=status_name))
        for guild in self.guilds:
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)
            print(f"Команды синхронизированы для сервера: {guild.name}")
        self._build_guild_cache()
        print("Бот готов к работе! Слэш-команды синхронизированы.")

    async def on_guild_join(self, guild):
        self._build_guild_cache()

    async def on_guild_remove(self, guild):
        self._build_guild_cache()

    @tasks.loop(hours=24)
    async def update_days(self):
        for guild in self.guilds:
            users = self.db.get_users_in_guild(guild.id)
            for user_level in users:
                new_days = user_level.days_on_server + 1
                xp_gain = (new_days // 2) * 15 - (user_level.days_on_server // 2) * 15
                new_xp = user_level.xp + xp_gain

                current_level = user_level.level
                new_level = calculate_level(user_level.message_count, new_xp, new_days)
                new_level = max(current_level, new_level)

                self.db.update_user_level(
                    guild.id,
                    user_level.user_id,
                    message_count=user_level.message_count,
                    level=new_level,
                    xp=new_xp,
                    days_on_server=new_days,
                )

                if new_level > current_level and new_level > 5:
                    config = self.db.get_guild_config(guild.id)
                    if config and config["level_channel_id"]:
                        channel = guild.get_channel(config["level_channel_id"])
                        if channel:
                            member = guild.get_member(user_level.user_id)
                            if member:
                                await channel.send(
                                    f"Красава брад {member.mention}! Ты достиг нового уровня {new_level} за время на сервере!"
                                )

    @update_days.before_loop
    async def before_update_days(self):
        await self.wait_until_ready()

    async def on_member_join(self, member):
        if member.bot:
            return

        self.db.get_user_level(member.guild.id, member.id)

        config = self.db.get_guild_config(member.guild.id)
        if config and config["welcome_channel_id"]:
            channel = member.guild.get_channel(config["welcome_channel_id"])
            role = member.guild.get_role(config["welcome_role_id"])

            if channel:
                member_count = member.guild.member_count
                image = await self.create_welcome_image(member, member_count)
                message = f"С нами новый брад {member.mention}, Добро пожаловать на сервер **{member.guild.name}**"
                if image:
                    file = discord.File(image, filename="welcome.png")
                    await channel.send(content=message, file=file)
                else:
                    await channel.send(content=message)

            if role:
                await member.add_roles(role)

    async def on_message(self, message):
        if message.author.bot:
            return

        user_level = self.db.get_user_level(message.guild.id, message.author.id)
        user_level.message_count += 1

        xp_gain = 10 if user_level.level >= 5 else 0
        user_level.xp += xp_gain

        new_level = calculate_level(user_level.message_count, user_level.xp, user_level.days_on_server)
        if new_level > user_level.level:
            user_level.level = new_level
            config = self.db.get_guild_config(message.guild.id)
            if config and config["level_channel_id"]:
                channel = message.guild.get_channel(config["level_channel_id"])
                if channel:
                    await channel.send(f"Красава брад {message.author.mention}! Ты достиг нового уровня {user_level.level}!")

        self.db.update_user_level(
            message.guild.id,
            message.author.id,
            message_count=user_level.message_count,
            level=user_level.level,
            xp=user_level.xp,
            days_on_server=user_level.days_on_server,
        )

    async def create_welcome_image(self, member, member_count):
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url)) as resp:
                if resp.status != 200:
                    return None
                avatar_data = await resp.read()

        avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar = avatar.resize((200, 200), Image.LANCZOS)

        mask = Image.new("L", (200, 200), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 200, 200), fill=255)

        avatar_circle = Image.new("RGBA", (200, 200), (0, 0, 0, 0))
        avatar_circle.paste(avatar, (0, 0), mask)

        background = Image.new("RGBA", (600, 300), (0, 0, 0, 255))
        draw_border = ImageDraw.Draw(background)
        draw_border.ellipse((195, 15, 405, 225), outline=(255, 255, 255, 255), width=5)
        background.paste(avatar_circle, (200, 20), avatar_circle)

        draw = ImageDraw.Draw(background)
        font = _load_font(30)
        small_font = _load_font(20)

        text1 = f"{member.name} уже на нашем сервере"
        draw.text((300 - draw.textlength(text1, font=font) / 2, 230), text1, fill=(255, 255, 255, 255), font=font)

        text2 = f"БРАД #{member_count}"
        draw.text(
            (300 - draw.textlength(text2, font=small_font) / 2, 270),
            text2,
            fill=(255, 255, 255, 255),
            font=small_font,
        )

        buffer = io.BytesIO()
        background.save(buffer, format="PNG")
        buffer.seek(0)
        return buffer

    async def create_level_image(self, member, user_level):
        async with aiohttp.ClientSession() as session:
            async with session.get(str(member.display_avatar.url)) as resp:
                if resp.status != 200:
                    return None
                avatar_data = await resp.read()

        avatar = Image.open(io.BytesIO(avatar_data)).convert("RGBA")
        avatar = avatar.resize((100, 100), Image.LANCZOS)

        mask = Image.new("L", (100, 100), 0)
        draw_mask = ImageDraw.Draw(mask)
        draw_mask.ellipse((0, 0, 100, 100), fill=255)
        avatar.putalpha(mask)

        background = Image.new("RGBA", (600, 150), (0, 0, 0, 255))
        draw_border = ImageDraw.Draw(background)
        draw_border.ellipse((15, 20, 125, 130), outline=(255, 255, 255, 255), width=3)
        background.paste(avatar, (20, 25), avatar)

        status_colors = {
            discord.Status.online: (67, 181, 129, 255),
            discord.Status.offline: (67, 181, 129, 255),
            discord.Status.idle: (67, 181, 129, 255),
            discord.Status.dnd: (67, 181, 129, 255),
        }
        status = member.status
        status_color = status_colors.get(status, (67, 181, 129, 255))
        draw = ImageDraw.Draw(background)
        draw.ellipse((95, 100, 115, 120), fill=status_color)

        font = _load_font(30)
        small_font = _load_font(20)

        draw.text((140, 20), member.name, fill=(255, 255, 255, 255), font=font)

        rank = sum(1 for u in self.db.get_users_in_guild(member.guild.id) if u.level > user_level.level) + 1
        level_text = f"РАНГ #{rank} УРОВЕНЬ {user_level.level}"
        draw.text((140, 60), level_text, fill=(186, 85, 211, 255), font=small_font)

        next_level = min(user_level.level + 1, 999)
        current_threshold = get_message_threshold(user_level.level) if user_level.level < 5 else get_xp_threshold(user_level.level)
        next_threshold = get_message_threshold(next_level) if next_level <= 5 else get_xp_threshold(next_level)

        if user_level.level < 5:
            progress = user_level.message_count / next_threshold if next_threshold > 0 else 1
            xp_text = f"{user_level.message_count}/{next_threshold} сообщений"
        else:
            current_progress = max(0, user_level.xp - current_threshold)
            required_xp = next_threshold - current_threshold
            progress = current_progress / required_xp if required_xp > 0 else 1
            xp_text = f"{user_level.xp}/{next_threshold} XP"

        draw.text((140, 90), xp_text, fill=(255, 255, 255, 255), font=small_font)

        bar_width = 400
        bar_height = 20
        filled_width = int(bar_width * min(progress, 1))

        draw.rounded_rectangle((140, 120, 140 + bar_width, 120 + bar_height), radius=10, fill=(128, 128, 128, 255))
        if filled_width > 0:
            draw.rounded_rectangle(
                (140, 120, 140 + filled_width, 120 + bar_height), radius=10, fill=(186, 85, 211, 255)
            )

        buffer = io.BytesIO()
        background.save(buffer, format="PNG", quality=95)
        buffer.seek(0)
        return buffer


bot = Bot()


@app_commands.command(name="level", description="Посмотреть свой уровень")
async def level(interaction: discord.Interaction):
    await interaction.response.defer()
    user_level = bot.db.get_user_level(interaction.guild.id, interaction.user.id)
    image = await bot.create_level_image(interaction.user, user_level)
    if not image:
        await interaction.followup.send("Не удалось собрать картинку уровня (аватар недоступен).", ephemeral=True)
        return
    file = discord.File(image, filename="level.png")

    config = bot.db.get_guild_config(interaction.guild.id)
    if config and config["level_channel_id"]:
        channel = interaction.guild.get_channel(config["level_channel_id"])
        if channel:
            await channel.send(file=file)
            await interaction.followup.send(f"Ваш уровень отправлен в {channel.mention}!", ephemeral=True)
        else:
            await interaction.followup.send(file=file)
    else:
        await interaction.followup.send(file=file)


@app_commands.command(name="setwelcome", description="Установить канал и роль для приветствия")
@app_commands.describe(channel="Канал для приветствия", role="Роль для новых пользователей")
async def set_welcome(interaction: discord.Interaction, channel: discord.TextChannel, role: discord.Role):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("У вас нет прав администратора для этой команды!", ephemeral=True)
        return

    bot.db.update_guild_config(interaction.guild.id, channel_id=channel.id, role_id=role.id)
    await interaction.response.send_message(
        f"Настройки обновлены! Канал приветствия: {channel.mention}, Роль: {role.name}",
        ephemeral=True,
    )


@app_commands.command(name="top", description="Показать топ-10 пользователей по уровню")
async def top(interaction: discord.Interaction):
    await interaction.response.defer()
    users = bot.db.get_users_in_guild(interaction.guild.id)
    top_users = sorted(users, key=lambda x: (x.level, x.xp), reverse=True)[:10]
    embed = discord.Embed(title="Топ-10 пользователей по уровню", color=discord.Color.purple())
    for i, user_level in enumerate(top_users, 1):
        member = interaction.guild.get_member(user_level.user_id)
        if member:
            embed.add_field(
                name=f"{i}. {member.name}",
                value=f"Уровень: {user_level.level} | XP: {user_level.xp}",
                inline=False,
            )
    await interaction.followup.send(embed=embed)


@app_commands.command(name="help", description="Показать список команд и описание админки")
async def help_command(interaction: discord.Interaction):
    embed = discord.Embed(
        title="Информация по командам",
        description="Вот список доступных команд и информация!",
        color=discord.Color.blue(),
    )

    embed.add_field(name="/level", value="Показывает ваш текущий уровень и прогресс.", inline=False)
    embed.add_field(name="/top", value="Показывает топ-10 пользователей по уровню.", inline=False)
    embed.add_field(name="/help", value="Показывает это сообщение.", inline=False)
    embed.add_field(
        name="/setwelcome",
        value="Устанавливает канал и роль для приветствия новых пользователей (только для админов).",
        inline=False,
    )
    embed.add_field(
        name="/setup_roles",
        value="Отправляет сообщение для выбора ролей в настроенный канал (только для админов).",
        inline=False,
    )

    await interaction.response.send_message(embed=embed, ephemeral=True)


def _build_role_options(
    guild: discord.Guild,
    selectable_role_ids: list,
    current_member_role_ids: Optional[set] = None,
) -> list[discord.SelectOption]:
    """Собирает опции для меню ролей. Если передан current_member_role_ids — помечает текущие роли как выбранные (default=True)."""
    current_member_role_ids = current_member_role_ids or set()
    options = []
    for rid in selectable_role_ids:
        role = guild.get_role(int(rid))
        if not role:
            continue
        options.append(
            discord.SelectOption(
                label=role.name,
                value=str(role.id),
                default=(role.id in current_member_role_ids),
            )
        )
    return options


class RoleSelectView(discord.ui.View):
    def __init__(self, role_options: list[discord.SelectOption] | None = None):
        super().__init__(timeout=None)
        options = role_options or []
        self.add_item(
            RoleSelectMenu(
                options=options,
                custom_id="role_select_menu",
            )
        )


class RoleSelectMenu(discord.ui.Select):
    def __init__(self, options: list[discord.SelectOption], custom_id: str = "role_select_menu"):
        super().__init__(
            placeholder="Выберите одну или несколько ролей...",
            options=options,
            min_values=0,
            max_values=min(len(options), 25),
            custom_id=custom_id,
        )

    async def callback(self, interaction: discord.Interaction):
        config = bot.db.get_guild_config(interaction.guild.id)
        if not config:
            await interaction.response.send_message("Роли не настроены. Настройте через API/фронтенд.", ephemeral=True)
            return

        selectable_ids = {int(r) for r in config["selectable_roles"]}
        selected_roles = []
        for rid in self.values:
            r = interaction.guild.get_role(int(rid))
            if r is not None:
                selected_roles.append(r)
        selected_ids = {r.id for r in selected_roles}

        # Убираем роли, которые пользователь снял в меню
        member_role_ids = {r.id for r in interaction.user.roles}
        roles_to_remove = [
            r for r in interaction.user.roles
            if r.id in selectable_ids and r.id not in selected_ids
        ]
        # Добавляем только те выбранные роли, которых ещё нет
        roles_to_add = [r for r in selected_roles if r.id not in member_role_ids]

        if roles_to_remove:
            await interaction.user.remove_roles(*roles_to_remove)
        if roles_to_add:
            await interaction.user.add_roles(*roles_to_add)

        # Роли после обновления считаем из выбора, а не из user.roles (там может быть старый кэш)
        current_role_ids = selected_ids & selectable_ids
        current_names = [
            interaction.guild.get_role(rid).name
            for rid in current_role_ids
            if interaction.guild.get_role(rid)
        ]
        removed_names = [r.name for r in roles_to_remove]

        embed = discord.Embed(
            title="✅ Роли обновлены",
            color=discord.Color.green(),
        )
        embed.add_field(
            name="Ваши роли",
            value=", ".join(current_names) if current_names else "— нет выбранных ролей",
            inline=False,
        )
        if removed_names:
            embed.add_field(
                name="Снятые роли",
                value=", ".join(removed_names),
                inline=False,
            )
        await interaction.response.send_message(embed=embed, ephemeral=True)


@app_commands.command(name="setup_roles", description="Настроить сообщение для выбора ролей")
async def setup_roles(interaction: discord.Interaction):
    if not interaction.user.guild_permissions.administrator:
        await interaction.response.send_message("У вас нет прав администратора для этой команды!", ephemeral=True)
        return

    config = bot.db.get_guild_config(interaction.guild.id)
    if not config or not config["role_select_channel_id"] or not config["selectable_roles"]:
        await interaction.response.send_message(
            "Сначала настройте канал и роли для выбора через API или будущий фронтенд.",
            ephemeral=True,
        )
        return

    channel = interaction.guild.get_channel(config["role_select_channel_id"])
    if not channel:
        await interaction.response.send_message("Указанный канал не найден!", ephemeral=True)
        return

    role_options = _build_role_options(interaction.guild, config["selectable_roles"])
    if not role_options:
        await interaction.response.send_message("Нет доступных ролей для выбора!", ephemeral=True)
        return

    embed = discord.Embed(
        title="🎭 Выбор ролей",
        description="Выберите **одну или несколько ролей** в меню ниже.\nОтмеченные галочкой уже выданы вам.",
        color=discord.Color.blurple(),
    )
    embed.set_footer(text="Роли можно менять в любое время.")
    view = RoleSelectView(role_options=role_options)
    await channel.send(embed=embed, view=view)
    await interaction.response.send_message(f"Сообщение для выбора ролей отправлено в {channel.mention}!", ephemeral=True)


bot.tree.add_command(level)
bot.tree.add_command(set_welcome)
bot.tree.add_command(top)
bot.tree.add_command(help_command)
bot.tree.add_command(setup_roles)

