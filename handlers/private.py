import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')


import asyncio
import requests
import random as r
import os

from aiogram import F, Router
from aiogram.types import InlineKeyboardButton, FSInputFile, Message, CallbackQuery
from aiogram.filters import Command, StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from sqlalchemy.ext.asyncio import AsyncSession

from common import keyboard
from filters.chat_type import ChatTypeFilter
from database.orm_games import get_top_scores


# Инициализируем роутер уровня модуля
private_router = Router()
private_router.message.filter(ChatTypeFilter(['private']))
private_router.edited_message.filter(ChatTypeFilter(['private']))

# Создаем константы для текстов, которые используются в декораторах
BACK_TO_MAIN = __("Назад на главную ↩️")
CATS = __("Котики 🐱")

# команда /main, кнопка "назад на главную"
@private_router.message(or_f(Command("main"), F.text == BACK_TO_MAIN))
async def cancel_cmd(message: Message, state: FSMContext):
    await state.set_state(None)
    await message.answer(_('Главная панель'), reply_markup=keyboard.start_keyboard())

# символ точка - ОТМЕНА, сброс любого состояния;
# ловим любое состояние пользователя, и если введен текст "."
@private_router.message(StateFilter("*"), F.text.casefold() == ".")
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state() # получаем текущее состояние
    if current_state is None: # если состояния пустое, то ни чего не делаем
        return
    # Завершаем машину состояний, но не удаляем данные из словаря FSMContext
    await state.set_state(None)
    await message.answer(_("Действия отменены"))
    await asyncio.sleep(1)
    await message.answer(_('Главная панель'), reply_markup=keyboard.start_keyboard())


# команда /author
# @private_router.message(Command("author"))
# async def author_cmd(message: Message, workflow_data: dict):
@private_router.callback_query(F.data == "author")
async def author_cmd(callback: CallbackQuery, workflow_data: dict, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    last_message_id = data.get('last_message_id')

    # Если есть предыдущее сообщение, удаляем его
    if last_message_id:
        try:
            await callback.bot.delete_message(chat_id=user_id,
                                                message_id=last_message_id)
        except Exception as e:
            logger.error("Ошибка при удалении last_message_id сообщения: %s", e)
    else:
        try:
            await callback.message.delete()
        except Exception as e:
            logger.error("Ошибка при удалении сообщения: %s", e)

    await callback.message.answer(text=" ... ", reply_markup=keyboard.del_kb)
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text="Telegram",url="tg://user?id=459148628"))
    builder.row(InlineKeyboardButton(text="Linkedin",url="https://www.linkedin.com/in/ivan-goncharov-8a1982212/"))
    builder.row(InlineKeyboardButton(text="GitHub", url="https://github.com/van4956"))
    builder.row(InlineKeyboardButton(text="Kaggle",url="https://www.kaggle.com/ivan4956"))
    builder.row(InlineKeyboardButton(text=_("Назад"), callback_data="back_to_info"))
    builder.row(InlineKeyboardButton(text=_("Назад на главную ↩️"), callback_data='about_back_to_main'))
    image_from_pc = FSInputFile("common/images/image_about.jpg")
    msg = await callback.message.answer_photo(image_from_pc,
                               caption=_('... в мире, где машины стремятся к господству, он выбрал судьбу героя, '

                                         'создавая ботов, как первый шаг к спасению человечества через код и умные алгоритмы.'),
                                reply_markup=builder.adjust(2,2,1,1,).as_markup())

    analytics = workflow_data['analytics']
    await analytics(user_id=callback.from_user.id,
                    category_name="/options",
                    command_name="/help")

    # Сохраняем message_id в FSMContext
    await state.update_data(last_message_id=msg.message_id)


# callback "назад на главную"
@private_router.callback_query(F.data == 'about_back_to_main')
async def callback_about(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    data = await state.get_data()
    last_message_id = data.get('last_message_id')

    # Сбрасываем состояние
    await state.set_state(None)

    # Если есть предыдущее сообщение, удаляем его
    if last_message_id:
        try:
            await callback.bot.delete_message(chat_id=user_id,
                                                message_id=last_message_id)
        except Exception as e:
            logger.error("Ошибка при удалении last_message_id сообщения: %s", e)
            # если не удалось удалить last_message_id, то пробуем удалить текущее сообщение
            try:
                await callback.message.delete()
            except Exception as ex:
                logger.error("Ошибка при удалении сообщения: %s", ex)
    else:
        try:
            await callback.message.delete()
        except Exception as e:
            logger.error("Ошибка при удалении сообщения: %s", e)

    await callback.answer(_('Назад на главную ↩️'))
    await callback.message.answer(_('Главная панель'), reply_markup=keyboard.start_keyboard())


# кнопка "Котики"
@private_router.message(F.text == CATS)
async def cat_cmd(message: Message, workflow_data: dict):
    user_id = message.from_user.id

    # вероятность 20% для выбора локального изображения с Кет
    if r.random() < 0.2:
        image_folder = 'common/image_cat'
        images = [f'common/image_cat/{img}' for img in os.listdir(image_folder) if img.endswith('.jpg')]

        if images:
            random_image = r.choice(images)
            photo = FSInputFile(random_image)
            await message.answer_photo(photo)
            return
        else:
            await message.answer(_('Локальные изображения не найдены.'))

    cat_response = requests.get('https://api.thecatapi.com/v1/images/search', timeout=10)
    try:
        if cat_response.status_code == 200:
            if cat_response.json()[0]['url'][-3:].lower() in ['jpg','png']:
                cat_link = cat_response.json()[0]['url']
                await message.answer_photo(cat_link)
            else:
                cat_link = cat_response.json()[0]['url']
                await message.answer_document(cat_link)
        else:
            await message.answer(_('Здесь должна была быть картинка с котиком :('))

    except Exception as e:
        logger.error("Error: %s", str(e))
        text_error = f'Error:\n{str(e)}'
        await message.answer(text_error)

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/service",
                    command_name="/cat")
