def get_message_threshold(level: int) -> int:
    if level <= 1:
        return 0
    return 5 * (level - 1) * level // 2


def get_xp_threshold(level: int) -> int:
    """Суммарный XP (порог) для достижения уровня level."""
    if level <= 5:
        return get_message_threshold(level)
    return get_message_threshold(5) + (level - 5) * 600


def level_from_total_xp(total_xp: int) -> int:
    """Уровень 5+ по суммарному XP. Один источник истины для высоких уровней."""
    for lvl in range(5, 1000):
        if total_xp < get_xp_threshold(lvl):
            return lvl - 1
    return 999


def calculate_level(message_count: int, xp: int, days_on_server: int) -> int:
    """
    Уровень по данным из БД.
    Уровни 1–4: по сообщениям, если XP ещё мало. Как только XP хватает на 5+ уровень — считаем только по XP.
    """
    # Если XP уже хватает на 5+ уровень — всегда считаем по XP (чтобы не сбросить на 3 уровень при малом message_count)
    if xp >= get_xp_threshold(5):
        return level_from_total_xp(xp)
    if message_count < get_message_threshold(5):  # 50 сообщений для 5 уровня
        for lvl in range(1, 6):
            if message_count < get_message_threshold(lvl):
                return lvl - 1
        return 4
    return level_from_total_xp(xp)

