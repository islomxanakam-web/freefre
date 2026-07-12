# Free Fire Telegram Bot

## 📁 Fayllar
- `bot.py` — botning asosiy kodi
- `config.py` — sozlamalar (token, admin ID, kanallar)
- `texts.py` — barcha matnlar (nastroykalar, niklar, qo'llanmalar)
- `requirements.txt` — kerakli kutubxonalar
- `Procfile` — Railway uchun ishga tushirish buyrug'i

## 1️⃣ Avval qiling: yangi token oling
Tokeningiz ochiq chatda ko'rsatilgani uchun uni **almashtirish tavsiya etiladi**:
1. Telegram'da @BotFather ga yozing
2. `/mybots` → botingizni tanlang → **API Token** → **Revoke current token**
3. Yangi tokenni saqlab qo'ying (keyingi bosqichda kerak bo'ladi)

## 2️⃣ O'z Telegram ID'ingizni oling
Statistika va bildirishnomalar ishlashi uchun kerak:
1. Telegram'da @userinfobot ga yozing
2. U sizga raqamli ID'ingizni beradi (masalan: `123456789`)

## 3️⃣ Bot kanallarga admin qilinishi kerak
Majburiy obunani tekshirish uchun bot quyidagi 3 kanalda **admin** bo'lishi shart:
- @ffpanelchit
- @xonfirestream
- @sunniyintellekt_darslar

Har bir kanalga kirib: Kanal sozlamalari → Administratorlar → botni qo'shing.

## 4️⃣ GitHub'ga yuklash
```bash
cd ff_bot
git init
git add .
git commit -m "Free Fire bot"
git branch -M main
git remote add origin https://github.com/FOYDALANUVCHI_NOMI/REPO_NOMI.git
git push -u origin main
```
(GitHub'da avval bo'sh repository yarating: github.com/new)

## 5️⃣ Railway'ga deploy qilish
1. https://railway.app ga kiring, GitHub akkauntingiz bilan kiring
2. **New Project** → **Deploy from GitHub repo** → repongizni tanlang
3. Deploy tugagach, loyihaga kirib **Variables** bo'limini oching va qo'shing:
   - `BOT_TOKEN` = yangi tokeningiz
   - `ADMIN_ID` = sizning raqamli ID'ingiz
4. **Settings** bo'limida **Start Command** ni tekshiring: `python bot.py`
   (Procfile avtomatik aniqlanadi, lekin ba'zan qo'lda kiritish kerak bo'ladi)
5. Deploy tugagach, Telegram'da botga `/start` yozib sinab ko'ring

## ⚠️ Eslatma
- Statistika (`data.json`) fayli oddiy JSON asosida ishlaydi. Railway serverini qayta
  ishga tushirsangiz fayl tizimi tozalanishi mumkin — agar statistika doimiy saqlanishi
  kerak bo'lsa, kelajakda kichik ma'lumotlar bazasiga (masalan PostgreSQL) o'tkazish tavsiya etiladi.
- Har qanday matnni o'zgartirish uchun faqat `texts.py` faylini tahrirlang, `bot.py` ga tegishi shart emas.
