"""
Примеры товаров и данные для тестирования бота
Используется, когда реальный парсинг недоступен
"""
from search import Product

# Примеры товаров для демонстрации
MOCK_PRODUCTS = {
    "iphone": [
        Product(
            name="Apple iPhone 13 128GB",
            price=699.99,
            currency="EUR",
            store="Amazon",
            url="https://www.amazon.eu/Apple-iPhone-13-128GB/dp/B09G8N8W5G",
        ),
        Product(
            name="Apple iPhone 13 128GB",
            price=749.00,
            currency="USD",
            store="eBay",
            url="https://www.ebay.com/itm/iPhone-13-128GB/123456789",
        ),
        Product(
            name="iPhone 13 Pro 256GB",
            price=899.99,
            currency="EUR",
            store="Amazon",
            url="https://www.amazon.eu/Apple-iPhone-13-Pro/dp/B09H8N8W5G",
        ),
    ],
    "nike": [
        Product(
            name="Nike Air Max 90",
            price=89.99,
            currency="EUR",
            store="Amazon",
            url="https://www.amazon.eu/Nike-Air-Max-90/dp/B09G8N8W5G",
        ),
        Product(
            name="Nike Air Max 90 Sneakers",
            price=79.99,
            currency="USD",
            store="eBay",
            url="https://www.ebay.com/itm/Nike-Air-Max-90/123456789",
        ),
        Product(
            name="Nike Air Jordan 1 Retro High",
            price=119.99,
            currency="EUR",
            store="Amazon",
            url="https://www.amazon.eu/Nike-Jordan-1-Retro-High/dp/B09H8N8W5G",
        ),
    ],
    "samsung": [
        Product(
            name="Samsung Galaxy S21 128GB",
            price=799.00,
            currency="EUR",
            store="Amazon",
            url="https://www.amazon.eu/Samsung-Galaxy-S21/dp/B09G8N8W5G",
        ),
        Product(
            name="Samsung Galaxy S21 5G",
            price=699.99,
            currency="USD",
            store="eBay",
            url="https://www.ebay.com/itm/Samsung-Galaxy-S21/123456789",
        ),
    ],
}


def get_mock_products(query: str) -> list:
    """Получить примеры товаров для тестирования"""
    query_lower = query.lower()
    
    for key, products in MOCK_PRODUCTS.items():
        if key in query_lower:
            # Возвращаем отсортированный список
            sorted_products = sorted(products, key=lambda p: p.price)
            return sorted_products[:5]
    
    return []
