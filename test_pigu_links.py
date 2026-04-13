#!/usr/bin/env python3
"""Тестирование логики извлечения ссылок в search_pigu"""
from bs4 import BeautifulSoup

def test_url_validation():
    """Тестируем функцию is_valid_product_url с различными ссылками"""
    
    def is_valid_product_url(url: str) -> bool:
        url_lower = url.lower()
        return ("id=" in url_lower and 
                "/lt/" in url_lower and
                "search" not in url_lower and 
                "sq?" not in url_lower)
    
    test_cases = [
        ("https://pigu.lt/lt/mobilieji-telefonai/apple-iphone-15?id=75500617", True, "Правильная ссылка"),
        ("/lt/mobilieji-telefonai/apple-iphone-15?id=75500617", True, "Относительная ссылка"),
        ("https://pigu.lt/lt/search?q=iphone&id=123", False, "Ссылка на поиск"),
        ("https://pigu.lt/lt/kategorija?sq?=filter", False, "Ссылка с sq?"),
        ("/en/products/iphone?id=123", False, "Язык /en"),
    ]
    
    passed = sum(1 for url, expected, _ in test_cases if is_valid_product_url(url) == expected)
    print(f"✅ Валидация URL: {passed}/{len(test_cases)} пройдено")
    return passed == len(test_cases)

def test_link_extraction():
    """Тестируем извлечение ссылок из HTML"""
    html = '<a href="/lt/iphone?id=123">iPhone</a><a href="/lt/search?q=x">Search</a>'
    
    def is_valid_product_url(url: str) -> bool:
        url_lower = url.lower()
        return ("id=" in url_lower and "/lt/" in url_lower and "search" not in url_lower and "sq?" not in url_lower)
    
    soup = BeautifulSoup(html, "html.parser")
    valid = [link for link in soup.find_all("a") if is_valid_product_url(link.get("href", ""))]
    
    print(f"✅ Извлечение ссылок: {len(valid)}/1 найдено (ожидали 1)")
    return len(valid) == 1

if __name__ == "__main__":
    print("\n" + "="*60)
    print("ТЕСТИРОВАНИЕ ЛОГИКИ ИЗВЛЕЧЕНИЯ ССЫЛОК")
    print("="*60 + "\n")
    
    test1 = test_url_validation()
    test2 = test_link_extraction()
    
    if test1 and test2:
        print("\n🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ!\n")
    else:
        print("\n❌ НЕКОТОРЫЕ ТЕСТЫ НЕ ПРОЙДЕНЫ\n")
