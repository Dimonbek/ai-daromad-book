import logging
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import LabeledPrice, PreCheckoutQuery, ContentType

# ==========================================
# KONFIGURATSIYA (Sizning tokenlaringiz ulandi)
# ==========================================
BOT_TOKEN = "8637987450:AAEwdY0xi7BvzNUcoY4RRhwtOvUBIYstcRI"
CLICK_TOKEN = "398062629:TEST:999999999_F91D8F69C042267444B74CC0B3C747757EB0E065"
BOOK_PRICE = 63000 * 100  # 63,000 UZS (Tiynlarda)
BOOK_PDF_PATH = "C:/Users/Lenovo/Downloads/kitob.pdf" # Fayl tayyor bo'lgach nomini tekshiring

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
        "💰 Kitob narxi: **63,000 UZS**\n\n"
        "Sotib olish uchun quyidagi tugmani bosing:",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="Sotib olish 💳", callback_data="buy_book")]
            ]
        ),
        parse_mode="Markdown"
    )

# 2. Sotib olish tugmasi bosilganda Invoice (schyot) yuborish
@dp.callback_query(F.data == "buy_book")
async def send_invoice(callback_query: types.CallbackQuery):
    await bot.send_invoice(
        callback_query.from_user.id,
        title="AI DAROMAD Kitobi",
        description="AI orqali daromad qilish bo'yicha to'liq qo'llanma (PDF)",
        provider_token=CLICK_TOKEN,
        currency="UZS",
        prices=[LabeledPrice(label="Kitob", amount=BOOK_PRICE)],
        payload="book_purchase_payload", # Ichki identifikator
        photo_url="https://raw.githubusercontent.com/username/repo/main/book-cover.png", # Agar rasm ulamoqchi bo'lsangiz
        photo_size=512,
        photo_width=512,
        photo_height=512,
        is_flexible=False # Yetkazib berish manzili kerak emas
    )

# 3. To'lovdan oldingi tekshiruv (Pre-checkout)
@dp.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    # Har doim 'ok=True' qaytaramiz (agar biror maxsus cheklov bo'lmasa)
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)

# 4. Muvaffaqiyatli to'lovdan so'ng xabar va kitobni yuborish
@dp.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def success_payment_handler(message: types.Message):
    await message.answer(
        "To'lov muvaffaqiyatli amalga oshirildi! 🎉✅\n\n"
        "Tabriklaymiz! Siz moliyaviy erkinlik sari katta qadam tashladingiz.\n"
    )
    
    try:
        # Faylni yuborish (Hozircha fayl bo'lmasa xato berishi mumkin)
        # Fayl tayyor bo'lganda quyidagi qatorni aktivlashtiring:
        # await message.answer_document(types.FSInputFile(BOOK_PDF_PATH), caption="Mana sizning kitobingiz! 📚")
        await message.answer("Kitobingiz hozirda yakuniy tahrirda. Tayyor bo'lishi bilan aynan shu yerga yuboriladi! 🚀")
    except Exception as e:
        logging.error(f"Fayl yuborishda xato: {e}")
        await message.answer("Kitobni avtomatik yuborishda kichik muammo bo'ldi. Admin tez orada siz bilan bog'lanadi.")

# Polling (Botni ishga tushirish)
async def main():
    print("Bot ishga tushdi...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")
