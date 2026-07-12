import asyncio
import json
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramBadRequest

import config
import texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)


# ---------------------------------------------------------------------------
# Oddiy JSON asosidagi ma'lumotlar bazasi (foydalanuvchilar va statistika uchun)
# ---------------------------------------------------------------------------
def load_data() -> dict:
    if not os.path.exists(config.DATA_FILE):
        return {"users": {}, "total_starts": 0, "total_messages": 0}
    try:
        with open(config.DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return {"users": {}, "total_starts": 0, "total_messages": 0}


def save_data(data: dict) -> None:
    with open(config.DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def register_user(user) -> None:
    data = load_data()
    uid = str(user.id)
    is_new = uid not in data["users"]
    data["users"][uid] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_seen": datetime.now().isoformat(),
    }
    data["total_starts"] += 1
    save_data(data)


def register_message() -> None:
    data = load_data()
    data["total_messages"] = data.get("total_messages", 0) + 1
    save_data(data)


# ---------------------------------------------------------------------------
# Obunani tekshirish
# ---------------------------------------------------------------------------
async def check_subscription(user_id: int) -> bool:
    for channel in config.CHANNELS:
        try:
            member = await bot.get_chat_member(chat_id=channel, user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest as e:
            logger.warning("Kanal tekshiruvda xato (%s): %s", channel, e)
            return False
        except Exception as e:
            logger.warning("Kutilmagan xato (%s): %s", channel, e)
            return False
    return True


def subscribe_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for i, channel in enumerate(config.CHANNELS, start=1):
        kb.button(text=f"{i}️⃣ Kanalga o'tish", url=f"https://t.me/{channel.lstrip('@')}")
    kb.button(text="✅ Tekshirish", callback_data="check_sub")
    kb.adjust(1)
    return kb.as_markup()


SUBSCRIBE_TEXT = (
    "🔒 <b>Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling:</b>\n\n"
    + "\n".join(f"{i}. {c}" for i, c in enumerate(config.CHANNELS, start=1))
    + "\n\nObuna bo'lgach, <b>✅ Tekshirish</b> tugmasini bosing."
)


# ---------------------------------------------------------------------------
# Menyular
# ---------------------------------------------------------------------------
def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🆘 Yordam", callback_data="menu_help")
    kb.button(text="⚙️ Free Fire nastroykalar", callback_data="menu_nastroyka")
    kb.button(text="🆔 Free Fire niklar", callback_data="menu_niklar")
    kb.button(text="📚 Qo'llanmalar", callback_data="menu_qollanma")
    kb.button(text="💎 Premium bo'lim", callback_data="menu_premium")
    kb.button(text="🛠 Cheat va panellar", callback_data="menu_cheat")
    kb.button(text="🌐 Proxy server", callback_data="menu_proxy")
    if user_id == config.ADMIN_ID:
        kb.button(text="📊 Statistika", callback_data="menu_stats")
    kb.adjust(1)
    return kb.as_markup()


def back_keyboard(target: str) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔙 Orqaga", callback_data=target)
    return kb.as_markup()


def nastroyka_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="📱 iPhone nastroyka", callback_data="nastroyka_iphone")
    kb.button(text="📱 Samsung nastroyka", callback_data="nastroyka_samsung")
    kb.button(text="📱 Infinix nastroyka", callback_data="nastroyka_infinix")
    kb.button(text="📱 Tecno nastroyka", callback_data="nastroyka_tecno")
    kb.button(text="📱 Redmi nastroyka", callback_data="nastroyka_redmi")
    kb.button(text="📱 Honor nastroyka", callback_data="nastroyka_honor")
    kb.button(text="🔙 Orqaga", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def niklar_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥 Super niklar", callback_data="niklar_super")
    kb.button(text="🎮 Gamer niklar", callback_data="niklar_gamer")
    kb.button(text="🔙 Orqaga", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


def qollanma_menu_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🎯 Headshot qilish sirlari", callback_data="qollanma_headshot")
    kb.button(text="🏆 Rank tez ko'tarish maslahatlari", callback_data="qollanma_rank")
    kb.button(text="🛡 Gloo Wall texnikalari", callback_data="qollanma_gloo")
    kb.button(text="⚔️ Rush usullari", callback_data="qollanma_rush")
    kb.button(text="🎯 Snayper bo'yicha maslahatlar", callback_data="qollanma_snayper")
    kb.button(text="🔙 Orqaga", callback_data="main_menu")
    kb.adjust(1)
    return kb.as_markup()


NASTROYKA_TEXTS = {
    "nastroyka_iphone": texts.IPHONE_TEXT,
    "nastroyka_samsung": texts.SAMSUNG_TEXT,
    "nastroyka_infinix": texts.INFINIX_TEXT,
    "nastroyka_tecno": texts.TECNO_TEXT,
    "nastroyka_redmi": texts.REDMI_TEXT,
    "nastroyka_honor": texts.HONOR_TEXT,
}

QOLLANMA_TEXTS = {
    "qollanma_headshot": texts.HEADSHOT_SIRLARI,
    "qollanma_rank": texts.RANK_KOTARISH,
    "qollanma_gloo": texts.GLOO_WALL,
    "qollanma_rush": texts.RUSH_USULLARI,
    "qollanma_snayper": texts.SNAYPER_MASLAHAT,
}


# ---------------------------------------------------------------------------
# Yordamchi: adminga xabar yuborish
# ---------------------------------------------------------------------------
async def notify_admin(text: str) -> None:
    if not config.ADMIN_ID:
        logger.warning("ADMIN_ID sozlanmagan - adminga xabar yuborilmadi.")
        return
    try:
        await bot.send_message(config.ADMIN_ID, text)
    except Exception as e:
        logger.warning("Adminga xabar yuborishda xato: %s", e)


def user_info_block(user) -> str:
    username = f"@{user.username}" if user.username else "yo'q"
    return (
        f"👤 Ism: {user.full_name}\n"
        f"🆔 ID: <code>{user.id}</code>\n"
        f"🔗 Username: {username}"
    )


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message):
    user = message.from_user
    register_user(user)

    await notify_admin(f"🆕 <b>Yangi start bosildi!</b>\n\n{user_info_block(user)}")

    if not await check_subscription(user.id):
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_keyboard())
        return

    await message.answer(
        f"👋 Salom, {user.first_name}!\n\nQuyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard(user.id),
    )


# ---------------------------------------------------------------------------
# Obunani tekshirish tugmasi
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "check_sub")
async def check_sub_handler(call: CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.edit_text(
            f"✅ Obuna tasdiqlandi!\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard(call.from_user.id),
        )
    else:
        await call.answer(
            "❗️Siz hali barcha kanallarga obuna bo'lmadingiz!", show_alert=True
        )


# ---------------------------------------------------------------------------
# Obuna middleware o'rniga: har bir callback/message'da tekshirish
# ---------------------------------------------------------------------------
async def ensure_subscribed_call(call: CallbackQuery) -> bool:
    if await check_subscription(call.from_user.id):
        return True
    await call.answer("❗️Avval kanallarga obuna bo'ling!", show_alert=True)
    await call.message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_keyboard())
    return False


# ---------------------------------------------------------------------------
# Asosiy menyu
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(
        "Quyidagi bo'limlardan birini tanlang:",
        reply_markup=main_menu_keyboard(call.from_user.id),
    )


@router.callback_query(F.data == "menu_help")
async def menu_help_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(texts.HELP_TEXT, reply_markup=back_keyboard("main_menu"))


@router.callback_query(F.data == "menu_nastroyka")
async def menu_nastroyka_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(
        "⚙️ <b>Free Fire nastroykalar</b>\n\nTelefon modelingizni tanlang:",
        reply_markup=nastroyka_menu_keyboard(),
    )


@router.callback_query(F.data.in_(NASTROYKA_TEXTS.keys()))
async def nastroyka_detail_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    text = NASTROYKA_TEXTS[call.data]
    await call.message.edit_text(text, reply_markup=back_keyboard("menu_nastroyka"))


@router.callback_query(F.data == "menu_niklar")
async def menu_niklar_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(
        "🆔 <b>Free Fire niklar</b>\n\nQaysi turdagi nik kerak?",
        reply_markup=niklar_menu_keyboard(),
    )


@router.callback_query(F.data == "niklar_super")
async def niklar_super_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    text = f"🔥 <b>Super niklar</b>\n\n<code>{texts.SUPER_NIKLAR}</code>\n\n👆 Nikka bosing - nusxa olinadi!"
    await call.message.edit_text(text, reply_markup=back_keyboard("menu_niklar"))


@router.callback_query(F.data == "niklar_gamer")
async def niklar_gamer_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    text = f"🎮 <b>Gamer niklar</b>\n\n<code>{texts.GAMER_NIKLAR}</code>\n\n👆 Nikka bosing - nusxa olinadi!"
    await call.message.edit_text(text, reply_markup=back_keyboard("menu_niklar"))


@router.callback_query(F.data == "menu_qollanma")
async def menu_qollanma_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(
        "📚 <b>Qo'llanmalar</b>\n\nMavzuni tanlang:",
        reply_markup=qollanma_menu_keyboard(),
    )


@router.callback_query(F.data.in_(QOLLANMA_TEXTS.keys()))
async def qollanma_detail_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    text = QOLLANMA_TEXTS[call.data]
    await call.message.edit_text(text, reply_markup=back_keyboard("menu_qollanma"))


@router.callback_query(F.data == "menu_premium")
async def menu_premium_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(texts.PREMIUM_TEXT, reply_markup=back_keyboard("main_menu"))


@router.callback_query(F.data == "menu_cheat")
async def menu_cheat_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(texts.CHEAT_PANEL_TEXT, reply_markup=back_keyboard("main_menu"))


@router.callback_query(F.data == "menu_proxy")
async def menu_proxy_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(texts.PROXY_TEXT, reply_markup=back_keyboard("main_menu"))


@router.callback_query(F.data == "menu_stats")
async def menu_stats_handler(call: CallbackQuery):
    if call.from_user.id != config.ADMIN_ID:
        await call.answer("❌ Bu bo'lim faqat admin uchun.", show_alert=True)
        return
    data = load_data()
    total_users = len(data.get("users", {}))
    total_starts = data.get("total_starts", 0)
    total_messages = data.get("total_messages", 0)
    text = (
        "📊 <b>Bot statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n"
        f"🔁 Jami /start bosilgan: <b>{total_starts}</b>\n"
        f"✉️ Jami yozilgan xabarlar: <b>{total_messages}</b>"
    )
    await call.message.edit_text(text, reply_markup=back_keyboard("main_menu"))


# ---------------------------------------------------------------------------
# Har qanday matnli xabarni adminga forward qilish (obunachi bo'lganlardan)
# ---------------------------------------------------------------------------
@router.message(F.text)
async def forward_to_admin(message: Message):
    user = message.from_user

    if user.id == config.ADMIN_ID:
        return  # admin o'z-o'ziga forward qilinmaydi

    if not await check_subscription(user.id):
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_keyboard())
        return

    register_message()
    text = f"✉️ <b>Yangi xabar!</b>\n\n{user_info_block(user)}\n\n💬 {message.text}"
    await notify_admin(text)


# ---------------------------------------------------------------------------
async def main():
    if config.ADMIN_ID == 0:
        logger.warning(
            "DIQQAT: ADMIN_ID sozlanmagan! Statistika va bildirishnomalar ishlamaydi. "
            "config.py yoki Railway Environment Variables'da ADMIN_ID ni sozlang."
        )
    logger.info("Bot ishga tushmoqda...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
