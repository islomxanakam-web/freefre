from aiogram import Bot

from config import CHANNELS


async def get_not_subscribed(bot: Bot, user_id: int) -> list:
    """Foydalanuvchi obuna bo'lmagan kanallar ro'yxatini qaytaradi."""
    not_subscribed = []
    for ch in CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=f"@{ch['username']}", user_id=user_id)
            if member.status in ("left", "kicked"):
                not_subscribed.append(ch)
        except Exception:
            # Bot kanalda admin emas yoki kanal topilmadi - xavfsizlik uchun
            # obuna bo'lmagan deb hisoblaymiz.
            not_subscribed.append(ch)
    return not_subscribed
