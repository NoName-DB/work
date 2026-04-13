"""
Конфигурация бота
"""
import os
from dotenv import load_dotenv

# Загрузить переменные окружения из .env файла
load_dotenv()

# Telegram Bot Token
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")

# eBay API Configuration
EBAY_APP_ID = os.getenv("EBAY_APP_ID", "YOUR_EBAY_APP_ID_HERE")
EBAY_API_URL = "https://svcs.ebay.com/services/search/FindingService/v1"

# Логирование
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

# Параметры поиска
MAX_RESULTS = 5  # Максимальное количество результатов на запрос
SEARCH_TIMEOUT = 10  # Timeout для запросов в секундах
CACHE_TTL = int(os.getenv("CACHE_TTL", "300"))  # Seconds to cache query results
POPULAR_SEARCHES = [
    "iPhone", "Samsung Galaxy", "MacBook", "PlayStation 5",
    "Nike кроссовки", "Adidas майка", "Sony наушники",
    "Canon фотоаппарат", "LG телевизор", "Bosch стиральная машина",
    "IKEA стул", "Samsung холодильник", "Xiaomi робот-пылесос",
    "LEGO конструктор", "Nintendo Switch", "Dyson пылесос",
    "Philips бритва", "Oral-B зубная щётка", "KitchenAid миксер"
]
MAX_HISTORY = int(os.getenv("MAX_HISTORY", "10"))

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

# Google Custom Search API
GOOGLE_CSE_API_KEY = os.getenv("GOOGLE_CSE_API_KEY", "")
GOOGLE_CSE_ENGINE_ID = os.getenv("GOOGLE_CSE_ENGINE_ID", "")

# Google Shopping API
GOOGLE_SHOPPING_API_KEY = os.getenv("GOOGLE_SHOPPING_API_KEY", "")
GOOGLE_SHOPPING_CX = os.getenv("GOOGLE_SHOPPING_CX", "")

# Price tracking
PRICE_CHECK_INTERVAL = int(os.getenv("PRICE_CHECK_INTERVAL", "3600"))  # seconds
PRICE_CHANGE_THRESHOLD = float(os.getenv("PRICE_CHANGE_THRESHOLD", "0.05"))  # 5% change

# History storage
HISTORY_FILE = os.getenv("HISTORY_FILE", "user_history.json")
TRACKING_FILE = os.getenv("TRACKING_FILE", "price_tracking.json")
