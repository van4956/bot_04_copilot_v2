# список команд которые мы отправляем боту
# команды в кнопке "Меню", либо через знак "/"

from aiogram.types import BotCommand

private_command = [
    BotCommand(command='main',description='main'),
    BotCommand(command='help',description='help'),
]

admin_command = [
    BotCommand(command='main',description='main'),
    BotCommand(command='help',description='help'),
    BotCommand(command='admin',description='admin'),
]
