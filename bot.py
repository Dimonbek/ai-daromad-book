import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType

# ==========================================
# KONFIGURATSIYA
# ==========================================
BOT_TOKEN = "8637987450:AAEwdY0xi7BvzNUcoY4RRhwtOvUBIYstcRI"
BOOK_PRICE = 66000 # UZS
BOOK_PDF_PATH = "kitob.pdf"

# Loglarni sozlash
logging.basicConfig(level=logging.INFO)

# Bot va Dispatcherni yaratish
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# 1. Start komandasi
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

# 2. Sotib olish tugmasi bosilganda to'lov ma'lumotlarini yuborish
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

# Polling (Botni ishga tushirish)
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
