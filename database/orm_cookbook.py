import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from sqlalchemy import delete, select, text, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Cookbook

# добавляем рецепт в орм
async def orm_add_recipe(session: AsyncSession, data: dict):
    # создаем объект Product, передаем ему данные из data
    obj = Cookbook(recipe_name=data["recipe_name"],
                  author=data["author"],
                  description=data["description"],
                  price=float(data["price"]),
                  image=data["image"],)
    session.add(obj) # добавляем объект Product в сессию
    await session.commit() # закрепляем данные в базе данных

# получаем все рецепты находящиеся в бд
async def orm_get_recipes(session: AsyncSession):
    query = select(Cookbook)
    result = await session.execute(query)
    return result.scalars().all()

# получаем определенный рецепт по его id
async def orm_get_recipe(session: AsyncSession, recipe_id: int):
    query = select(Cookbook).where(Cookbook.recipe_id == recipe_id)
    result = await session.execute(query)
    return result.scalar()

# изменение определенного рецепта
async def orm_update_recipe(session: AsyncSession, recipe_id: int, data):
    query = update(Cookbook).where(Cookbook.recipe_id == recipe_id).values(
        recipe_name=data["recipe_name"],
        author=data["author"],
        description=data["description"],
        price=float(data["price"]),
        image=data["image"],)
    await session.execute(query)
    await session.commit()

# переупорядочивание ID рецептов
async def reorder_recipe_ids(session: AsyncSession):
    # Получаем все рецепты, отсортированные по ID
    query = select(Cookbook).order_by(Cookbook.recipe_id)
    recipes = (await session.execute(query)).scalars().all()

    # Обновляем ID для каждого рецепта последовательно
    for new_id, recipe in enumerate(recipes, start=1):
        recipe.recipe_id = new_id

    await session.commit()

# удаляем определенный рецепт
async def orm_delete_recipe(session: AsyncSession, recipe_id: int):
    query = delete(Cookbook).where(Cookbook.recipe_id == recipe_id)
    await session.execute(query)
    await session.commit()
    await reorder_recipe_ids(session)
