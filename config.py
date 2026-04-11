"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Параметры поиска
MAX_RESULTS = 5  # Максимальное количество результатов на запрос
SEARCH_TIMEOUT = 10  # Timeout для запросов в секундах

# Интернет-магазины для поиска
STORES = {
    "amazon": "https://www.amazon.eu",
    "ebay": "https://www.ebay.com",
    "aliexpress": "https://www.aliexpress.com",
}

# User-Agent для запросов
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
]
