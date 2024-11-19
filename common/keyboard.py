import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, KeyboardButtonPollType, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from aiogram.utils.i18n import gettext as _



# Удаление клавиатуры
del_kb = ReplyKeyboardRemove()

# del_inline_kb = ReplyI


# Функция создания клавиатуры
def get_keyboard(
    *btns: str,
    placeholder: str | None = None,
    request_contact: int | None = None,
    request_location: int | None = None,
    sizes: tuple = (2,),
):
    '''
    Функция создания обычной клавиатуры.
    Параметры request_contact и request_location должны быть индексами аргументов btns для нужных вам кнопок.
    Пример:
    get_keyboard("Меню", "Варианты оплаты", "Варианты доставки", "Отправить номер телефона", placeholder="Что вас интересует?", request_contact=3, sizes=(2, 2, 1))
    '''
    keyboard = ReplyKeyboardBuilder()

    for index, text in enumerate(btns, start=0):
        if request_contact and request_contact == index:
            keyboard.add(KeyboardButton(text=text, request_contact=True))
        elif request_location and request_location == index:
            keyboard.add(KeyboardButton(text=text, request_location=True))
        else:
            keyboard.add(KeyboardButton(text=text))

    return keyboard.adjust(*sizes).as_markup(resize_keyboard=True, # сделать кнопки поменьше
                                             input_field_placeholder=placeholder) # в поле ввода выводим текст placeholder


# Функция стартовой клавиатуры
def start_keyboard():
    return get_keyboard(_("Погода 🌊"), _("Валюта 💵"), _("Котики 🐱"), _("LLMs 🤖"), sizes=(2, 2, ), placeholder='⬇️')


# создать обычные inline кнопки с отображаемым текстом
def get_callback_btns(*, # запрет на передачу неименованных аргументов
                      btns: dict[str, str], # передаем словарик text:data, text то что будет отображаться в боте, data то что отправится внутри
                      sizes: tuple = (2,)): # кортеж, разметка кнопок
    """создать обычные кнопки с отображаемым текстом"""

    keyboard = InlineKeyboardBuilder()

    for text, data in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, callback_data=data)) # событие callback_data

    return keyboard.adjust(*sizes).as_markup()


# создать inline кнопки с url ссылками
def get_url_btns(*,
                 btns: dict[str, str],
                 sizes: tuple = (2,)):
    """создать кнопки с url ссылками"""

    keyboard = InlineKeyboardBuilder()

    for text, url in btns.items():
        keyboard.add(InlineKeyboardButton(text=text, url=url))

    return keyboard.adjust(*sizes).as_markup()


# создать микс из CallBack кнопок и URL кнопок
def get_inlineMix_btns(*,
                       btns: dict[str, str],
                       sizes: tuple = (2,)):
    """создать микс из CallBack кнопок и URL кнопок"""

    keyboard = InlineKeyboardBuilder()

    for text, value in btns.items():
        if '://' in value:
            keyboard.add(InlineKeyboardButton(text=text, url=value))
        else:
            keyboard.add(InlineKeyboardButton(text=text, callback_data=value))

    return keyboard.adjust(*sizes).as_markup()

# inline клавиатура с цифрами и точкой, удалением и вводом
def markup_num():
    """inline клавиатура с цифрами и точкой, удалением и вводом"""
    buttons = [
                        [InlineKeyboardButton(text=" 1 ", callback_data="num_1"),
                        InlineKeyboardButton(text="   2   ", callback_data="num_2"),
                        InlineKeyboardButton(text=" 3 ", callback_data="num_3")],
                        [InlineKeyboardButton(text=" 4 ", callback_data="num_4"),
                        InlineKeyboardButton(text=" 5 ", callback_data="num_5"),
                        InlineKeyboardButton(text="   6   ", callback_data="num_6")],
                        [InlineKeyboardButton(text=" 7 ", callback_data="num_7"),
                        InlineKeyboardButton(text=" 8 ", callback_data="num_8"),
                        InlineKeyboardButton(text=" 9 ", callback_data="num_9")],
                        [InlineKeyboardButton(text=" 0 ", callback_data="num_0"),
                         InlineKeyboardButton(text=" 000 ", callback_data="num_000"),
                         InlineKeyboardButton(text=" . ", callback_data="num_com")],
                        [InlineKeyboardButton(text="◀️ delete", callback_data="num_del"),
                        InlineKeyboardButton(text="enter ▶️", callback_data="num_enter")]
                    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard

# inline клавиатура только с 9 цифрами
def markup_num_9():
    """inline клавиатура только с 9 цифрами"""
    buttons = [
                        [InlineKeyboardButton(text=" 1 ", callback_data="num_1"),
                        InlineKeyboardButton(text=" 2 ", callback_data="num_2"),
                        InlineKeyboardButton(text=" 3 ", callback_data="num_3")],
                        [InlineKeyboardButton(text=" 4 ", callback_data="num_4"),
                        InlineKeyboardButton(text=" 5 ", callback_data="num_5"),
                        InlineKeyboardButton(text=" 6 ", callback_data="num_6")],
                        [InlineKeyboardButton(text=" 7 ", callback_data="num_7"),
                        InlineKeyboardButton(text=" 8 ", callback_data="num_8"),
                        InlineKeyboardButton(text=" 9 ", callback_data="num_9")],
                    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard