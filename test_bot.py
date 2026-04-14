"""
Простые тесты для модулей бота
Запуск: python -m pytest test_bot.py -v
или просто: python test_bot.py
"""

import asyncio
import sys
from pathlib import Path

# Добавляем текущую папку в PATH для импорта модулей
sys.path.insert(0, str(Path(__file__).parent))

from search import Product, format_product_message, format_search_results, _extract_promotion_text
from examples import get_mock_products


def test_product_creation():
    """Тест создания товара"""
    product = Product(
        name="Test Product",
        price=99.99,
        currency="EUR",
        store="Amazon",
        url="https://example.com"
    )
    
    assert product.name == "Test Product"
    assert product.price == 99.99
    assert product.currency == "EUR"
    assert product.store == "Amazon"
    
    print("✅ test_product_creation - пройден")


def test_product_dict_conversion():
    """Тест конвертирования товара в dict"""
    product = Product(
        name="Test",
        price=50.0,
        currency="USD",
        store="eBay",
        url="https://example.com"
    )
    
    product_dict = product.to_dict()
    assert product_dict["name"] == "Test"
    assert product_dict["price"] == 50.0
    
    print("✅ test_product_dict_conversion - пройден")


def test_format_product_message():
    """Тест форматирования одного товара"""
    product = Product(
        name="iPhone 13",
        price=699.99,
        currency="EUR",
        store="Amazon",
        url="https://amazon.eu/iphone13"
    )
    
    message = format_product_message(product)
    assert "iPhone 13" in message
    assert "699.99" in message
    assert "EUR" in message
    assert "Amazon" in message
    
    print("✅ test_format_product_message - пройден")


def test_extract_promotion_text():
    """Тест извлечения текста акции и условий"""
    assert _extract_promotion_text("Nuolaida 20% perkant internetu") == "Скидка 20% (только онлайн)"
    assert _extract_promotion_text("PiguPlus akcija 15%") == "Скидка 15% (с PiguPlus)"
    assert _extract_promotion_text("Akcija sutaupykite 10 €") == "Скидка 10 €"
    assert _extract_promotion_text("PiguPlus") == "Цена с PiguPlus"

    print("✅ test_extract_promotion_text - пройден")


def test_format_empty_results():
    """Тест форматирования пустого списка"""
    message = format_search_results([])
    assert "не найден" in message.lower()
    
    print("✅ test_format_empty_results - пройден")


def test_format_multiple_results():
    """Тест форматирования списка товаров"""
    products = [
        Product("Product A", 50.0, "EUR", "Store1", "https://example1.com"),
        Product("Product B", 100.0, "EUR", "Store2", "https://example2.com"),
        Product("Product C", 75.0, "EUR", "Store3", "https://example3.com"),
    ]
    
    message = format_search_results(products)
    assert "Product A" in message
    assert "Product B" in message
    assert "Product C" in message
    assert "50.0" in message
    assert "100.0" in message
    
    print("✅ test_format_multiple_results - пройден")


def test_mock_products_iphone():
    """Тест примеров товаров - iPhone"""
    products = get_mock_products("iPhone")
    assert len(products) > 0
    assert all("iphone" in p.name.lower() or "apple" in p.name.lower() for p in products)
    
    print(f"✅ test_mock_products_iphone - пройден (найдено {len(products)} товаров)")


def test_mock_products_nike():
    """Тест примеров товаров - Nike"""
    products = get_mock_products("Nike")
    assert len(products) > 0
    
    print(f"✅ test_mock_products_nike - пройден (найдено {len(products)} товаров)")


def test_mock_products_samsung():
    """Тест примеров товаров - Samsung"""
    products = get_mock_products("Samsung")
    assert len(products) > 0
    
    print(f"✅ test_mock_products_samsung - пройден (найдено {len(products)} товаров)")


def test_mock_products_no_match():
    """Тест примеров товаров - неизвестный запрос"""
    products = get_mock_products("RandomUnknownProduct12345")
    assert len(products) == 0
    
    print("✅ test_mock_products_no_match - пройден")


def test_products_sorting():
    """Тест сортировки товаров по цене"""
    products = [
        Product("Product C", 100.0, "EUR", "Store1", "https://example.com"),
        Product("Product A", 50.0, "EUR", "Store2", "https://example.com"),
        Product("Product B", 75.0, "EUR", "Store3", "https://example.com"),
    ]
    
    sorted_products = sorted(products, key=lambda p: p.price)
    
    assert sorted_products[0].price == 50.0
    assert sorted_products[1].price == 75.0
    assert sorted_products[2].price == 100.0
    
    print("✅ test_products_sorting - пройден")


async def test_search_ebay_invalid_query():
    """Тест поиска eBay с невалидным запросом"""
    from search import search_ebay_api

    results = await search_ebay_api("")
    assert isinstance(results, list)
    assert len(results) == 0

    print("✅ test_search_ebay_invalid_query - пройден")


async def test_search_products_invalid_query():
    """Тест поиска с невалидным запросом"""
    from search import search_products

    # Слишком короткий запрос
    products = await search_products("x", "LT")
    assert len(products) == 0

    # Пустой запрос
    products = await search_products("", "LT")
    assert len(products) == 0

    print("✅ test_search_products_invalid_query - пройден")


async def test_ebay_api_no_app_id():
    """Тест eBay API без настроенного App ID"""
    from search import search_ebay_api

    # Сохраняем оригинальный App ID
    import config
    original_app_id = config.EBAY_APP_ID

    try:
        # Устанавливаем невалидный App ID
        config.EBAY_APP_ID = "YOUR_EBAY_APP_ID_HERE"

        results = await search_ebay_api("test")
        assert isinstance(results, list)
        assert len(results) == 0  # Должен вернуть пустой список без App ID

        print("✅ test_ebay_api_no_app_id - пройден")
    finally:
        # Восстанавливаем оригинальный App ID
        config.EBAY_APP_ID = original_app_id


def run_all_tests():
    """Запустить все тесты"""
    print("=" * 50)
    print("🧪 Запуск тестов бота")
    print("=" * 50)
    print()

    # Синхронные тесты
    test_product_creation()
    test_product_dict_conversion()
    test_format_product_message()
    test_extract_promotion_text()
    test_format_empty_results()
    test_format_multiple_results()
    test_mock_products_iphone()
    test_mock_products_nike()
    test_mock_products_samsung()
    test_mock_products_no_match()
    test_products_sorting()
    
    print()
    print("=" * 50)
    print("🔄 Запуск асинхронных тестов")
    print("=" * 50)
    print()
    
    # Асинхронные тесты
    asyncio.run(test_search_ebay_invalid_query())
    asyncio.run(test_search_products_invalid_query())
    asyncio.run(test_ebay_api_no_app_id())
    
    print()
    print("=" * 50)
    print("✅ ВСЕ ТЕСТЫ ПРОЙДЕНЫ!")
    print("=" * 50)


if __name__ == "__main__":
    try:
        run_all_tests()
    except AssertionError as e:
        print(f"\n❌ Тест не пройден: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Ошибка при выполнении тестов: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
