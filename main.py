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
CLICK_TOKEN = os.getenv("CLICK_TOKEN", "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065")
BOOK_PRICE = 66000 * 100 
BOOK_PDF_PATH = os.getenv("BOOK_PDF_PATH", "kitob.pdf") 

# Webhook sozlamalari
RENDER_URL = "https://ai-daromad-book.onrender.com"
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
async def send_invoice(callback_query: types.CallbackQuery):
    await bot.send_invoice(
        callback_query.from_user.id,
        title="AI DAROMAD Kitobi",
        description="AI orqali daromad qilish bo'yicha to'liq qo'llanma (PDF)",
        provider_token=CLICK_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="Kitob", amount=BOOK_PRICE)],
        payload="book_purchase_payload",
        photo_url="https://raw.githubusercontent.com/Dimonbek/ai-daromad-book/main/book-cover.png",
        photo_size=512,
        photo_width=512,
        photo_height=512,
        is_flexible=False
    )

@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment_handler(message: types.Message):
    await message.answer(
        "To'lov muvaffaqiyatli amalga oshirildi! 🎉✅\n\n"
        "Tabriklaymiz! Siz moliyaviy erkinlik sari katta qadam tashladingiz.\n"
    )
    
    try:
        if os.path.exists(BOOK_PDF_PATH):
            await message.answer_document(types.FSInputFile(BOOK_PDF_PATH), caption="Mana sizning kitobingiz! 📚")
        else:
            await message.answer("Kitobingiz hozirda yakuniy tahrirda. Tayyor bo'lishi bilan aynan shu yerga yuboriladi! 🚀")
    except Exception as e:
        logging.error(f"Fayl yuborishda xato: {e}")
        await message.answer("Kitobni avtomatik yuborishda kichik muammo bo'ldi. Admin tez orada siz bilan bog'lanadi.")

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
    logging.info(f"Setting webhook to: {WEBHOOK_URL}")
    await bot.set_webhook(url=WEBHOOK_URL, drop_pending_updates=True)

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
