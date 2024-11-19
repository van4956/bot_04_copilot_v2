import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')

import requests
import os
import datetime

from aiogram import F, Router, Bot
from aiogram.fsm.state import State, StatesGroup
from aiogram.enums import ParseMode
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from aiogram.utils.i18n import lazy_gettext as __
from common import keyboard
from filters.chat_type import ChatTypeFilter

# создаем роутер
weather_router = Router()
weather_router.message.filter(ChatTypeFilter(['private']))

# api токен для сайта погоды
token = os.getenv('API_WEATHER')

# Определяем класс состояния прогноза погоды
class City(StatesGroup):
    """Класс состояния прогноза погоды"""
    forecast_moment = State()
    forecast_period = State()
    city_name_moment = State()  # Состояние, в котором бот ожидает ввода названия города для прогноза в текущем моменте
    city_name_period = State()  # Состояние, в котором бот ожидает ввода названия города для прогноза на период

dict_weather_descriptions = {
    "ясно": "☀️",
    "несколько облаков": "🌤",
    "небольшая облачность": "🌤",
    "переменная облачность": "⛅️",
    "облачно с прояснениями": "🌥",
    "пасмурно": "☁️",
    "слабый дождь": "🌦",
    "небольшой дождь": "🌦",
    "умеренный дождь": "🌧",
    "дождь": "🌧",
    "сильный дождь": "🌧",
    "очень сильный дождь": "🌧",
    "проливной дождь": "🌧",
    "моросящий дождь": "🌧",
    "морось": "🌦",
    "слабая морось": "🌦",
    "гроза": "🌩",
    "гроза с дождем": "⛈",
    "сильная гроза": "⛈",
    "гроза с крупным градом": "⛈",
    "слабый снег": "🌨",
    "снег": "❄️",
    "сильный снег": "🌨",
    "снегопад": "🌨",
    "снежные заряды": "🌨",
    "туман": "🌫",
    "дымка": "🌫",
    "мгла": "🌫",
    "пыль": "🌪",
    "песок": "🌪",
    "пепел": "🌋",
    "шквал": "🌬",
    "торнадо": "🌪"
}

# Создаем константы для текстов, которые используются в декораторах
WATER = __("Погода 🌊")
CURRENT = __("Текущий ⏺")
FOR_3_DAYS = __("На 3 дня ⏩")
BACK_TO_MAIN = __("Назад на главную ↩️")
CITY_BY_NAME = __("По названию 🏙")


# кнопка "погода"
@weather_router.message(F.text == WATER)
async def water_cmd(message: Message, workflow_data: dict):
    user_id = message.from_user.id
    await message.answer(_("Выберите период прогноза"),
                         reply_markup=keyboard.get_keyboard(_("Текущий ⏺"), _("На 3 дня ⏩"), _("Назад на главную ↩️"),
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

    analytics = workflow_data['analytics']
    await analytics(user_id=user_id,
                    category_name="/service",
                    command_name="/weather")


# Функция получения погоды через OpenWeatherMap
def parse_weather_data(type_forecast, city, lat, lon, locale='ru'):
    """Функция получения погоды через OpenWeatherMap;
       type_forecast определяет, показать погоду в моменте, или на 5 дней;
       city - название города, lat - широта, lon - долгота;
       locale - локаль, по умолчанию 'ru' """

    # moment weather
    if type_forecast == 1:
        if city:
            url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={token}&units=metric&lang={locale}"
        elif lat and lon:
            url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={token}&units=metric&lang={locale}"

    # forecast for 5 days with data every 3 hours
    elif type_forecast == 2:
        if city:
            url = f'https://api.openweathermap.org/data/2.5/forecast?q={city}&appid={token}&units=metric&lang={locale}'
        elif lat and lon:
            url = f'https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={token}&units=metric&lang={locale}'

    try:
        req = requests.get(url, timeout=10)
        data = req.json()

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        text = _("Ошибка получения информации от OpenWeatherMap - {e}").format(e=str(e))
        return text

    try:
        if type_forecast == 1:
            temp = data['main']['temp'] # Температура
            humidity = data['main']['humidity'] # Влажность, %
            wind = data['wind']['speed'] # Скорость ветра, метр/сек
            dt = data['dt'] # Время расчета данных, unix, UTC
            timezone = data['timezone'] #Сдвиг в секундах от UTC
            dt_object = datetime.datetime.fromtimestamp(dt + timezone, tz=datetime.timezone.utc) # Конвертация в читаемый формат
            time = dt_object.strftime('%d-%m-%Y  %H:%M') # Форматирование даты и времени в желаемый вид
            name = data['name'] # Название города
            lon = data['coord']['lon']
            lat = data['coord']['lat']
            description = data['weather'][0]['description']
            emoji = dict_weather_descriptions.get(description, description)

            result = (f"<code>{name}</code>\n<code>{lat}° {lon}°</code>\n\n"
                            f"<code>{str(round(temp,1))}°C\n{str(humidity)} %\n{str(round(wind,1))} 𝑣</code>\n<code>{emoji}</code>\n\n"
                            f"<code>{time}</code>")

            return result

        elif type_forecast == 2:
            result = []
            city = data['city']['name']
            lat = data['city']['coord']['lat']
            lon = data['city']['coord']['lon']
            text_head = f'<code>{city}</code>\n<code>{lat}° {lon}°</code>'
            result.append(text_head)

            timezone = data['city']['timezone']
            weather_list = data['list']
            day = 0
            cnt_day = 0
            for entry in weather_list:
                dt_obj = datetime.datetime.fromtimestamp(entry['dt'] + timezone, tz=datetime.timezone.utc)
                dt = dt_obj.strftime('%d.%m %H:%M')
                temp_celsius = round(entry['main']['temp'],1)
                humidity = entry['main']['humidity']
                description = entry['weather'][0]['description']
                emoji = dict_weather_descriptions.get(description, 'None')
                wind_speed = round(entry['wind']['speed'],1)
                text = f"{dt} | {temp_celsius}° | {humidity}% | {wind_speed}𝑣 | {emoji}"

                if day != int(dt[:2]):
                    day = int(dt[:2])
                    text = '\n' + text
                    cnt_day += 1

                # оставляем только 4 дня в отчете
                if cnt_day > 3:
                    break

                result.append(text)

            result = "\n".join(result)

            return result

    except Exception as e:
        logger.error("Ошибка: %s", str(e))
        text = _("Ошибка в расчете json файла - {e}").format(e=str(e))
        return text


@weather_router.message(F.text == CURRENT)
async def water_moment_cmd(message: Message, state:FSMContext):
    await state.set_state(City.forecast_moment)
    await message.answer(_("Каким способом определить прогноз?"),
                         reply_markup=keyboard.get_keyboard(_("По названию 🏙"), _("По локации 🗺"), _("Назад на главную ↩️"),
                                                                 request_location=1,
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

@weather_router.message(F.text == FOR_3_DAYS)
async def water_period_cmd(message: Message, state: FSMContext):
    await state.set_state(City.forecast_period)
    await message.answer(_("Каким способом определить прогноз?"),
                         reply_markup=keyboard.get_keyboard(_("По названию 🏙"), _("По локации 🗺"), _("Назад на главную ↩️"),
                                                                 request_location=1,
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

# =====================================< Текущий ⏺ >======================================================

@weather_router.edited_message()
@weather_router.message(City.forecast_moment, F.text == CITY_BY_NAME)
async def city_message_moment(message: Message, state: FSMContext):
    await message.answer(_('Введите название населенного пункта'), reply_markup=keyboard.del_kb)
    await state.set_state(City.city_name_moment)

@weather_router.message(City.city_name_moment, F.text)
async def process_city_moment(message: Message, state: FSMContext):
    await state.update_data(city_name_moment=message.text)
    city_name_moment = message.text
    data_state = await state.get_data()
    user_locale = data_state.get('locale')
    weather_info = parse_weather_data(1, city=city_name_moment, lat=None, lon=None, locale=user_locale) # type: ignore
    await state.set_state(None)
    await state.update_data(city_name_moment=None)
    await message.answer(weather_info, parse_mode=ParseMode.HTML)
    await message.answer(_("Выберите период прогноза"),
                         reply_markup=keyboard.get_keyboard(_("Текущий ⏺"), _("На 3 дня ⏩"), _("Назад на главную ↩️"),
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

@weather_router.message(City.city_name_moment)
async def process_city_moment_(message: Message):
    await message.answer(_("Вы ввели не допустимые данные, введите название населенного пункта"))

# =====================================< На 3 дня ⏩ >======================================================

@weather_router.edited_message()
@weather_router.message(City.forecast_period, F.text == CITY_BY_NAME)
async def city_message_period(message: Message, state: FSMContext):
    await message.answer(_('Введите название населенного пункта'), reply_markup=keyboard.del_kb)
    await state.set_state(City.city_name_period)

@weather_router.message(City.city_name_period, F.text)
async def process_city_period(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(city_name_period=message.text)
    city_name_period = message.text
    data_state = await state.get_data()
    user_locale = data_state.get('locale')
    weather_info = parse_weather_data(2, city=city_name_period, lat=None, lon=None, locale=user_locale) # type: ignore
    await state.set_state(None)
    await state.update_data(city_name_period=None)
    await message.answer(weather_info, parse_mode=ParseMode.HTML)
    await message.answer(_("Выберите период прогноза"),
                         reply_markup=keyboard.get_keyboard(_("Текущий ⏺"), _("На 3 дня ⏩"), _("Назад на главную ↩️"),
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

@weather_router.message(City.city_name_period)
async def process_city_period_(message: Message):
    await message.answer(_("Вы ввели не допустимые данные, введите название населенного пункта"))


@weather_router.edited_message()
@weather_router.message(F.location, City.forecast_moment)
async def loc_message_moment(message: Message, state: FSMContext):
    await message.answer(_('Локация получена'))
    await state.set_state(None)
    await state.update_data(city_name_moment=None)
    data_state = await state.get_data()
    user_locale = data_state.get('locale')
    weather_info = parse_weather_data(1, city=None, lat=message.location.latitude, lon=message.location.longitude, locale=user_locale) # type: ignore
    await message.answer(weather_info, parse_mode=ParseMode.HTML)
    await message.answer(_("Выберите период прогноза"),
                         reply_markup=keyboard.get_keyboard(_("Текущий ⏺"), _("На 3 дня ⏩"), _("Назад на главную ↩️"),
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))

@weather_router.edited_message()
@weather_router.message(F.location, City.forecast_period)
async def loc_message_period(message: Message, state: FSMContext):
    await message.answer(_('Локация получена'))
    await state.set_state(None)
    await state.update_data(city_name_period=None)
    data_state = await state.get_data()
    user_locale = data_state.get('locale')
    weather_info = parse_weather_data(2, city=None, lat=message.location.latitude, lon=message.location.longitude, locale=user_locale) # type: ignore
    await message.answer(weather_info, parse_mode=ParseMode.HTML)
    await message.answer(_("Выберите период прогноза"),
                         reply_markup=keyboard.get_keyboard(_("Текущий ⏺"), _("На 3 дня ⏩"), _("Назад на главную ↩️"),
                                                                 sizes=(2, 1,),
                                                                 placeholder='⬇️'))
