"""
Модуль для поиска товаров в интернет-магазинах
"""
import logging
import re
import asyncio
import aiohttp
import cloudscraper
from typing import Any, Dict, List, Optional
from urllib.parse import quote_plus
from bs4 import BeautifulSoup
import config

logger = logging.getLogger(__name__)


def _parse_price(price_text: str) -> float:
    """Привести текст цены к числу с плавающей точкой."""
    if not price_text:
        return 0.0

    clean = price_text.replace("\xa0", " ").replace("\u202f", " ").strip()
    clean = re.sub(r"[^0-9,\.]+", "", clean)

    if clean.count(",") > 0 and clean.count(".") > 0:
        if clean.rfind(",") > clean.rfind("."):
            clean = clean.replace(".", "").replace(",", ".")
        else:
            clean = clean.replace(",", "")
    elif clean.count(",") > 0:
        clean = clean.replace(",", ".")

    try:
        return float(clean)
    except ValueError:
        return 0.0


def _parse_currency(price_text: str) -> str:
    """Определить валюту из текста цены."""
    text = price_text.upper()
    if "EUR" in text or "€" in text:
        return "EUR"
    if "GBP" in text or "£" in text:
        return "GBP"
    return "USD"


class Product:
    """Класс для представления товара"""

    def __init__(
        self,
        name: str,
        price: float,
        currency: str,
        store: str,
        url: str,
        image_url: Optional[str] = None,
    ):
        self.name = name
        self.price = price
        self.currency = currency
        self.store = store
        self.url = url
        self.image_url = image_url

    def __repr__(self):
        return f"Product(name={self.name}, price={self.price} {self.currency}, store={self.store})"

    def to_dict(self):
        return {
            "name": self.name,
            "price": self.price,
            "currency": self.currency,
            "store": self.store,
            "url": self.url,
            "image_url": self.image_url,
        }


def _is_valid_pigu_url(url: str) -> bool:
    """Проверить, является ли ссылка на Pigu реальным товаром."""
    if not url:
        return False

    url_lower = url.lower()
    return (
        "id=" in url_lower
        and "/lt/" in url_lower
        and "search" not in url_lower
        and "sq?" not in url_lower
    )


def _normalize_pigu_url(url: str) -> str:
    """Нормализовать относительный URL Pigu в абсолютный."""
    url = url.strip()
    if url.startswith("http"):
        return url
    if url.startswith("/"):
        return f"https://pigu.lt{url}"
    return f"https://pigu.lt/{url}"


def _extract_price_from_text(text: str) -> tuple[Optional[float], str]:
    """Извлечь цену и валюту из текста."""
    if not text:
        return None, "EUR"

    text = text.replace("\xa0", " ").replace("\u202f", " ")
    price_match = re.search(r"(\d+[\d\.,]*)", text)
    if not price_match:
        return None, "EUR"

    price = _parse_price(price_match.group(1))
    currency = _parse_currency(text)
    return (price if price and price > 0 else None, currency)


def _find_pigu_price(link_element) -> tuple[Optional[float], str]:
    """Поиск цены в контексте ссылки на Pigu."""
    candidates = [link_element, link_element.parent, link_element.parent.parent]
    for candidate in candidates:
        if candidate is None:
            continue
        text = candidate.get_text(" ", strip=True)
        price, currency = _extract_price_from_text(text)
        if price is not None:
            return price, currency

    next_elem = link_element.find_next(string=True)
    if next_elem:
        price, currency = _extract_price_from_text(next_elem)
        if price is not None:
            return price, currency

    for sibling in link_element.find_next_siblings():
        text = sibling.get_text(" ", strip=True)
        price, currency = _extract_price_from_text(text)
        if price is not None:
            return price, currency

    return None, "EUR"


def _search_pigu_sync(query: str) -> List[Product]:
    """Синхронный helper для поиска на Pigu через cloudscraper."""
    search_query = quote_plus(query)
    url = f"https://pigu.lt/lt/search?q={search_query}"
    scraper = cloudscraper.create_scraper(browser={"custom": config.USER_AGENTS[0]})
    response = scraper.get(url, timeout=config.SEARCH_TIMEOUT)
    if response.status_code != 200:
        logger.warning(f"Pigu request failed with status {response.status_code} for query: {query}")
        return []

    soup = BeautifulSoup(response.text, "html.parser")
    links = soup.find_all("a", href=True)

    products: List[Product] = []
    seen_urls = set()
    tokens = [token.lower() for token in re.findall(r"\w+", query)]

    for link in links:
        href = link.get("href", "").strip()
        if not _is_valid_pigu_url(href):
            continue

        product_url = _normalize_pigu_url(href)
        if product_url in seen_urls:
            continue

        title = link.get_text(" ", strip=True)
        if not title or len(title) < 3:
            continue

        if tokens and not all(token in title.lower() for token in tokens):
            continue

        price, currency = _find_pigu_price(link)
        if price is None:
            # Если цена не найдена, добавляем товар с неизвестной ценой
            price = 999999
            currency = "EUR"

        products.append(
            Product(
                name=title,
                price=price,
                currency=currency,
                store="Pigu.lt",
                url=product_url,
            )
        )
        seen_urls.add(product_url)

        if len(products) >= config.MAX_RESULTS:
            break

    logger.info(f"Found {len(products)} products on Pigu.lt for query: {query}")
    return products


async def search_pigu(query: str, session: Optional[aiohttp.ClientSession] = None) -> List[Product]:
    """Поиск товаров на Pigu.lt с использованием cloudscraper."""
    try:
        return await asyncio.to_thread(_search_pigu_sync, query)
    except Exception as e:
        logger.error(f"Error searching Pigu.lt: {e}")
        return []


async def search_ebay_api(query: str) -> List[Dict[str, Any]]:
    """Поиск товаров на eBay через официальный Finding API."""
    if not query or not query.strip():
        return []

    if not config.EBAY_APP_ID or config.EBAY_APP_ID == "YOUR_EBAY_APP_ID_HERE":
        logger.warning("eBay App ID not configured")
        return []

    params = {
        "OPERATION-NAME": "findItemsByKeywords",
        "SERVICE-VERSION": "1.0.0",
        "SECURITY-APPNAME": config.EBAY_APP_ID,
        "RESPONSE-DATA-FORMAT": "JSON",
        "keywords": query,
        "paginationInput.entriesPerPage": config.MAX_RESULTS,
        "GLOBAL-ID": "EBAY-US",
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(config.EBAY_API_URL, params=params, timeout=config.SEARCH_TIMEOUT) as response:
                if response.status != 200:
                    logger.warning(f"eBay API request failed with status {response.status}")
                    return []

                data = await response.json()

        if not data:
            return []

        if "errorMessage" in data:
            error = data["errorMessage"][0]["error"][0]
            logger.error(f"eBay API error: {error.get('message', 'unknown')}")
            return []

        response_items = data.get("findItemsByKeywordsResponse", [])
        if not response_items:
            return []

        search_results = response_items[0].get("searchResult", [])
        if not search_results:
            return []

        items = search_results[0].get("item", [])
        if not items:
            return []

        results: List[Dict[str, Any]] = []
        for item in items:
            try:
                title = item.get("title", [""])[0]
                selling_status = item.get("sellingStatus", [{}])[0]
                current_price = selling_status.get("currentPrice", [{}])[0]
                price = float(current_price.get("__value__", 0.0))
                currency = current_price.get("@currencyId", "USD")
                url = item.get("viewItemURL", [""])[0]

                if not title or not url:
                    continue

                results.append(
                    {
                        "title": title,
                        "price": price,
                        "url": url,
                        "source": "eBay",
                        "currency": currency,
                    }
                )
            except Exception as e:
                logger.debug(f"Error parsing eBay API item: {e}")
                continue

        logger.info(f"Found {len(results)} products via eBay API for query: {query}")
        return results

    except asyncio.TimeoutError:
        logger.warning(f"eBay API timeout for query: {query}")
        return []
    except Exception as e:
        logger.error(f"Error searching eBay API: {e}")
        return []


async def search_amazon(query: str, session: aiohttp.ClientSession) -> List[Product]:
    """Поиск товаров на Amazon.eu"""
    try:
        url = f"https://www.amazon.eu/s?k={quote_plus(query)}"
        headers = {"User-Agent": config.USER_AGENTS[0]}

        async with session.get(url, headers=headers, timeout=config.SEARCH_TIMEOUT) as response:
            if response.status != 200:
                logger.warning(f"Amazon request failed with status {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            products = []
            items = soup.find_all(
                "div", {"data-component-type": "s-search-result"}
            )[:config.MAX_RESULTS]

            for item in items:
                try:
                    name_elem = item.find("span", {"class": "a-size-base-plus"})
                    price_elem = item.find("span", {"class": "a-price-whole"})
                    url_elem = item.find("h2", {"class": "s-size-mini"}).find("a")

                    if name_elem and price_elem and url_elem:
                        name = name_elem.text.strip()
                        price_str = price_elem.text.strip().replace("€", "").replace(",", ".").strip()
                        try:
                            price = float(price_str.split()[0])
                        except (ValueError, IndexError):
                            price = 0.0

                        product_url = "https://www.amazon.eu" + url_elem.get("href", "")

                        product = Product(
                            name=name,
                            price=price,
                            currency="EUR",
                            store="Amazon",
                            url=product_url,
                        )
                        products.append(product)
                except Exception as e:
                    logger.debug(f"Error parsing Amazon product: {e}")
                    continue

            logger.info(f"Found {len(products)} products on Amazon for query: {query}")
            return products

    except asyncio.TimeoutError:
        logger.warning(f"Amazon search timeout for query: {query}")
        return []
    except Exception as e:
        logger.error(f"Error searching Amazon: {e}")
        return []


async def search_ebay(query: str) -> List[Dict[str, Any]]:
    """
    Поиск товаров на eBay. Возвращает список словарей с результатами.
    Использует множественные fallback методы для гарантированного поиска.
    """
    if not query or not query.strip():
        return []

    search_query = quote_plus(query)
    
    # Попробовать сначала .com, затем .co.uk
    urls = [
        f"https://www.ebay.com/sch/i.html?_nkw={search_query}",
        f"https://www.ebay.co.uk/sch/i.html?_nkw={search_query}"
    ]
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
        "Accept-Encoding": "gzip, deflate, br",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": "document",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-User": "?1",
        "Cache-Control": "max-age=0",
    }

    for url in urls:
        try:
            await asyncio.sleep(0.2)
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=headers, timeout=config.SEARCH_TIMEOUT) as response:
                    if response.status != 200:
                        logger.warning(f"eBay request failed with status {response.status} for {url}")
                        continue

                    html = await response.text()

            # Проверка на блокировку
            if "Pardon Our Interruption" in html or "captcha" in html.lower():
                logger.warning(f"eBay search page blocked or captcha for query: {query} on {url}")
                continue

            soup = BeautifulSoup(html, "html.parser")
            
            # МЕТОД 1: Основной селектор
            results = _parse_ebay_items(soup, query)
            if results:
                logger.info(f"Found {len(results)} products (method 1: li.s-item) on eBay for query: {query}")
                return results
            
            # МЕТОД 2: Альтернативный селектор 1
            logger.debug(f"Method 1 failed, trying method 2...")
            results = _parse_ebay_items_alt1(soup, query)
            if results:
                logger.info(f"Found {len(results)} products (method 2: div.s-item__wrapper) on eBay for query: {query}")
                return results
            
            # МЕТОД 3: Альтернативный селектор 2
            logger.debug(f"Method 2 failed, trying method 3...")
            results = _parse_ebay_items_alt2(soup, query)
            if results:
                logger.info(f"Found {len(results)} products (method 3: div.s-item) on eBay for query: {query}")
                return results
            
            # МЕТОД 4: Простой fallback - сырые ссылки
            logger.debug(f"Method 3 failed, using raw fallback...")
            results = _parse_ebay_fallback(soup, query)
            if results:
                logger.warning(f"Found {len(results)} products using raw fallback for query: {query}")
                return results
            
            logger.warning(f"No results found on {url}. HTML preview: {html[:500]}")

        except asyncio.TimeoutError:
            logger.warning(f"eBay search timeout for query: {query} on {url}")
            continue
        except Exception as e:
            logger.error(f"Error searching eBay on {url}: {e}")
            continue

    # Если ничего не найдено ни на одном сайте
    logger.error(f"No eBay results found for query: {query} on any site using any method")
    return []


def _extract_title_from_item(item) -> Optional[str]:
    """Извлечь название товара из элемента (с fallback селекторами)."""
    # Основной селектор
    title_elem = item.select_one("h3.s-item__title")
    if title_elem:
        return title_elem.text.strip()
    
    # Fallback 1: любой h3
    title_elem = item.find("h3")
    if title_elem:
        return title_elem.text.strip()
    
    # Fallback 2: любой span с текстом
    spans = item.find_all("span")
    for span in spans:
        text = span.text.strip()
        if len(text) > 10:  # Достаточно длинный текст вероятно是названием
            return text
    
    return None


def _extract_price_from_item(item) -> tuple[Optional[float], Optional[str]]:
    """Извлечь цену и валюту из элемента (с fallback селекторами)."""
    # Основной селектор
    price_elem = item.select_one("span.s-item__price")
    if price_elem:
        price_text = price_elem.text.strip()
        price = _parse_price(price_text)
        currency = _parse_currency(price_text)
        return price, currency
    
    # Fallback 1: любой span с символом цены
    spans = item.find_all("span")
    for span in spans:
        text = span.text.strip()
        if "$" in text or "€" in text or "£" in text:
            price = _parse_price(text)
            currency = _parse_currency(text)
            if price is not None and price != 0:
                return price, currency
    
    return None, None


def _extract_url_from_item(item) -> Optional[str]:
    """Извлечь URL товара из элемента."""
    url_elem = item.select_one("a.s-item__link")
    if url_elem:
        return url_elem.get("href", "").strip()
    
    # Fallback: первая ссылка в элементе
    url_elem = item.find("a")
    if url_elem:
        return url_elem.get("href", "").strip()
    
    return None


def _parse_ebay_items(soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
    """Основной парсинг: li.s-item"""
    items = soup.select("li.s-item")
    logger.debug(f"Method 1: Found {len(items)} items with li.s-item selector")
    
    results: List[Dict[str, Any]] = []
    
    for item in items:
        if len(results) >= config.MAX_RESULTS:
            break
        
        title = _extract_title_from_item(item)
        if not title or title.lower() == "new listing":
            continue
        
        price, currency = _extract_price_from_item(item)
        product_url = _extract_url_from_item(item)
        
        if not product_url:
            continue
        
        # Теперь цена может быть None
        results.append(
            {
                "title": title,
                "price": price if price else None,
                "url": product_url,
                "source": "eBay",
                "currency": currency if currency else "USD",
            }
        )
    
    return results


def _parse_ebay_items_alt1(soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
    """Альтернативный парсинг: div.s-item__wrapper"""
    items = soup.select("div.s-item__wrapper")
    logger.debug(f"Method 2: Found {len(items)} items with div.s-item__wrapper selector")
    
    results: List[Dict[str, Any]] = []
    
    for item in items:
        if len(results) >= config.MAX_RESULTS:
            break
        
        title = _extract_title_from_item(item)
        if not title or title.lower() == "new listing":
            continue
        
        price, currency = _extract_price_from_item(item)
        product_url = _extract_url_from_item(item)
        
        if not product_url:
            continue
        
        results.append(
            {
                "title": title,
                "price": price if price else None,
                "url": product_url,
                "source": "eBay",
                "currency": currency if currency else "USD",
            }
        )
    
    return results


def _parse_ebay_items_alt2(soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
    """Альтернативный парсинг: div.s-item"""
    items = soup.select("div.s-item")
    logger.debug(f"Method 3: Found {len(items)} items with div.s-item selector")
    
    results: List[Dict[str, Any]] = []
    
    for item in items:
        if len(results) >= config.MAX_RESULTS:
            break
        
        title = _extract_title_from_item(item)
        if not title or title.lower() == "new listing":
            continue
        
        price, currency = _extract_price_from_item(item)
        product_url = _extract_url_from_item(item)
        
        if not product_url:
            continue
        
        results.append(
            {
                "title": title,
                "price": price if price else None,
                "url": product_url,
                "source": "eBay",
                "currency": currency if currency else "USD",
            }
        )
    
    return results


def _parse_ebay_fallback(soup: BeautifulSoup, query: str) -> List[Dict[str, Any]]:
    """
    Простой fallback: если ничего не нашлось, просто возьми первые ссылки.
    Главное - не вернуть пустой список.
    """
    # Ищем все ссылки в основной области контента
    main_content = soup.find("main") or soup
    links = main_content.find_all("a", limit=20)

    logger.debug(f"Method 4 (fallback): Found {len(links)} links")
    
    results: List[Dict[str, Any]] = []
    
    for link in links:
        if len(results) >= config.MAX_RESULTS:
            break
        href = link.get("href", "").strip()
        text = link.text.strip()
        
        # Пропустить короткие тексты и ссылки без href
        if not href or len(text) < 5 or not text or "http" not in href:
            continue
        
        # Убедиться что это ссылка на товар (содержит /itm/ или похоже)
        if "/itm/" not in href and "/itm-" not in href:
            continue
        
        results.append(
            {
                "title": text,
                "price": None,
                "url": href,
                "source": "eBay",
                "currency": "USD",
            }
        )
    
    return results


async def search_aliexpress(query: str, session: aiohttp.ClientSession) -> List[Product]:
    """Поиск товаров на AliExpress"""
    try:
        url = f"https://www.aliexpress.com/wholesale?SearchText={quote_plus(query)}"
        headers = {"User-Agent": config.USER_AGENTS[2]}

        async with session.get(url, headers=headers, timeout=config.SEARCH_TIMEOUT) as response:
            if response.status != 200:
                logger.warning(f"AliExpress request failed with status {response.status}")
                return []

            html = await response.text()
            soup = BeautifulSoup(html, "html.parser")

            products = []
            # AliExpress использует JavaScript для загрузки товаров, поэтому парсинг сложен
            items = soup.find_all("div", {"class": "organic-item"})[:config.MAX_RESULTS]

            logger.info(f"Found {len(products)} products on AliExpress for query: {query}")
            return products  # Возвращаем пустой список, так как товары загружаются через JS

    except asyncio.TimeoutError:
        logger.warning(f"AliExpress search timeout for query: {query}")
        return []
    except Exception as e:
        logger.error(f"Error searching AliExpress: {e}")
        return []


async def search_products(query: str, locale: str = "LT") -> List[Product]:
    """
    Поиск товаров по нескольким источникам.
    Возвращает отсортированный список товаров по цене.
    """
    if not query or len(query.strip()) < 2:
        logger.warning(f"Invalid search query: {query}")
        return []

    logger.info(f"Starting search for query: {query}")
    all_products: List[Product] = []
    seen_urls = set()

    ebay_results = await search_ebay_api(query)
    if not ebay_results:
        ebay_results = await search_ebay(query)

    async with aiohttp.ClientSession() as session:
        tasks = [
            asyncio.create_task(search_pigu(query, session)),
            asyncio.create_task(search_amazon(query, session)),
            asyncio.create_task(search_aliexpress(query, session)),
        ]
        fetched = await asyncio.gather(*tasks, return_exceptions=True)

    for idx, result in enumerate(fetched):
        if isinstance(result, Exception):
            logger.error(f"Source {idx} raised an exception: {result}")
            continue
        for product in result:
            try:
                if not product.url or product.url in seen_urls:
                    continue
                if product.price is None or product.price <= 0:
                    product.price = 999999
                all_products.append(product)
                seen_urls.add(product.url)
            except Exception as e:
                logger.debug(f"Error processing aggregated product: {e}")
                continue

    for item in ebay_results:
        try:
            price = item["price"] if item["price"] is not None else 999999
            product = Product(
                name=item["title"],
                price=price,
                currency=item.get("currency", "USD"),
                store=item.get("source", "eBay"),
                url=item["url"],
            )
            if product.url and product.url not in seen_urls:
                all_products.append(product)
                seen_urls.add(product.url)
        except Exception as e:
            logger.debug(f"Error converting eBay result to Product: {e}")
            continue

    if not all_products:
        logger.warning(f"No products found for query: {query}")
        return []

    all_products.sort(key=lambda p: (p.price == 999999, p.price))
    top_products = all_products[: config.MAX_RESULTS]

    logger.info(f"Search completed. Found {len(top_products)} products")
    return top_products


def format_product_message(product: Product) -> str:
    """Форматирование товара для вывода в Telegram"""
    price_text = f"{product.price} {product.currency}" if product.price != 999999 else "Цена не указана"
    
    return (
        f"💰 <b>{product.name}</b>\n"
        f"💵 Цена: <b>{price_text}</b>\n"
        f"🏪 Магазин: {product.store}\n"
        f"🔗 <a href='{product.url}'>Перейти на товар</a>"
    )


def format_search_results(products: List[Product]) -> str:
    """Форматирование списка товаров для вывода в Telegram"""
    if not products:
        return "❌ Товар не найден. Попробуйте другой поисковый запрос."

    message = "✅ <b>Найденные товары (отсортированы по цене):</b>\n\n"

    for i, product in enumerate(products, 1):
        price_text = f"{product.price} {product.currency}" if product.price != 999999 else "Цена не указана"
        message += f"{i}. {product.name}\n"
        message += f"   💵 {price_text}\n"
        message += f"   🏪 {product.store}\n"
        message += f"   <a href='{product.url}'>Ссылка</a>\n\n"

    return message
