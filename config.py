import os

# Bot tokenini Railway'da Environment Variable orqali BOT_TOKEN nomi bilan qo'ying.
# Agar mahalliy sinab ko'rmoqchi bo'lsangiz, pastdagi standart qiymatdan foydalanishi mumkin,
# lekin bu tokenni ochiq joyga yozmang - u ochiq chatda ko'rsatilgani uchun @BotFather'da
# /revoke qilib, yangisini oling va shu yerga emas, Railway'ga yozing.
BOT_TOKEN = os.getenv("BOT_TOKEN", "8764058918:AAESRQ86jfeBEKbSs02P_ph9lwqwc4rDEvI")

# O'zingizning Telegram raqamli ID'ingizni shu yerga yozing (masalan @userinfobot orqali oling).
# Statistika tugmasi va barcha xabar/ start bildirishnomalari shu ID'ga keladi.
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))

ADMIN_USERNAME = "ffhelpnastroyka"

# Majburiy obuna kanallari (bot shu kanallarda ADMIN/A'ZO bo'lishi shart, aks holda
# obunani tekshira olmaydi)
CHANNELS = [
    "@ffpanelchit",
    "@xonfirestream",
    "@sunniyintellekt_darslar",
]

DATA_FILE = "data.json"
