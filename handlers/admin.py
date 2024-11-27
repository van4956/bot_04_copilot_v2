import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')


from aiogram import Router, F, Bot
from aiogram.filters import Command, CommandStart, CommandObject, or_f, StateFilter
from aiogram.types import Message, InlineKeyboardMarkup, CallbackQuery, ReplyKeyboardRemove, FSInputFile

from filters.is_admin import IsAdminGroupFilter, IsAdminListFilter
from filters.chat_type import ChatTypeFilter
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.utils.i18n import gettext as _
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_cookbook import orm_add_recipe, orm_delete_recipe, orm_get_recipe, orm_get_recipes, orm_update_recipe
from database.orm_users import orm_get_users
from common.keyboard import get_callback_btns, get_keyboard


admin_router = Router()
admin_router.message.filter(ChatTypeFilter(["private"]), IsAdminListFilter(is_admin=True))

# клавиатура админки
ADMIN_KB = get_keyboard(
    "Ассортимент Книги", "Добавить рецепт",
    "Информация о пользователях",
    "Назад на главную ↩️",
    placeholder="⬇️",
    sizes=(2,1,1),
    )

# класс состояний для добавления рецепта
class AddProduct(StatesGroup):
    """Класс состояний для добавления рецепта"""
    recipe_name = State()
    author = State()
    description = State()
    price = State()
    image = State()

    # атрибут для возможности изменения продукта, режим change
    product_for_change = None

    # свойство класса, словарь, нужен для вывода заскриптованных ответов пользователю
    texts = {
        'AddProduct:recipe_name': 'Введите название заново:',
        'AddProduct:author': 'Введите имя автора заново',
        'AddProduct:description': 'Введите описание заново:',
        'AddProduct:price': 'Введите количество заново:',
        'AddProduct:image': 'Этот стейт последний, поэтому...',
        }

# команда /admin
@admin_router.message(Command("admin"))
async def cmd_admin(message: Message, bot: Bot):
    if message.from_user.id in bot.admin_list:
        await message.answer(text=('Админка:\n\n'
                                    '/admin - режим адменистратора\n'
                                    '/start - перезапустить бота\n'
                                    '/data - состояние FSMContext\n'
                                    '/get_id - посмотреть id диалога\n'
                                    '/ping - количество апдейтов\n'
                                    '/users - пользователи\n'),
                            reply_markup=ADMIN_KB
                            )

# Here is some example !ping command ...
@admin_router.message(IsAdminListFilter(is_admin=True), Command(commands=["ping"]),)
async def cmd_ping_bot(message: Message, counter):
    await message.reply(f"ping-{counter}")


# команда /users, показывает полную информацию всех зарегистрированных пользователей
@admin_router.message(or_f(Command("users"), F.text == "Информация о пользователях"))
async def get_users_info(message: Message, session: AsyncSession):
    all_info = ['Информация зарегистрированных пользователей:\n']
    cnt_users = 0
    for user in await orm_get_users(session):
        user_status = 'm' if user.status == 'member' else 'k'
        info = f"<code>{user.user_id: <11}</code> | {user_status} | {user.flag} | {user.locale} | <code>{user.user_name}</code>"
        all_info.append(info)
        cnt_users += 1

    text = "\n".join(all_info)

    # Обрезаем запись, если она превышает 1000 символов
    if len(text) > 1000:
        text = text[:995] + "..."

    text = text + f"\n\nВсего {cnt_users} пользователей"

    await message.answer(text)


# ===================================< кулинарная книга >======================================================


@admin_router.message(F.text == "Ассортимент Книги")
async def assortment_cookbook(message: Message, session: AsyncSession):
    for recipe in await orm_get_recipes(session):
        caption = f"<b>{recipe.recipe_name}</b>\n<i>Автор: {recipe.author}</i>\n\n{recipe.description}\n"
        # Обрезаем подпись, если она превышает 1024 символа
        if len(caption) > 1024:
            caption = caption[:1021] + "..."
        try:
            await message.answer_photo(recipe.image,
                                       caption=caption,
                                       reply_markup=get_callback_btns(btns={"Удалить":f"delete_{recipe.recipe_id}",
                                                                            "Изменить":f"change_{recipe.recipe_id}"}))
        except Exception as e:
            logger.error("Ошибка вывода рецепта: %s", e)
            photo = FSInputFile("common/images/image_cookbook.jpg")
            await message.answer_photo(photo=photo,
                                       caption=caption,
                                       reply_markup=get_callback_btns(btns={"Удалить":f"delete_{recipe.recipe_id}",
                                                                            "Изменить":f"change_{recipe.recipe_id}"}))
    await message.answer("ОК, вот весь список рецептов ⏫", reply_markup=ADMIN_KB)

@admin_router.callback_query(F.data.startswith('delete_'))
async def delete_recipe_callback(callback: CallbackQuery, session: AsyncSession):
    recipe_id = callback.data.split("_")[-1]
    await orm_delete_recipe(session, int(recipe_id))
    await callback.answer("Рецепт удален") # метод answer обязателен; строка по желанию (выведет всплывашку)
    await callback.message.answer("Рецепт удален!") # отправить сообщение


# ========================< Код для машины состояний (FSM) AddProduct >===================================


# отлавливаем пустое состояние, если data начинается на change_
@admin_router.callback_query(StateFilter(None), F.data.startswith("change_"))
async def change_product_callback(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    recipe_id = callback.data.split("_")[-1] # определяем id продукта
    product_for_change = await orm_get_recipe(session, int(recipe_id)) # получаем данные продукта
    # ic(product_for_change)
    AddProduct.product_for_change = product_for_change # записываем их в атрибут объекта

    await callback.answer()
    await callback.message.answer("Введите название рецепта", reply_markup=ReplyKeyboardRemove()) # отправляем сообщение; убираем клавиатуру
    await state.set_state(AddProduct.recipe_name) # встаем в состояние ожидания ввода name

# ловим кнопку "Добавить рецепт", проверяем чтобы состояние было пустым
@admin_router.message(StateFilter(None), F.text == "Добавить рецепт")
async def add_product(message: Message, state: FSMContext):
    await message.answer("Введите название рецепта", # отправляем сообщение
                         reply_markup=ReplyKeyboardRemove() # удаляем клавиатуру
                         )
    await state.set_state(AddProduct.recipe_name) # встаем в состояние ожидания ввода name


# хендлер ОТМЕНЫ и сброса состояния, должен быть всегда именно здесь!
# после того как встали в состояние номер 1
@admin_router.message(StateFilter("*"), Command("отмена")) # ловим любое состояние пользователя, если введена команда "отмена", либо текст "отмена"
@admin_router.message(StateFilter("*"), or_f(F.text.casefold() == "отмена", F.text == "."))
async def cancel_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state() # получаем текущее состояние
    if current_state is None: # если состояния пустое, то ни чего не делаем
        return
    if AddProduct.product_for_change:
        AddProduct.product_for_change = None
    await state.set_state(None)
    await state.update_data(recipe_name=None, author=None, description=None, price=None, image=None)
    await message.answer("Действия отменены",
                         reply_markup=ADMIN_KB) # выводим всплывающее сообщение, возвращаем клавиатуру

# вернутся на шаг назад (на прошлое состояние)
@admin_router.message(StateFilter("*"), Command("назад"))
@admin_router.message(StateFilter("*"), F.text.casefold() == "назад")
async def back_handler(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state() # получаем текущее состояние

    if current_state == AddProduct.recipe_name:
        await message.answer('Предыдущего шага нет, или введите название рецепта, или напишите "отмена"')
        return

    previous = None
    for step in AddProduct.__all_states__:
        if step.state == current_state:
            await state.set_state(previous)
            await message.answer(f"Ок, вы вернулись к прошлому шагу \n{AddProduct.texts[previous.state]}") # type: ignore
            return
        previous = step
    await message.answer("Ок, вы вернулись к прошлому шагу")


# ловим состояние ожидания name, и наличие вводимого текста, либо две точки
@admin_router.message(AddProduct.recipe_name, or_f(F.text, F.text == '..'))
async def add_name(message: Message, state: FSMContext):
    if message.text == '..':
        await state.update_data(recipe_name=AddProduct.product_for_change.recipe_name)
    else:
        if len(message.text) > 100: # type: ignore
            await message.answer('Название не должно превышать 100 символов!\nВведите название заново')
            return
        await state.update_data(recipe_name=message.text) # передаем название из полученного текста в атрибут name объекта state
    await message.answer("Введите имя автора рецепта")
    await state.set_state(AddProduct.author)
    # await message.answer("Введите описание рецепта") # отправляем сообщение юзеру
    # await state.set_state(AddProduct.description) # встаем в состояние ожидания description

# хендлер для отлова некорректных ввода для состояния name
@admin_router.message(AddProduct.recipe_name)
async def add_name2(message: Message):
    await message.answer("Вы ввели не допустимые данные, введите название рецепта")

# ловим состояние ожидания author, и, если поступает текст, или точка
@admin_router.message(AddProduct.author, or_f(F.text, F.text == '..'))
async def add_author(message: Message, state: FSMContext):
    if message.text == '..':
        await state.update_data(author=AddProduct.product_for_change.author)
    else:
        await state.update_data(author=message.text)
    await message.answer("Введите описание рецепта") # отправляем сообщение юзеру
    await state.set_state(AddProduct.description) # встаем в состояние ожидания description

# хендлер для отлова некорректных ввода для состояния author
@admin_router.message(AddProduct.author)
async def add_author2(message: Message):
    await message.answer("Вы ввели не допустимые данные, введите имя автора рецепта")

# ловим стостяние ожидание description, и если поступает текст, или точка
@admin_router.message(AddProduct.description, or_f(F.text, F.text == '..'))
async def add_description(message: Message, state: FSMContext):
    if message.text == '..':
        await state.update_data(description=AddProduct.product_for_change.description)
    else:
        await state.update_data(description=message.text) # передаем описание из полученного текста пользователя
    await message.answer("Введите количество приготовлений")
    await state.set_state(AddProduct.price) # встаем в состояние ожидания price

# хендлер для отлова некорректного ввода состояния description
@admin_router.message(AddProduct.description)
async def add_description2(message: Message):
    await message.answer("Вы ввели не допустимые данные, введите описание рецепта")


# ловим стостяние ожидание price, и если поступает текст, либо точка
@admin_router.message(AddProduct.price, or_f(F.text, F.text == '..'))
async def add_price(message: Message, state: FSMContext):
    if message.text == '..':
        await state.update_data(price=AddProduct.product_for_change.price)
    else:
        try:
            float(message.text) # type: ignore
        except ValueError:
            await message.answer("Введите корректное количество")
            return
        await state.update_data(price=message.text) # передаем цену

    await message.answer("Загрузите изображение блюда")
    await state.set_state(AddProduct.image) # встаем в состояние ожидания картинки

# хендлер для отлова некорректных ввода для состояния price
@admin_router.message(AddProduct.price)
async def add_price2(message: Message):
    await message.answer("Вы ввели не допустимые данные, введите количество приготовлений")


# ловим данные для состояние image и потом выходим из состояний
@admin_router.message(AddProduct.image, or_f(F.photo, F.text == '..'))
async def add_image(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == '..':
        await state.update_data(image=AddProduct.product_for_change.image)
    else:
        await state.update_data(image=message.photo[-1].file_id) # type: ignore
    data = await state.get_data() # скачать данные из state в переменную data
    try:
        if AddProduct.product_for_change: # если объект AddProduct имеет значение product_for_change
            await orm_update_recipe(session, recipe_id=AddProduct.product_for_change.recipe_id, data=data)
            await message.answer('Рецепт изменен', reply_markup=ADMIN_KB)
            await state.set_state(None)
            await state.update_data(recipe_name=None, author=None, description=None, price=None, image=None)
        else:
            await orm_add_recipe(session, data) # иначе просто добаляем данные в бд
            await message.answer("Рецепт добавлен", reply_markup=ADMIN_KB) # отправляем ответ, возвращаем клавиатуру
            await state.set_state(None)
            await state.update_data(recipe_name=None, author=None, description=None, price=None, image=None)
    except Exception as e: # если ловим ошибку
        await message.answer(f"Ошибка: {str(e)}\nОбратись к администратору!",
                             reply_markup=ADMIN_KB,)
        await state.set_state(None)
        await state.update_data(recipe_name=None, author=None, description=None, price=None, image=None)

    AddProduct.product_for_change = None

@admin_router.message(AddProduct.image)
async def add_image2(message: Message):
    await message.answer("Отправьте фото блюда")
