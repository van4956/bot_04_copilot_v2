import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from sqlalchemy import DateTime, Float, String, Text, Integer, func, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    '''первичный класс, от него дальше будут наследоваться все остальные'''
    created: Mapped[DateTime] = mapped_column(DateTime, default=func.now())
    updated: Mapped[DateTime] = mapped_column(DateTime, default=func.now(), onupdate=func.now())


class Users(Base):
    '''class Users соответствует таблице users в базе данных'''
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True, autoincrement=True)
    user_name: Mapped[str] = mapped_column(String(150), nullable=False)
    full_name: Mapped[str] = mapped_column(String(150), nullable=False)
    locale: Mapped[str] = mapped_column(String(150), nullable=False)
    status: Mapped[str] = mapped_column(String(150), nullable=False)
    flag: Mapped[int] = mapped_column(Integer, nullable=False)  # возможность для тротлинга

# class Cookbook соответствует таблице cookbook в базе данных
class Cookbook(Base):
    '''class Cookbook соответствует таблице cookbook в базе данных'''
    __tablename__ = "cookbook"

    recipe_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    recipe_name: Mapped[str] = mapped_column(String(150), nullable=False)
    author: Mapped[str] = mapped_column(String(150))
    description: Mapped[str] = mapped_column(Text)
    price: Mapped[float] = mapped_column(Float(asdecimal=True), nullable=False)
    image: Mapped[str] = mapped_column(String(150))

# class Games соответствует таблице games в базе данных
class Games(Base):
    '''class Games соответствует таблице games в базе данных'''
    __tablename__ = "games"

    game_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    game_name: Mapped[str] = mapped_column(String(150), nullable=False)
    user_id: Mapped[int] = mapped_column(BigInteger, nullable=False)
    user_name: Mapped[str] = mapped_column(String(150), nullable=False)
    score: Mapped[int] = mapped_column(Integer, nullable=False)