#!/usr/bin/env python3
"""
⚡ БЫСТРЫЙ СТАРТ

Этот скрипт поможет вам быстро начать работу с ботом.
"""

import os
import sys
from pathlib import Path

def print_banner():
    """Печать красивого баннера"""
    print("""
╔════════════════════════════════════════════════════════╗
║  🤖 TELEGRAM БОТ ПОИСКА ДЕШЁВЫХ ТОВАРОВ             ║
║  ⚡ БЫСТРЫЙ СТАРТ                                    ║
╚════════════════════════════════════════════════════════╝
    """)

def check_files():
    """Проверка наличия всех файлов"""
    print("📁 Проверка файлов...")
    
    required_files = [
        "bot.py",
        "search.py",
        "config.py",
        "examples.py",
        "logger.py",
        "requirements.txt",
        ".env.example",
    ]
    
    missing_files = []
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        print(f"❌ Отсутствуют файлы: {', '.join(missing_files)}")
        return False
    
    print("✅ Все файлы присутствуют")
    return True

def check_python_version():
    """Проверка версии Python"""
    print("\n🐍 Проверка версии Python...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Требуется Python 3.8+, у вас {sys.version_info.major}.{sys.version_info.minor}")
        return False
    
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor}")
    return True

def check_dependencies():
    """Проверка установленных зависимостей"""
    print("\n📦 Проверка зависимостей...")
    
    # Маппинг имен пакетов на имена модулей
    packages = {
        "aiogram": "aiogram",
        "aiohttp": "aiohttp",
        "beautifulsoup4": "bs4",
        "requests": "requests",
        "python-dotenv": "dotenv",
    }
    
    missing_packages = []
    for package_name, module_name in packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"❌ Отсутствуют пакеты: {', '.join(missing_packages)}")
        print("\n💡 Установите зависимости командой:")
        print("   pip install -r requirements.txt")
        return False
    
    print("✅ Все зависимости установлены")
    return True

def check_env_file():
    """Проверка файла .env"""
    print("\n⚙️  Проверка конфигурации...")
    
    if not os.path.exists(".env"):
        print("❌ Файл .env не найден")
        print("\n💡 Создайте файл .env из шаблона:")
        print("   cp .env.example .env")
        return False
    
    with open(".env", "r") as f:
        content = f.read()
        if "YOUR_BOT_TOKEN_HERE" in content:
            print("⚠️  Токен не установлен в файле .env")
            print("\n💡 Получите токен у @BotFather в Telegram и обновите .env")
            return False
    
    print("✅ Файл .env правильно настроен")
    return True

def show_next_steps():
    """Показать следующие шаги"""
    print("\n" + "="*60)
    print("✅ СИСТЕМА ГОТОВА К РАБОТЕ!")
    print("="*60)
    
    print("""
📝 СЛЕДУЮЩИЕ ШАГИ:

1. 🎯 Локальное тестирование (БЫСТРЫЙ РЕЖИМ):
   python test_local.py

2. 🚀 Запуск бота:
   python bot.py

3. 📚 Документация:
   - README.md - основная информация
   - PROJECT_STRUCTURE.md - структура проекта
   - DEPLOY.md - развёртывание на сервер
   - API_EXAMPLES.md - примеры интеграции с API

4. 🧪 Тестирование:
   python test_bot.py        # автотесты
   python test_local.py      # локальное тестирование

⚙️  НАСТРОЙКА:

• Бот использует реальный поиск eBay через официальный API
• Убедитесь, что TELEGRAM_BOT_TOKEN задан в `.env`
• Для поиска eBay настройте EBAY_APP_ID в `.env` (опционально)

🔌 EBAY API (РЕКОМЕНДУЕТСЯ):

• Зарегистрируйтесь: https://developer.ebay.com/
• Получите App ID и добавьте в .env:
  EBAY_APP_ID=YOUR_APP_ID_HERE
• Без App ID поиск eBay будет недоступен

💡 СОВЕТ:
   Вы можете протестировать бота в Telegram:
   1. Откройте бота по ссылке из @BotFather
   2. Отправьте /start
   3. Напишите название товара (например: iPhone)
    """)

def main():
    """Главная функция"""
    print_banner()
    
    checks = [
        ("Python", check_python_version),
        ("Файлы", check_files),
        ("Зависимости", check_dependencies),
        ("Конфигурация", check_env_file),
    ]
    
    all_passed = True
    for name, check_func in checks:
        try:
            if not check_func():
                all_passed = False
        except Exception as e:
            print(f"❌ Ошибка при проверке {name}: {e}")
            all_passed = False
    
    if all_passed:
        show_next_steps()
        print("\n" + "="*60)
        print("🎉 ГОТОВО К РАБОТЕ!")
        print("="*60 + "\n")
    else:
        print("\n" + "="*60)
        print("❌ ИСПРАВЬТЕ ОШИБКИ ВЫШЕ")
        print("="*60 + "\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
