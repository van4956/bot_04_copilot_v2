import logging

# Инициализируем логгер модуля
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.info("Загружен модуль: %s", __name__)

from aiogram.filters import BaseFilter
from aiogram.types import Message
from aiogram import Bot

class IsAdminGroupFilter(BaseFilter):
    """
    Фильтр, проверяет наличие прав администратора в группе, у пользователя отправившего сообщение
    """
    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def __call__(self, message: Message) -> bool:
        member = await message.bot.get_chat_member(message.chat.id, message.from_user.id)
        return member.is_chat_admin() == self.is_admin

class IsAdminListFilter(BaseFilter):
    """
    Фильтр, проверяет находится ли ID пользователя, отправившего сообщение, в нашем списке администраторов
    """
    def __init__(self, is_admin: bool):
        self.is_admin = is_admin

    async def __call__(self, message: Message, bot: Bot) -> bool:
        return (message.from_user.id in bot.admin_list) & self.is_admin
