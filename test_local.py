#!/usr/bin/env python3
"""
Быстрое локальное тестирование бота
Позволяет тестировать функционал без запуска Telegram бота
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую папку в PATH
sys.path.insert(0, str(Path(__file__).parent))

import config
from search import search_products, format_search_results


async def test_search(query: str):
    """Протестировать поиск товаров"""
    print(f"\n{'='*60}")
    print(f"🔍 Поиск: {query}")
    print('='*60)
    
    products = await search_products(query)
    
    if not products:
        print("❌ Товары не найдены")
        return
    
    message = format_search_results(products)
    print(message)


async def interactive_mode():
    """Интерактивный режим тестирования"""
    print("\n" + "="*60)
    print("🤖 ИНТЕРАКТИВНОЕ ТЕСТИРОВАНИЕ БОТА")
    print(f"Максимум результатов: {config.MAX_RESULTS}")
    print("\nДля выхода введите 'exit' или 'quit'")
    print("-"*60)
    
    while True:
        try:
            query = input("\n📝 Введите поисковый запрос: ").strip()
            
            if query.lower() in ['exit', 'quit', 'выход', 'выхода']:
                print("\n👋 До встречи!")
                break
            
            if not query:
                print("❌ Введите непустой запрос")
                continue
            
            await test_search(query)
            
        except KeyboardInterrupt:
            print("\n\n👋 Программа прервана")
            break
        except Exception as e:
            print(f"❌ Ошибка: {e}")


async def search_test():
    """Автоматический тест поиска"""
    print("\n" + "="*60)
    print("📋 АВТОМАТИЧЕСКИЙ ТЕСТ ПОИСКА")
    print("="*60)
    
    test_queries = [
        ("iPhone", "Apple iPhone"),
        ("Nike", "Nike кроссовки"),
        ("Samsung", "Samsung смартфоны"),
        ("random product xyz", "несуществующий товар"),
    ]
    
    for query, description in test_queries:
        print(f"\n📦 Тестирование: {description}")
        print(f"   Запрос: '{query}'")
        
        products = await search_products(query)
        
        if products:
            print(f"   ✅ Найдено {len(products)} товаров")
            for i, p in enumerate(products, 1):
                print(f"      {i}. {p.name} - {p.price} {p.currency} ({p.store})")
        else:
            print(f"   ❌ Товары не найдены")


async def main():
    """Главная функция"""
    print("\n" + "="*60)
    print("🚀 ЛОКАЛЬНОЕ ТЕСТИРОВАНИЕ БОТА")
    print("="*60)
    print(f"Текущие параметры:")
    print(f"  - TELEGRAM_BOT_TOKEN: {'установлен' if config.TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE' else 'НЕ установлен'}")
    print(f"  - LOG_LEVEL: {config.LOG_LEVEL}")
    print(f"  - MAX_RESULTS: {config.MAX_RESULTS}")
    
    if len(sys.argv) > 1:
        # Режим с аргументом командной строки
        query = " ".join(sys.argv[1:])
        await test_search(query)
    else:
        # Интерактивный режим
        print("\n📌 Выберите опцию:")
        print("  1. Интерактивный режим поиска")
        print("  2. Автоматический тест поиска")
        print("  3. Выход")
        
        choice = input("\nВведите номер опции (1-3): ").strip()
        
        if choice == "1":
            await interactive_mode()
        elif choice == "2":
            await search_test()
        else:
            print("До встречи!")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 Программа прервана пользователем")
    except Exception as e:
        print(f"\n❌ Ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
