import requests
import os
import sys

# Добавляем путь к корневой директории проекта
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config_data.config import load_config
config = load_config()

TOKEN = config.tg_bot.token_test
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

response = requests.get(URL, timeout=30)
print(response.json())
