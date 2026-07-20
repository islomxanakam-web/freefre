from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from config import CHANNELS, MAIN_MENU, CONTENT_MAP, ADMIN_USERNAME

CONTACT_BTN_TEXT = "📞 Aloqaga chiqish"
ADMIN_POST_BTN_TEXT = "🛠 Post/Tugma qo'shish"
ADMIN_STATS_BTN_TEXT = "📊 Statistika"


def channels_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for ch in CHANNELS:
        builder.add(
            InlineKeyboardButton(
                text=f"📢 {ch['title']}",
                url=f"https://t.me/{ch['username']}",
            )
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(text="✅ Obunani tekshirish", callback_data="check_sub")
    )
    return builder.as_markup()


def main_menu_reply_kb(is_admin: bool = False) -> ReplyKeyboardMarkup:
    """Pastda doimiy turadigan, rangli (pill) tugmali bosh menyu."""
    builder = ReplyKeyboardBuilder()
    for item in MAIN_MENU:
        builder.add(KeyboardButton(text=item["title"]))
    builder.add(KeyboardButton(text=CONTACT_BTN_TEXT))
    builder.adjust(2)
    if is_admin:
        builder.row(
            KeyboardButton(text=ADMIN_POST_BTN_TEXT),
            KeyboardButton(text=ADMIN_STATS_BTN_TEXT),
        )
    return builder.as_markup(resize_keyboard=True)


def submenu_kb(parent_key: str) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in CONTENT_MAP.items():
        if item["parent"] == parent_key:
            builder.add(InlineKeyboardButton(text=item["title"], callback_data=f"content:{key}"))
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data="back:main"))
    return builder.as_markup()


def content_view_kb(content_key: str) -> InlineKeyboardMarkup:
    parent = CONTENT_MAP[content_key]["parent"]
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="⬅️ Orqaga", callback_data=f"back:{parent}"))
    return builder.as_markup()


def admin_menu_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Post/Tugma qo'shish", callback_data="admin_post"))
    builder.add(InlineKeyboardButton(text="📊 Statistika", callback_data="admin_stats"))
    builder.adjust(2)
    return builder.as_markup()


def admin_select_content_kb() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for key, item in CONTENT_MAP.items():
        builder.add(
            InlineKeyboardButton(text=item["title"], callback_data=f"admin_select:{key}")
        )
    builder.adjust(2)
    builder.row(InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel"))
    return builder.as_markup()
