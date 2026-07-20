from aiogram import Router, Bot, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

import database as db
from config import MENU_TITLES, CONTENT_MAP, MAIN_MENU, ADMIN_IDS, ADMIN_USERNAME
from keyboards import (
    channels_kb,
    main_menu_reply_kb,
    submenu_kb,
    content_view_kb,
    CONTACT_BTN_TEXT,
)
from subscription import get_not_subscribed

router = Router()

TEXT_TO_KEY = {item["title"]: item["key"] for item in MAIN_MENU}


async def register_and_notify(bot: Bot, user_id: int, username: str, full_name: str):
    """Agar foydalanuvchi yangi bo'lsa, bazaga qo'shadi va barcha adminlarga xabar beradi."""
    if db.user_exists(user_id):
        return
    total = db.add_user(user_id, username, full_name)
    uname_str = f"@{username}" if username else "yo'q"
    text = (
        "🆕 Yangi a'zo botga qo'shildi!\n\n"
        f"👤 Ism: {full_name}\n"
        f"🔗 Username: {uname_str}\n"
        f"🆔 ID: <code>{user_id}</code>\n\n"
        f"📊 Bu — botning <b>{total}</b>-chi foydalanuvchisi!"
    )
    for admin_id in ADMIN_IDS:
        try:
            await bot.send_message(admin_id, text)
        except Exception:
            pass


async def ensure_subscribed(bot: Bot, message: Message) -> bool:
    """Obunani tekshiradi; obuna bo'lmasa xabar yuborib False qaytaradi."""
    not_subscribed = await get_not_subscribed(bot, message.from_user.id)
    if not_subscribed:
        await message.answer(
            "👋 Botdan foydalanish uchun avval barcha kanallarga obuna bo'ling:",
            reply_markup=channels_kb(),
        )
        return False
    return True


@router.message(CommandStart())
async def cmd_start(message: Message, bot: Bot):
    not_subscribed = await get_not_subscribed(bot, message.from_user.id)
    if not_subscribed:
        await message.answer(
            "👋 Assalomu alaykum!\n\n"
            "Botdan foydalanish uchun quyidagi kanallarga obuna bo'ling, "
            "so'ng <b>✅ Obunani tekshirish</b> tugmasini bosing:",
            reply_markup=channels_kb(),
        )
        return

    await register_and_notify(
        bot,
        message.from_user.id,
        message.from_user.username or "",
        message.from_user.full_name,
    )

    is_admin = message.from_user.id in ADMIN_IDS
    await message.answer(
        "✅ Xush kelibsiz!\n\nQuyidagi bo'limlardan birini tanlang 👇",
        reply_markup=main_menu_reply_kb(is_admin=is_admin),
    )


@router.message(Command("darslar"))
async def cmd_darslar(message: Message, bot: Bot):
    if not await ensure_subscribed(bot, message):
        return
    await message.answer(
        "🎓 <b>Barcha darslar</b>\n\n"
        "Barcha darslar tugmalarda — tugmalardan foydalaning 👇",
        reply_markup=submenu_kb("menu_dars"),
    )


@router.message(Command("prompt"))
async def cmd_prompt(message: Message, bot: Bot):
    if not await ensure_subscribed(bot, message):
        return
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="📝 Promptlar kanali", url="https://t.me/AI_YANGILIKLA"))
    await message.answer(
        "📝 <b>Promptlar</b>\n\n"
        "Barcha tayyor AI promptlarimiz quyidagi kanalda joylashgan 👇",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("haqida"))
async def cmd_haqida(message: Message):
    await message.answer(
        "🌟 <b>Bilimdon haqida</b>\n\n"
        "Bilimdon — bu sun'iy intellekt (AI) dunyosini har bir insonga "
        "tushunarli va oson qilib yetkazish uchun yaratilgan ta'lim platformasi.\n\n"
        "🎯 <b>Bizning maqsadimiz:</b>\n"
        "AI bilan ishlashni bilmaganlarga — oddiy tilda o'rgatish, "
        "biladiganlarga esa — yangi bilim va imkoniyatlar taqdim etish.\n\n"
        "📚 <b>Bizda nima bor:</b>\n"
        "🔹 Foydali darslar va vizual infografikalar\n"
        "🔹 Tayyor AI promptlari\n"
        "🔹 AI yangiliklari va foydali resurslar\n"
        "🔹 Savol-javob va faol hamjamiyat\n\n"
        "🤝 Bilimdon oilasiga xush kelibsiz — birga o'rganamiz, birga rivojlanamiz!\n\n"
        "📢 Kanallarimiz va guruhimizga qo'shilishni unutmang 👇",
        reply_markup=channels_kb(),
    )


@router.message(Command("yordam"))
async def cmd_yordam(message: Message):
    await message.answer(
        "🆘 <b>Yordam va qo'llab-quvvatlash</b>\n\n"
        "Botdan foydalanishda qiynalsangiz, quyidagilarga amal qiling:\n\n"
        "1️⃣ /start — botni qayta ishga tushirish\n"
        "2️⃣ Bosh menyudagi tugmalar orqali kerakli bo'limni toping\n"
        "3️⃣ /darslar — barcha darslarni ko'rish\n"
        "4️⃣ /prompt — tayyor promptlarni olish\n\n"
        "Muammo hal bo'lmasa — administratorga murojaat qiling, "
        "biz doim yordam berishga tayyormiz! 🤝",
    )


async def send_aloqa(message: Message):
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(text="📞 Administrator bilan bog'lanish", url=f"https://t.me/{ADMIN_USERNAME}")
    )
    await message.answer(
        "📞 <b>Biz bilan bog'lanish</b>\n\n"
        "Savol, taklif yoki hamkorlik bo'yicha murojaat uchun "
        "administratorimizga yozing 👇",
        reply_markup=builder.as_markup(),
    )


@router.message(Command("aloqa"))
async def cmd_aloqa(message: Message):
    await send_aloqa(message)


@router.message(F.text == CONTACT_BTN_TEXT)
async def btn_aloqa(message: Message):
    await send_aloqa(message)


@router.message(F.text.in_(list(TEXT_TO_KEY.keys())))
async def open_main_submenu(message: Message, bot: Bot):
    if not await ensure_subscribed(bot, message):
        return
    key = TEXT_TO_KEY[message.text]
    title = MENU_TITLES.get(key, "Bo'lim")
    await message.answer(
        f"📍 {title}\n\nKerakli bo'limni tanlang 👇",
        reply_markup=submenu_kb(key),
    )


@router.callback_query(F.data == "check_sub")
async def cb_check_sub(callback: CallbackQuery, bot: Bot):
    not_subscribed = await get_not_subscribed(bot, callback.from_user.id)
    if not_subscribed:
        await callback.answer(
            "❗️ Siz hali barcha kanallarga obuna bo'lmadingiz. Iltimos, barchasiga obuna bo'ling.",
            show_alert=True,
        )
        return

    await register_and_notify(
        bot,
        callback.from_user.id,
        callback.from_user.username or "",
        callback.from_user.full_name,
    )

    await callback.message.edit_text("✅ Obuna tasdiqlandi!", reply_markup=None)
    await callback.message.answer(
        "Quyidagi bo'limlardan birini tanlang 👇",
        reply_markup=main_menu_reply_kb(is_admin=callback.from_user.id in ADMIN_IDS),
    )
    await callback.answer()


@router.callback_query(F.data == "back:main")
async def cb_back_main(callback: CallbackQuery):
    await callback.message.edit_text(
        "🏠 Pastdagi asosiy menyudan kerakli bo'limni tanlang.",
        reply_markup=None,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("back:"))
async def cb_back_submenu(callback: CallbackQuery):
    parent_key = callback.data.split(":", 1)[1]
    if parent_key == "main":
        await callback.message.edit_text(
            "🏠 Pastdagi asosiy menyudan kerakli bo'limni tanlang.",
            reply_markup=None,
        )
    else:
        title = MENU_TITLES.get(parent_key, "Bo'lim")
        await callback.message.edit_text(
            f"📍 {title}\n\nKerakli bo'limni tanlang 👇",
            reply_markup=submenu_kb(parent_key),
        )
    await callback.answer()


@router.callback_query(F.data.startswith("content:"))
async def cb_show_content(callback: CallbackQuery):
    content_key = callback.data.split(":", 1)[1]
    if content_key not in CONTENT_MAP:
        await callback.answer("Xatolik yuz berdi.", show_alert=True)
        return

    content = db.get_content(content_key)
    title = CONTENT_MAP[content_key]["title"]
    markup = content_view_kb(content_key)

    if not content:
        await callback.message.answer(
            f"📍 {title}\n\n⏳ Hozircha bu bo'lim uchun material qo'shilmagan. Tez orada qo'shiladi!",
            reply_markup=markup,
        )
        await callback.answer()
        return

    ctype = content["content_type"]
    caption = content["text"] or ""

    if ctype == "text":
        await callback.message.answer(caption, reply_markup=markup)
    elif ctype == "photo":
        await callback.message.answer_photo(content["file_id"], caption=caption, reply_markup=markup)
    elif ctype == "video":
        await callback.message.answer_video(content["file_id"], caption=caption, reply_markup=markup)
    elif ctype == "document":
        await callback.message.answer_document(content["file_id"], caption=caption, reply_markup=markup)
    else:
        await callback.message.answer(
            f"📍 {title}\n\n⏳ Hozircha bu bo'lim uchun material qo'shilmagan.",
            reply_markup=markup,
        )

    await callback.answer()
