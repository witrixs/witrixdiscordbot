def get_message_threshold(level: int) -> int:
    if level <= 1:
        return 0
    return 5 * (level - 1) * level // 2


def get_xp_threshold(level: int) -> int:
    if level <= 5:
        return get_message_threshold(level)
    return get_message_threshold(5) + (level - 5) * 600


def calculate_level(message_count: int, xp: int, days_on_server: int) -> int:
    if message_count < get_message_threshold(5):
        for lvl in range(1, 6):
            threshold = get_message_threshold(lvl)
            if message_count < threshold:
                return lvl - 1
        return 4

    total_xp = xp + (days_on_server // 2) * 15
    for lvl in range(5, 1000):
        threshold = get_xp_threshold(lvl)
        if total_xp < threshold:
            return lvl - 1
    return 999

