import logging
import asyncio
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

# ==========================================
# KONFIGURATSIYA
# ==========================================
# Render-da Environment Variables qilib sozlash tavsiya etiladi
BOT_TOKEN = os.getenv("BOT_TOKEN", "8637987450:AAEwdY0xi7BvzNUcoY4RRhwtOvUBIYstcRI")
CLICK_TOKEN = os.getenv("CLICK_TOKEN", "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065")
BOOK_PRICE = 63000 * 100  # 63,000 UZS
# Render-da fayl yo'li Linux bo'lishi kerak
BOOK_PDF_PATH = os.getenv("BOOK_PDF_PATH", "kitob.pdf") 

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
        "💰 Kitob narxi: **63,000 UZS**\n\n"
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

# Statik fayllarni xizmat qilish (index.html, style.css, rasmlar)
app.mount("/static", StaticFiles(directory="."), name="static")

@app.get("/")
async def serve_home():
    return FileResponse("index.html")

# Agar CSS yoki rasmlar chaqirilsa, ularni rootdan topish uchun
@app.get("/{file_path:path}")
async def get_file(file_path: str):
    if os.path.exists(file_path):
        return FileResponse(file_path)
    return {"error": "File not found"}

# Botni backgroundda ishga tushirish
@app.on_event("startup")
async def on_startup():
    # Avvalgi polling yoki webhooklarni tozalash (Conflict oldini olish uchun)
    await bot.delete_webhook(drop_pending_updates=True)
    asyncio.create_task(dp.start_polling(bot))

if __name__ == "__main__":
    # Render PORT muhitini o'zi beradi
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)
