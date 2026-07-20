from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

import database as db
from config import ADMIN_IDS, CONTENT_MAP
from keyboards import (
    admin_menu_kb,
    admin_select_content_kb,
    ADMIN_POST_BTN_TEXT,
    ADMIN_STATS_BTN_TEXT,
)
from states import AdminPost

router = Router()
router.message.filter(F.from_user.id.in_(ADMIN_IDS))
router.callback_query.filter(F.from_user.id.in_(ADMIN_IDS))


@router.message(Command("admin"))
async def cmd_admin(message: Message):
    await message.answer("🛠 Admin panel", reply_markup=admin_menu_kb())


async def send_stats(message: Message):
    stats = db.get_stats()
    await message.answer(
        "📊 <b>Statistika</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{stats['total']}</b>\n"
        f"🆕 Bugun qo'shilganlar: <b>{stats['today']}</b>"
    )


async def start_post_flow(message: Message, state: FSMContext):
    await state.set_state(AdminPost.choosing_button)
    await message.answer(
        "❓ Qaysi tugmaga post/kontent qo'shamiz?\n\nKerakli bo'limni tanlang 👇",
        reply_markup=admin_select_content_kb(),
    )


@router.message(F.text == ADMIN_STATS_BTN_TEXT)
async def btn_admin_stats(message: Message):
    await send_stats(message)


@router.message(F.text == ADMIN_POST_BTN_TEXT)
async def btn_admin_post(message: Message, state: FSMContext):
    await start_post_flow(message, state)


@router.callback_query(F.data == "admin_stats")
async def cb_admin_stats(callback: CallbackQuery):
    await send_stats(callback.message)
    await callback.answer()


@router.callback_query(F.data == "admin_post")
async def cb_admin_post(callback: CallbackQuery, state: FSMContext):
    await start_post_flow(callback.message, state)
    await callback.answer()


@router.callback_query(F.data == "admin_cancel")
async def cb_admin_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_kb())
    await callback.answer()


@router.callback_query(AdminPost.choosing_button, F.data.startswith("admin_select:"))
async def cb_admin_select(callback: CallbackQuery, state: FSMContext):
    content_key = callback.data.split(":", 1)[1]
    title = CONTENT_MAP[content_key]["title"]
    await state.update_data(content_key=content_key)
    await state.set_state(AdminPost.waiting_content)
    await callback.message.answer(
        f"📩 <b>{title}</b> uchun kontent yuboring.\n\n"
        "Matn, rasm, video yoki fayl (document) yuborishingiz mumkin.\n"
        "Bekor qilish uchun /cancel yozing."
    )
    await callback.answer()


@router.message(Command("cancel"), AdminPost.waiting_content)
@router.message(Command("cancel"), AdminPost.choosing_button)
async def cmd_cancel(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("❌ Bekor qilindi.", reply_markup=admin_menu_kb())


@router.message(AdminPost.waiting_content)
async def receive_content(message: Message, state: FSMContext):
    data = await state.get_data()
    content_key = data.get("content_key")
    if not content_key:
        await state.clear()
        await message.answer("Xatolik: bo'lim tanlanmagan. Qaytadan urinib ko'ring.")
        return

    if message.photo:
        content_type = "photo"
        file_id = message.photo[-1].file_id
        text = message.caption or ""
    elif message.video:
        content_type = "video"
        file_id = message.video.file_id
        text = message.caption or ""
    elif message.document:
        content_type = "document"
        file_id = message.document.file_id
        text = message.caption or ""
    elif message.text:
        content_type = "text"
        file_id = ""
        text = message.text
    else:
        await message.answer("⚠️ Bu turdagi kontentni saqlab bo'lmaydi. Matn, rasm, video yoki fayl yuboring.")
        return

    db.save_content(content_key, content_type, file_id, text)
    title = CONTENT_MAP[content_key]["title"]
    await state.clear()
    await message.answer(
        f"✅ <b>{title}</b> bo'limi uchun post saqlandi!\n\nEndi foydalanuvchilar shu tugma orqali ko'radi.",
        reply_markup=admin_menu_kb(),
    )
