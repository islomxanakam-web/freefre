import os

# Bot tokenini Railway'da Environment Variable orqali BOT_TOKEN nomi bilan qo'ying.
# Agar mahalliy sinab ko'rmoqchi bo'lsangiz, pastdagi standart qiymatdan foydalanishi mumkin,
# lekin bu tokenni ochiq joyga yozmang - u ochiq chatda ko'rsatilgani uchun @BotFather'da
# /revoke qilib, yangisini oling va shu yerga emas, Railway'ga yozing.
BOT_TOKEN = os.getenv("BOT_TOKEN", "8764058918:AAESRQ86jfeBEKbSs02P_ph9lwqwc4rDEvI")

# O'zingizning Telegram raqamli ID'ingiz (Railway'da ADMIN_ID environment variable orqali
# ham o'zgartirishingiz mumkin, u shu yerdagi qiymatdan ustun turadi).
ADMIN_ID = int(os.getenv("ADMIN_ID", "8969109663"))

ADMIN_USERNAME = "ffhelpnastroyka"

# Majburiy obuna kanallari va guruh (bot shularning barchasida ADMIN bo'lishi shart,
# aks holda obunani tekshira olmaydi)
CHANNELS = [
    {"username": "@ffpanelchit", "label": "1-kanal"},
    {"username": "@xonfirestream", "label": "2-kanal"},
    {"username": "@sunniyintellekt_darslar", "label": "3-kanal"},
    {"username": "@FREEFIRECHAT_UZBEKI", "label": "Guruh"},
]

DATA_FILE = "data.json"
