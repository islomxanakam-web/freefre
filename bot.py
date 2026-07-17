import asyncio
import json
import logging
import os
from datetime import datetime

from aiogram import Bot, Dispatcher, F, Router
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    CallbackQuery,
    Message,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.exceptions import TelegramBadRequest

import config
import texts

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())
router = Router()
dp.include_router(router)


class BroadcastStates(StatesGroup):
    waiting_for_post = State()


class FFIDStates(StatesGroup):
    waiting_for_id = State()


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
    data["users"][uid] = {
        "id": user.id,
        "username": user.username,
        "first_name": user.first_name,
        "last_seen": datetime.now().isoformat(),
    }
    data["total_starts"] = data.get("total_starts", 0) + 1
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
            member = await bot.get_chat_member(chat_id=channel["username"], user_id=user_id)
            if member.status in ("left", "kicked"):
                return False
        except TelegramBadRequest as e:
            logger.warning("Tekshiruvda xato (%s): %s", channel["username"], e)
            return False
        except Exception as e:
            logger.warning("Kutilmagan xato (%s): %s", channel["username"], e)
            return False
    return True


def _btn(text: str, callback_data: str) -> InlineKeyboardButton:
    return InlineKeyboardButton(text=text, callback_data=callback_data)


def subscribe_keyboard() -> InlineKeyboardMarkup:
    channel_buttons = [
        InlineKeyboardButton(
            text=f"{c['label']} 🔗",
            url=f"https://t.me/{c['username'].lstrip('@')}",
        )
        for c in config.CHANNELS
    ]
    rows = [channel_buttons[i:i + 2] for i in range(0, len(channel_buttons), 2)]
    rows.append([_btn("✅ A'zo bo'ldim, tekshirish", "check_sub")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def build_subscribe_text() -> str:
    lines = "\n".join(f"🔸 {c['label']}: {c['username']}" for c in config.CHANNELS)
    return (
        "🎮 <b>FREE FIRE BOT'ga xush kelibsiz!</b>\n\n"
        "Botdan foydalanish uchun avval quyidagilarga a'zo bo'lishingiz kerak 👇\n\n"
        f"{lines}\n\n"
        "✅ Barchasiga a'zo bo'lgach, pastdagi tugmani bosing."
    )


SUBSCRIBE_TEXT = build_subscribe_text()


# ---------------------------------------------------------------------------
# Menyular
# ---------------------------------------------------------------------------
def main_menu_keyboard(user_id: int) -> InlineKeyboardMarkup:
    rows = [
        [_btn("🆘 Yordam", "menu_help"), _btn("⚙️ Nastroykalar", "menu_nastroyka")],
        [_btn("🆔 Niklar", "menu_niklar"), _btn("📚 Qo'llanmalar", "menu_qollanma")],
        [_btn("💎 Premium bo'lim", "menu_premium"), _btn("🛠 Cheat va panellar", "menu_cheat")],
        [_btn("🎮 Mening FF ID'im", "menu_ffid"), _btn("🌟 Pro versiya", "menu_pro")],
        [_btn("🌐 Proxy server", "menu_proxy")],
    ]
    if user_id == config.ADMIN_ID:
        rows.append([_btn("📊 Statistika", "menu_stats"), _btn("📢 Post yuborish", "menu_broadcast")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def back_keyboard(target: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[_btn("🔙 Orqaga", target)]])


def nastroyka_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [_btn("📱 iPhone", "nastroyka_iphone"), _btn("📱 Samsung", "nastroyka_samsung")],
        [_btn("📱 Infinix", "nastroyka_infinix"), _btn("📱 Tecno", "nastroyka_tecno")],
        [_btn("📱 Redmi", "nastroyka_redmi"), _btn("📱 Honor", "nastroyka_honor")],
        [_btn("🔙 Orqaga", "main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def niklar_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [_btn("🔥 Super niklar", "niklar_super"), _btn("🎮 Gamer niklar", "niklar_gamer")],
        [_btn("🔙 Orqaga", "main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


def qollanma_menu_keyboard() -> InlineKeyboardMarkup:
    rows = [
        [_btn("🎯 Headshot sirlari", "qollanma_headshot"), _btn("🏆 Rank ko'tarish", "qollanma_rank")],
        [_btn("🛡 Gloo Wall", "qollanma_gloo"), _btn("⚔️ Rush usullari", "qollanma_rush")],
        [_btn("🎯 Snayper maslahat", "qollanma_snayper")],
        [_btn("🔙 Orqaga", "main_menu")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


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
# Yordamchi funksiyalar
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


async def ensure_subscribed_call(call: CallbackQuery) -> bool:
    if await check_subscription(call.from_user.id):
        return True
    await call.answer("❗️Avval kanallarga obuna bo'ling!", show_alert=True)
    await call.message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_keyboard())
    return False


# ---------------------------------------------------------------------------
# /start
# ---------------------------------------------------------------------------
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    register_user(user)

    await notify_admin(f"🆕 <b>Yangi start bosildi!</b>\n\n{user_info_block(user)}")

    if not await check_subscription(user.id):
        await message.answer(SUBSCRIBE_TEXT, reply_markup=subscribe_keyboard())
        return

    await message.answer(
        f"👋 Salom, {user.first_name}!\n\n"
        "🎮 <b>Free Fire botiga xush kelibsiz!</b>\n"
        "Quyidagi bo'limlardan birini tanlang 👇",
        reply_markup=main_menu_keyboard(user.id),
    )


@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=main_menu_keyboard(message.from_user.id))


# ---------------------------------------------------------------------------
# Obunani tekshirish tugmasi
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "check_sub")
async def check_sub_handler(call: CallbackQuery):
    if await check_subscription(call.from_user.id):
        await call.message.edit_text(
            "✅ <b>Obuna tasdiqlandi!</b>\n\nQuyidagi bo'limlardan birini tanlang:",
            reply_markup=main_menu_keyboard(call.from_user.id),
        )
    else:
        await call.answer(
            "❗️Siz hali barcha kanal/guruhlarga obuna bo'lmadingiz!", show_alert=True
        )


# ---------------------------------------------------------------------------
# Asosiy menyu va bo'limlar
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "main_menu")
async def main_menu_handler(call: CallbackQuery, state: FSMContext):
    await state.clear()
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


@router.callback_query(F.data == "menu_pro")
async def menu_pro_handler(call: CallbackQuery):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(texts.PRO_VERSION_TEXT, reply_markup=back_keyboard("main_menu"))


# ---------------------------------------------------------------------------
# Mening FF ID'im
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "menu_ffid")
async def menu_ffid_handler(call: CallbackQuery, state: FSMContext):
    if not await ensure_subscribed_call(call):
        return
    await call.message.edit_text(
        "🎮 <b>Mening FF ID'im</b>\n\n"
        "📩 Free Fire ID'ingizni (raqamini) pastga yozib yuboring 👇\n\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=back_keyboard("main_menu"),
    )
    await state.set_state(FFIDStates.waiting_for_id)


@router.message(StateFilter(FFIDStates.waiting_for_id))
async def ffid_receive_handler(message: Message, state: FSMContext):
    await state.clear()
    user = message.from_user
    register_message()
    await notify_admin(
        f"🎮 <b>Yangi FF ID so'rovi!</b>\n\n{user_info_block(user)}\n\n🆔 FF ID: <code>{message.text}</code>"
    )
    await message.answer(
        "✅ <b>Qabul qilindi!</b>\n\n"
        "Free Fire ID'ingiz haqida ma'lumot tez orada admin tomonidan yuboriladi.",
        reply_markup=main_menu_keyboard(user.id),
    )


# ---------------------------------------------------------------------------
# Statistika (faqat admin)
# ---------------------------------------------------------------------------
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
# Post yuborish / Barchaga xabar (faqat admin)
# ---------------------------------------------------------------------------
@router.callback_query(F.data == "menu_broadcast")
async def menu_broadcast_handler(call: CallbackQuery, state: FSMContext):
    if call.from_user.id != config.ADMIN_ID:
        await call.answer("❌ Bu bo'lim faqat admin uchun.", show_alert=True)
        return
    await call.message.edit_text(
        "📢 <b>Post yuborish</b>\n\n"
        "Barcha foydalanuvchilarga yubormoqchi bo'lgan xabaringizni yuboring "
        "(matn, rasm, video - istalgan turda bo'lishi mumkin).\n\n"
        "⚠️ Xabar aynan siz yuborgan ko'rinishda hammaga jo'natiladi.\n"
        "Bekor qilish uchun /cancel yozing.",
        reply_markup=back_keyboard("main_menu"),
    )
    await state.set_state(BroadcastStates.waiting_for_post)


@router.message(StateFilter(BroadcastStates.waiting_for_post))
async def broadcast_receive_handler(message: Message, state: FSMContext):
    if message.from_user.id != config.ADMIN_ID:
        return

    await state.clear()
    data = load_data()
    user_ids = list(data.get("users", {}).keys())

    status = await message.answer(f"⏳ Yuborilmoqda... (0/{len(user_ids)})")
    sent, failed = 0, 0
    for uid_str in user_ids:
        try:
            await message.copy_to(chat_id=int(uid_str))
            sent += 1
        except Exception as e:
            failed += 1
            logger.warning("Broadcast xato (%s): %s", uid_str, e)
        await asyncio.sleep(0.05)  # flood limitga tushmaslik uchun

    await status.edit_text(
        f"✅ <b>Yuborish yakunlandi!</b>\n\n"
        f"✅ Yuborildi: <b>{sent}</b> ta\n"
        f"❌ Yuborilmadi: <b>{failed}</b> ta"
    )
    await message.answer("Bosh menyu:", reply_markup=main_menu_keyboard(message.from_user.id))


# ---------------------------------------------------------------------------
# Har qanday boshqa matnli xabarni adminga forward qilish
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
