"""
Настройка логирования для бота
"""
import logging
import logging.handlers
import os
from datetime import datetime
import config

# Создаём папку для логов, если её нет
LOG_DIR = "logs"
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


def setup_logging():
    """Настройка логирования для приложения"""
    
    # Основной логгер
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG)
    
    # Формат логов
    formatter = logging.Formatter(config.LOG_FORMAT)
    
    # Обработчик для консоли
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, config.LOG_LEVEL))
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Обработчик для файла
    log_file = os.path.join(LOG_DIR, f"bot_{datetime.now().strftime('%Y-%m-%d')}.log")
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5  # Хранить 5 файлов
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    return logger


# Инициализируем логирование при импорте модуля
logger = setup_logging()
