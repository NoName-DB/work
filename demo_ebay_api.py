#!/usr/bin/env python3
"""
Демо-скрипт для тестирования eBay Finding API.
Показывает как работает новая функция search_ebay_api().
"""
import asyncio
import logging
from search import search_ebay_api
import config

# Настроить логирование
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

async def demo_ebay_api():
    """Демонстрация работы eBay API"""

    print("=" * 70)
    print("🔌 ДЕМО: eBay Finding API Integration")
    print("=" * 70)
    print()

    # Проверка конфигурации
    if not config.EBAY_APP_ID or config.EBAY_APP_ID == "YOUR_EBAY_APP_ID_HERE":
        print("⚠️  eBay App ID не настроен!")
        print("   Добавьте EBAY_APP_ID=YOUR_APP_ID в файл .env")
        print("   Получить App ID: https://developer.ebay.com/")
        print()
        return

    print(f"✅ eBay App ID настроен: {config.EBAY_APP_ID[:8]}...")
    print()

    # Тестовые запросы
    test_queries = [
        "iPhone 13",
        "Nike Air Max",
        "Samsung Galaxy"
    ]

    for query in test_queries:
        print(f"🔍 Поиск: '{query}'")
        print("-" * 50)

        try:
            results = await search_ebay_api(query)

            if results:
                print(f"✅ Найдено товаров: {len(results)}")
                print()

                # Показать первые 3 товара
                for i, item in enumerate(results[:3], 1):
                    title = item["title"][:60] + "..." if len(item["title"]) > 60 else item["title"]
                    price = f"${item['price']:.2f}" if item["price"] else "Цена неизвестна"
                    currency = item.get("currency", "USD")

                    print(f"  {i}. {title}")
                    print(f"     💰 {price} {currency}")
                    print(f"     🔗 {item['url'][:50]}...")
                    print()

            else:
                print("❌ Товары не найдены")
                print("   Возможно, API вернул пустой результат или произошла ошибка")
                print()

        except Exception as e:
            print(f"❌ Ошибка: {e}")
            print()

        # Небольшая пауза между запросами
        await asyncio.sleep(1)

    print("=" * 70)
    print("🎯 ДЕМО ЗАВЕРШЕНО")
    print("=" * 70)
    print()
    print("💡 Советы:")
    print("   • eBay API имеет лимит 1000 запросов в день для бесплатного тарифа")
    print("   • Используйте разные запросы для тестирования")
    print("   • При ошибках проверьте логи для деталей")
    print("   • Для продакшена рассмотрите премиум тарифы")

if __name__ == "__main__":
    print("\n🚀 Запуск демо eBay API...")
    print()

    asyncio.run(demo_ebay_api())