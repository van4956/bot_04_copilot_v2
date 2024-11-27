from aiogram import Router, types
from aiogram.filters import Command
from aiogram.types import WebAppInfo, FSInputFile

miniapp_router = Router()

# URL веб-приложения
WEBAPP_URL = "https://van4956.github.io/bot_04_copilot_v2/pizza_calculator/"

@miniapp_router.message(Command("mini"))
async def cmd_miniapp(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(
        inline_keyboard=[
            [types.InlineKeyboardButton(text="🍕 Калькулятор пиццы", web_app=WebAppInfo(url=WEBAPP_URL))],
            [types.InlineKeyboardButton(text="🎮 Тетрис", web_app=WebAppInfo(url=WEBAPP_URL))],
            [types.InlineKeyboardButton(text="🐍 Змейка", web_app=WebAppInfo(url=WEBAPP_URL))],
        ]
    )
    photo = FSInputFile("common/images/image_miniapp.jpg")
    await message.answer_photo(
        photo=photo,
        caption="Mini apps Telegram:",
        reply_markup=keyboard
    )
