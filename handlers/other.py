import asyncio
import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')


from aiogram import Router, F, Bot
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
from aiogram.utils.i18n import gettext as _

from database.orm_users import orm_update_locale
from common import keyboard

# Инициализируем роутер уровня модуля
other_router = Router()


# Этот хэндлер срабатывает на команду /sett
@other_router.message(Command('sett'))
async def process_help_command(message: Message, workflow_data: dict):
    await message.answer(
        text=_('Настройки бота:\n\n'
               '/terms - условия использования\n'
               '/lang - сменить язык бота\n'
               '/stats - статистика игр\n'
               '/author - автор бота\n'
               '/donate - донат автору\n'
               )
    )
    analytics = workflow_data['analytics']
    await analytics(user_id=message.from_user.id,
                    category_name="/options",
                    command_name="/info")


# Клавиатура выбора языка
def get_keyboard():
    button_1 = InlineKeyboardButton(text=_('🇺🇸 Английский'), callback_data='locale_en')
    button_2 = InlineKeyboardButton(text=_('🇷🇺 Русский'), callback_data='locale_ru')
    button_3 = InlineKeyboardButton(text=_('🇩🇪 Немецкий'), callback_data='locale_de')
    # button_4 = InlineKeyboardButton(text=_('🇫🇷 Французский'), callback_data='locale_fr')
    button_5 = InlineKeyboardButton(text=_('🇯🇵 Японский'), callback_data='locale_ja')
    button_6 = InlineKeyboardButton(text=_('Назад на главную ↩️'), callback_data='about_back_to_main') # обработчик этой кнопки в private.py

    return InlineKeyboardMarkup(inline_keyboard=[[button_1, button_2], [button_3, button_5], [button_6]])


# Это хендлер будет срабатывать на команду locale
@other_router.message(Command('lang'))
async def locale_cmd(message: Message):
    await message.answer(_("Настройки языка"), reply_markup=keyboard.del_kb)
    await message.answer(text=_('Выберите язык на котором будет работать бот'),
                         reply_markup=get_keyboard())


@other_router.callback_query(F.data.startswith("locale_"))
async def update_locale_cmd(callback: CallbackQuery, session: AsyncSession, state: FSMContext, workflow_data: dict):
    user_id = callback.from_user.id

    if callback.data == 'locale_en':
        await orm_update_locale(session, user_id, 'en')  # Обновляем локаль в бд
        await state.update_data(locale='en')  # Обновляем локаль в контексте
        # await callback.message.edit_text('Choose a language ', reply_markup=None)  # Редактируем сообщение, скрываем inline клавиатуру
        await callback.message.delete()
        await callback.answer("Selected: 🇺🇸 English")  # Отправляем всплывашку
        await callback.message.answer("Current language \n\n 🇺🇸 English", # Отправляем новое сообщение
                                      reply_markup=keyboard.get_keyboard("Weather 🌊", "Currency 💵", "Cats 🐱", "LLMs 🤖", sizes=(2, 2, ), placeholder='⬇️'))

    elif callback.data == 'locale_ru':
        await orm_update_locale(session, user_id, 'ru')  # Обновляем локаль в бд
        await state.update_data(locale='ru')  # Обновляем локаль в контексте
        # await callback.message.edit_text('Выберите язык ', reply_markup=None)   # Редактируем сообщение, скрываем inline клавиатуру
        await callback.message.delete()
        await callback.answer("Выбран: 🇷🇺 Русский язык")  # Отправляем всплывашку
        await callback.message.answer("Текущий язык \n\n 🇷🇺 Русский", # Отправляем новое сообщение
                                      reply_markup=keyboard.get_keyboard("Погода 🌊", "Валюта 💵", "Котики 🐱", "LLMs 🤖", sizes=(2, 2, ), placeholder='⬇️'))

    elif callback.data == 'locale_de':
        await orm_update_locale(session, user_id, 'de')  # Обновляем локаль в бд
        await state.update_data(locale='de')  # Обновляем локаль в контексте
        # await callback.message.edit_text('Wählen Sie eine Sprache ', reply_markup=None)  # type: ignore # Редактируем сообщение,скрываем клавиатуру
        await callback.message.delete()
        await callback.answer("Ausgewählt: 🇩🇪 Deutsch")  # Отправляем всплывашку
        await callback.message.answer("Aktuelle Sprache \n\n 🇩🇪 Deutsch",   # Отправляем новое сообщение
                                      reply_markup=keyboard.get_keyboard("Wetter 🌊", "Währung 💵", "Katzen 🐱", "LLMs 🤖", sizes=(2, 2, ), placeholder='⬇️'))

    elif callback.data == 'locale_ja':
        await orm_update_locale(session, user_id, 'ja')  # Обновляем локаль в бд
        await state.update_data(locale='ja')  # Обновляем локаль в контексте
        # await callback.message.edit_text('言語を選択してください ', reply_markup=None)  # type: ignore # Редактируем сообщение,скрываем клавиатуру
        await callback.message.delete()
        await callback.answer("選択された: 🇯🇵 日本語")  # Отправляем всплывашку
        await callback.message.answer("現在の言語 \n\n 🇯🇵 日本語",   # Отправляем новое сообщение
                                      reply_markup=keyboard.get_keyboard("テンキ 🌊", "カワセ 💵", "ネコ 🐱", "エルエルエム 🤖", sizes=(2, 2, ), placeholder='⬇️'))

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/options",
                    command_name="/language")

# секретный хендлер, покажет содержимое data пользователя
@other_router.message(Command("data"))
async def data_cmd(message: Message, state: FSMContext):
    data = await state.get_data()
    await message.answer(str(data))

# Этот хэндлер срабатывает на команду /terms
@other_router.message(Command("terms"))
async def terms_cmd(message: Message):
    text = _("Условия использования:\n\n"
              "1. Этот бот создан для помощи и развлечения. Он не претендует на мировое господство (пока что).\n\n"
              "2. Бот старается быть точным, но иногда может ошибаться. Он всё-таки не человек, а просто очень умная программа.\n\n"
              "3. Фотографии котиков безопасны и проходят строгий отбор на милоту.\n\n"
              "4. Прогноз погоды и курсы валют берутся из надёжных источников, но используйте эти данные на своё усмотрение.\n\n"
              "5. Общение с ИИ (LLM) модулем может быть познавательным, но помните - это не замена реальному общению.\n\n"
              "6. Калькулятор пиццы поможет с расчётами, но окончательный выбор пиццы всегда за вами!\n\n"
              "7. Все донаты добровольные. Бот будет одинаково дружелюбен ко всем пользователям.\n\n"
              "8. Мы заботимся о вашей приватности и храним только необходимый минимум данных.\n\n"
              "9. В случае сбоев не переживайте - просто подождите немного или перезапустите бота.\n\n"
              "10. Развлекайтесь, узнавайте новое и не забывайте - этот бот создан, чтобы делать ваш день чуточку лучше!")
    await message.answer(text)
