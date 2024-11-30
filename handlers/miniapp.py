import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

import asyncio
import json
from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, FSInputFile, CallbackQuery, InlineKeyboardButton, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from common import keyboard
from database.models import Games
from database.orm_games import orm_add_game

miniapp_router = Router()

# URL веб-приложения
WEBAPP_URL_PIZZA = "https://van4956.github.io/bot_04_copilot_v2/pizza_calculator/"
WEBAPP_URL_RANDOM = "https://van4956.github.io/bot_04_copilot_v2/random_generator/"

WEBAPP_URL_SNAKE = "https://van4956.github.io/bot_04_copilot_v2/snake_game/"
WEBAPP_URL_SNAKE_V2 = "t.me/judge_dredd_v3_bot/snake_game"
WEBAPP_URL_SNAKE_V3 = "http://t.me/judge_dredd_v3_bot/snake_game"

@miniapp_router.message(Command("mini"))
async def cmd_miniapp(message: types.Message, workflow_data: dict):
    user_id = message.from_user.id
    await message.answer(text="Mini apps Telegram",reply_markup=keyboard.del_kb)
    await asyncio.sleep(1)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="🍕 Калькулятор", web_app=WebAppInfo(url=WEBAPP_URL_PIZZA)))
    builder.row(InlineKeyboardButton(text="🎲 Рандомайзер", web_app=WebAppInfo(url=WEBAPP_URL_RANDOM)))
    builder.row(InlineKeyboardButton(text="🐍 Змейка", web_app=WebAppInfo(url=WEBAPP_URL_SNAKE_V3)))
    builder.row(InlineKeyboardButton(text=_("Назад на главную ↩️"), callback_data='mini_back_to_main'))

    photo = FSInputFile("common/images/image_miniapp.jpg")
    await message.answer_photo(
        photo=photo,
        caption=_("Фабрика по производству мини-приложений:"),
        reply_markup=builder.adjust(1,1,1,1,).as_markup()
    )
    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/service",
                    command_name="/miniapp")

# callback "назад на главную"
@miniapp_router.callback_query(F.data == 'mini_back_to_main')
async def callback_about(callback: CallbackQuery):
    await callback.message.delete()
    await callback.answer(_('Назад на главную ↩️'))
    await asyncio.sleep(1)
    await callback.message.answer(_('Главная панель'), reply_markup=keyboard.start_keyboard())

@miniapp_router.message(F.web_app_data)
async def handle_web_app_data(message: Message,  session: AsyncSession, workflow_data: dict):
    logger.info("Веб-приложение отправляет данные: %s", message.web_app_data.data)
    try:
        analytics = workflow_data['analytics']
        data = json.loads(message.web_app_data.data)

        # Проверка структуры данных
        if not isinstance(data, dict):
            logger.error("Invalid data format: not a dictionary")
            return

        score=data.get('score', 0)

        if data.get('action') == 'game_start' and data.get('game') == 'snake':
            logger.info("Starting snake game for user %s", message.from_user.id)
            await analytics(user_id=message.from_user.id,
                            category_name="/game",
                            command_name="/snake")

        if data.get('action') == 'game_end' and data.get('game') == 'snake':
            logger.info("Ending snake game for user %s with score %s", message.from_user.id, data.get('score', 0))
            # добавляем данные игры в бд
            data = {'game_name': 'snake',
                                    'user_id': message.from_user.id,
                                    'user_name': message.from_user.username,
                                    'score': score}

            await orm_add_game(session=session, data=data)

            # Отправляем сообщение пользователю
            await message.answer(f"Игра окончена!\nВаш счет: {data.get('score', 0)}")

    except json.JSONDecodeError as e:
        logger.error("Failed to parse web app data: %s", e)
    except (ValueError, KeyError, AttributeError) as e:
        logger.error("Error processing web app data: %s", e)

# Обработка ошибок при работе с веб-приложением
@miniapp_router.error()
async def error_handler(update: types.Update, exception: Exception):
    logger.error("Ошибка при работе с веб-приложением: %s", exception)
    if isinstance(update.message, Message):
        await update.message.answer("Произошла ошибка при запуске приложения. Попробуйте позже.")
