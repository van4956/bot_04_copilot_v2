import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

import requests
import os
from datetime import datetime, timezone
from aiogram import F, Router
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import  StateFilter, or_f
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from common import keyboard
from filters.chat_type import ChatTypeFilter

# создаем роутер для валюты
currency_router = Router()
currency_router.message.filter(ChatTypeFilter(['private']))

# api token для сайта финанс
api_currency = os.getenv('API_CURRENCY')

# Определяем класс состояний для валюты
class Currency(StatesGroup):
    """Класс состояний для валюты"""
    amount = State()  # состояние ожидания количества базовой валюты
    base_currency = State()  # состояние ожидания базовой валюты
    target_currency = State()  # состояние ожидания целевой валюты

# Создаем константы для текстов, которые используются в декораторах
CURRENCY = __("Валюта 💵")
REPEAT = __("Повторить 💵")
BACK_TO_MAIN = __("Назад на главную ↩️")

async def update_num_text(message: Message, new_value: str):
    """функция обновления суммы операции"""
    await message.edit_text(_("Сумма операции: {new_value}").format(new_value=new_value),
                            reply_markup=keyboard.markup_num())

markup_cur = keyboard.get_callback_btns(btns={'$, USD 🇺🇸':'USD', '₽, RUB 🇷🇺':'RUB', '₾, GEL 🇬🇪':'GEL',
                                                                            '€, EUR 🇪🇺':'EUR', '₸, KZT 🇰🇿':'KZT', '₺, TRY 🇹🇷':'TRY',
                                                                            '¥, JPY 🇯🇵':'JPY', '₫, VND 🇻🇳':'VND', '¥ CNY 🇨🇳':'CNY',
                                                                            '₪, ILS 🇮🇱': 'ILS', '₱, PHP 🇵🇭': 'PHP', 'AED 🇦🇪': 'AED'},
                                                                            sizes=(3, 3, 3, 3,))
"""inline клавиатура с выбором валют"""


def get_currency_rate(base_currency, target_currency):
    """функция расчета кросс курса"""
    url = f'https://openexchangerates.org/api/latest.json?app_id={api_currency}'
    response = requests.get(url, timeout=20)
    try:
        if response.status_code == 200:
            try:
                data = response.json()
                base_rate = data['rates'].get(base_currency, 1.0)
                target_rate = data['rates'].get(target_currency, 1.0)
                rate = target_rate / base_rate
            except Exception as e:
                logger.error("Ошибка: %s", str(e))
                rate = _('Проблема в расчете курса')
            try:
                if 'timestamp' in data:
                    dt_object = datetime.fromtimestamp(data['timestamp'], tz=timezone.utc)
                    time = dt_object.strftime('%H:%M')
                    dt = dt_object.strftime('%d-%m-%Y')
                else:
                    raise ValueError("No timestamp in data")
            except Exception as e:
                logger.error("Ошибка: %s", str(e))
                time = _('Проблема в расчете времени.')
                dt = _('Проблема в расчете даты.')

            return time, dt, rate

        else:
            return 'time', 'dt', _('Ошибка: Проблема с подключением к API')

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        return 'time', 'dt', "Error: {str(e)}"




@currency_router.message(StateFilter(None), or_f(F.text == CURRENCY, F.text == REPEAT))
async def process_reopen(message: Message, state: FSMContext, workflow_data: dict):
    user_id = message.from_user.id
    await state.update_data(user_value='')
    await message.answer("💵", reply_markup=keyboard.del_kb)
    await message.answer(text=_("Сумма операции: 0.0"),
                         reply_markup=keyboard.markup_num())
    await state.set_state(Currency.amount)

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/service",
                    command_name="/currency")

@currency_router.callback_query(Currency.amount, F.data.startswith("num_"))
async def process_amout(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    user_value = state_data['user_value']
    action = callback.data.split("_")[1]
    try:
        if action == "enter":
            if len(user_value) > 0:
                await callback.message.edit_text(_("Сумма операции: {user_value}\nБазовая валюта: ").format(user_value=float(user_value)),
                                                 reply_markup=markup_cur) # type: ignore
                await state.update_data(currency_amount=user_value)
                await state.set_state(Currency.base_currency)
            else:
                await callback.message.edit_text(_("Сумма операции: 0.0"))
                await callback.message.answer(_("Что дальше?"),
                                              reply_markup=keyboard.get_keyboard(_("Повторить 💵"), _("Назад на главную ↩️"), placeholder='⬇️', sizes=(1, 1)))
                await callback.answer()
                await state.set_state(None)
                await state.update_data(currency_amount=None)
        elif action == "del" and len(user_value) > 0:
            user_value = user_value[:-1]
            await state.update_data(user_value=user_value)
            await update_num_text(callback.message, user_value) # type: ignore
        elif action == "del" and len(user_value) == 0:
            pass
        elif action == "com":
            user_value = user_value + '.'
            await state.update_data(user_value=user_value)
            await update_num_text(callback.message, user_value) # type: ignore
        else:
            user_value = user_value + action
            await state.update_data(user_value=user_value)
            await update_num_text(callback.message, user_value) # type: ignore
    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        await callback.message.edit_text(_("Ошибка в получении суммы"))
        await callback.message.answer(text=_("Что дальше?"),
                                      reply_markup=keyboard.get_keyboard(_("Повторить 💵"), _("Назад на главную ↩️"), placeholder='⬇️', sizes=(1, 1)))
        await callback.answer(_("Ошибка"))
        await state.set_state(None)
        await state.update_data(currency_amount=None)


@currency_router.message(Currency.amount)
async def process_amout_(message: Message):
    await message.answer(_("Вы ввели не допустимые данные, введите сумму используя inline кнопки"))

@currency_router.callback_query(Currency.base_currency, F.data)
async def process_base_currency(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    amount = state_data['currency_amount']
    base = callback.data
    await state.update_data(currency_base=base)
    await callback.message.edit_text(_("Сумма операции: {amount}\nБазовая валюта: {base}\nЦелевая валюта: ").format(amount=amount, base=base), reply_markup=markup_cur) # type: ignore
    await callback.answer()
    await state.set_state(Currency.target_currency)

@currency_router.message(Currency.base_currency)
async def process_base_currency_(message: Message):
    await message.answer(_("Вы ввели не допустимые данные, введите базовую валюту используя inline кнопки"))


@currency_router.callback_query(Currency.target_currency, F.data)
async def process_target_currency(callback: CallbackQuery, state: FSMContext):
    target = callback.data
    state_data = await state.get_data()
    amount = state_data['currency_amount']
    base = state_data['currency_base']
    time, dt, rate = get_currency_rate(base, target)  # type: ignore
    try:
        count = round(float(amount) * float(rate), 2)
        amount = str(amount)
        count = str(count)
        await callback.message.edit_text(_("Сумма операции: {amount}\nБазовая валюта: {base}\nЦелевая валюта: {target}\n\n<i>{dt},  {time}</i>\n\n<b>{amount} {base}  ~  {count} {target}</b>")
                                         .format(amount=amount, base=base, target=target, dt=dt, time=time, count=count))
        await callback.message.answer(_("Что дальше?"),
                                      reply_markup=keyboard.get_keyboard(_("Повторить 💵"), _("Назад на главную ↩️"), placeholder='⬇️', sizes=(1, 1)))
    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        await callback.message.edit_text(f'{dt} {time}\n\nRate: {rate}')
        await callback.message.answer(text=_("Что дальше?"),
                                      reply_markup=keyboard.get_keyboard(_("Повторить 💵"), _("Назад на главную ↩️"), placeholder='⬇️', sizes=(1, 1)))
    await callback.answer(_('Успех'))
    await state.set_state(None)
    await state.update_data(currency_amount=None, currency_base=None, currency_target=None)

@currency_router.message(Currency.target_currency)
async def process_target_currency_(message: Message):
    await message.answer(_("Вы ввели не допустимые данные, введите целевую валюту используя inline кнопки"))
