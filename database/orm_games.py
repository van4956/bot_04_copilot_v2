import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from icecream import ic
ic.configureOutput(includeContext=True, prefix=' >>> Debag >>> ')


from sqlalchemy import delete, select, update, desc
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Games


# добавляем данные одной игры в бд
async def orm_add_game(session: AsyncSession, data: dict):
    obj = Games(user_id=data["user_id"],
                user_name=data["user_name"],
                game_name=data["game_name"],
                score=data["score"])
    session.add(obj)
    await session.commit()

# получаем по всем играм всех юзеров находящиеся в бд
async def orm_get_games(session: AsyncSession):
    query = select(Games)
    result = await session.execute(query)
    return result.scalars().all()

async def get_top_scores(session: AsyncSession, game_name: str, limit: int = 10):
    """Получение топ N игроков для конкретной игры"""
    query = select(Games).where(Games.game_name == game_name).order_by(desc(Games.score)).limit(limit)
    result = await session.execute(query)
    return result.scalars().all()
