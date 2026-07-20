import os

# ====== ASOSIY SOZLAMALAR ======
# Railway'da Variables bo'limiga BOT_TOKEN va ADMIN_ID qo'shsangiz, shulardan foydalanadi.
# Agar qo'shmasangiz, pastdagi standart qiymatlar ishlatiladi.

BOT_TOKEN = os.getenv("BOT_TOKEN", "8258790417:AAGJ__XEzSc_cP938-DdQxCJYEb_Joa4LlI")

# Bir nechta admin bo'lishi mumkin - ro'yxatga ID qo'shib boraverasiz
ADMIN_IDS = [8969109663, 8914193938]
ADMIN_ID = ADMIN_IDS[0]  # eski kodlar bilan moslik uchun (bildirishnoma shu ID'ga ustuvor yuboriladi)
ADMIN_USERNAME = "auwsn"  # Aloqa uchun @username

DB_PATH = os.getenv("DB_PATH", "bot.db")

# ====== MAJBURIY OBUNA KANALLARI ======
CHANNELS = [
    {"title": "Sun'iy Intellekt Darslar", "username": "sunniyintellekt_darslar"},
    {"title": "AI GURUH", "username": "AIGURUH"},
    {"title": "Xon Fire Stream", "username": "xonfirestream"},
    {"title": "AI Yangiliklar", "username": "AI_YANGILIKLA"},
    {"title": "Shoxona Kinolar", "username": "shoxona_kinolar"},
]

# ====== MENYU STRUKTURASI ======
# Har bir "content_key" - admin post/tugma qo'shadigan yagona bo'lim.
# parent - bu bo'lim qaysi bosh menyudan ochilishini bildiradi.

MAIN_MENU = [
    {"key": "menu_dars", "title": "🎓 AI TO'LIQ DARS"},
    {"key": "menu_prompt", "title": "📝 Promptlar"},
    {"key": "menu_sayt", "title": "🌐 Web sayt yasash"},
    {"key": "menu_bot", "title": "🤖 Bot yasash"},
]

CONTENT_MAP = {
    "ai_dars_rasm_gen": {"title": "🖼 Rasm generatsiya qilish", "parent": "menu_dars"},
    "ai_dars_video": {"title": "🎬 Rasmdan video yasash", "parent": "menu_dars"},

    "prompt_rasm_referens": {"title": "🖼 Rasm referensa qilish prompti", "parent": "menu_prompt"},
    "prompt_sifatli_rasm": {"title": "✨ Sifatli rasm generatsiya prompti", "parent": "menu_prompt"},
    "prompt_4k": {"title": "🔍 Rasmni 4K tiniq qilish prompti", "parent": "menu_prompt"},
    "prompt_sayt": {"title": "🌐 Sayt yasash prompti", "parent": "menu_prompt"},
    "prompt_bot": {"title": "🤖 Bot yasash prompti", "parent": "menu_prompt"},

    "sayt_ai": {"title": "🌐 AI orqali sayt yasash", "parent": "menu_sayt"},

    "bot_ai": {"title": "🤖 AI orqali bot yasash", "parent": "menu_bot"},
}

MENU_TITLES = {m["key"]: m["title"] for m in MAIN_MENU}
MENU_TITLES["main"] = "🏠 Bosh menyu"
