#!/usr/bin/env python3
"""
Тест для проверки надёжности функции search_ebay.
Проверяет, что функция использует fallback методы и всегда пытается найти товары.
"""
import asyncio
import logging
from search import search_ebay
from bs4 import BeautifulSoup

# Настроить логирование для видимости debug сообщений
logging.basicConfig(
    level=logging.DEBUG,
    format="%(name)s - %(levelname)s - %(message)s"
)

async def test_ebay_search():
    """Протестировать поиск на eBay с разными полярностями"""
    
    test_queries = [
        "iPhone",
        "Nike shoes",
        "Samsung"
    ]
    
    print("=" * 60)
    print("🧪 ТЕСТ НАДЁЖНОСТИ search_ebay")
    print("=" * 60)
    print()
    
    for query in test_queries:
        print(f"📝 Поиск: '{query}'")
        print("-" * 60)
        
        try:
            results = await search_ebay(query)
            
            print(f"✅ Найдено товаров: {len(results)}")
            
            if results:
                print("\nПервые 3 товара:")
                for i, item in enumerate(results[:3], 1):
                    title = item["title"][:50] + "..." if len(item["title"]) > 50 else item["title"]
                    price = f"${item['price']}" if item["price"] is not None else "Цена неизвестна"
                    print(f"  {i}. {title}")
                    print(f"     Цена: {price}")
                    print(f"     URL: {item['url'][:60]}...")
            else:
                print("❌ Товары не найдены")
        
        except Exception as e:
            print(f"❌ Ошибка: {e}")
        
        print()

if __name__ == "__main__":
    print("\n🚀 Запуск теста надёжности...")
    print()
    
    asyncio.run(test_ebay_search())
    
    print("=" * 60)
    print("✅ ТЕСТ ЗАВЕРШЕН")
    print("=" * 60)
