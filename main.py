import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType, Update
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# ==========================================
# KONFIGURATSIYA
# ==========================================
BOT_TOKEN = os.getenv("BOT_TOKEN", "8637987450:AAEwdY0xi7BvzNUcoY4RRhwtOvUBIYstcRI")
BOOK_PRICE = 66000 # UZS
BOOK_PDF_PATH = os.getenv("BOOK_PDF_PATH", "kitob.pdf") 

# Webhook sozlamalari
RENDER_URL = os.getenv("RENDER_EXTERNAL_URL", "https://onlayn-kitob.uz")
WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = RENDER_URL + WEBHOOK_PATH

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcherni yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# --- BOT LOGIKASI ---

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer(
        f"Assalomu alaykum, {message.from_user.full_name}! 👋\n\n"
        "**AI DAROMAD** kitobini sotib olish botiga xush kelibsiz.\n\n"
        "Ushbu kitob orqali siz sun'iy intellekt yordamida moliyaviy erkinlikka erishish yo'llarini o'rganasiz.\n\n"
        "💰 Kitob narxi: **66,000 UZS**\n\n"
        "Sotib olish uchun quyidagi tugmani bosing:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Sotib olish 💳", callback_data="buy_book")]
            ]
        ),
        parse_mode="Markdown"
    )

@dp.callback_query(F.data == "buy_book")
async def process_buy_book(callback_query: types.CallbackQuery):
    payment_text = (
        "💳 **To'lov ma'lumotlari:**\n\n"
        "Karta: `5614681290542020` (HUMO)\n"
        "Egasi: **Abbosov.D**\n"
        "Summa: **66,000 UZS**\n\n"
        "Toʻlov qiling va chekni @Daromad_ai yuboring. Chekni tekshirib yaqin 10 daqiqada kitobni yuboraman. ✅"
    )
    
    await callback_query.message.answer(
        payment_text,
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Admin bilan bog'lanish 👤", url="https://t.me/Daromad_ai")]
            ]
        ),
        parse_mode="Markdown"
    )
    await callback_query.answer()

# --- WEB SERVER (FastAPI) ---

app = FastAPI()

@app.get("/")
async def serve_home():
    return FileResponse("index.html")

@app.post(WEBHOOK_PATH)
async def bot_webhook(request: Request):
    update = Update.model_validate(await request.json(), context={"bot": bot})
    await dp.feed_update(bot, update)

@app.get("/{file_path:path}")
async def get_file(file_path: str):
    # Agar fayl bo'sh bo'lsa yoki index bo'lsa serve_home ishlaydi
    if not file_path or file_path == "index.html":
        return FileResponse("index.html")
    
    if os.path.exists(file_path) and os.path.isfile(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

@app.on_event("startup")
async def on_startup():
    # Faqat Render-da Webhook o'rnatamiz
    if os.getenv("PORT"):
        logging.info(f"PRODUCTION: Setting webhook to: {WEBHOOK_URL}")
        await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)
    else:
        logging.info("LOCAL: Running in Polling mode...")
        # Lokal rejimda webhook o'chirib yuboriladi
        await bot.delete_webhook(drop_pending_updates=True)
        # Pollingni alohida vazifa sifatida boshlash
        asyncio.create_task(dp.start_polling(bot))

@app.on_event("shutdown")
async def on_shutdown():
    await bot.session.close()

if __name__ == "__main__":
    # Render PORT ni o'zi beradi, lokalda esa 8000 ishlaydi
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
