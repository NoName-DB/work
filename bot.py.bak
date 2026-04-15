"""
Основной файл Telegram бота для поиска дешёвых товаров
"""
import asyncio
from collections import deque
from typing import List, Optional
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message
import logging
import json
import os
from datetime import datetime
import aiohttp

import config
from search import search_products, format_search_results, Product, get_product_price
from logger import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()

search_history: dict[int, deque[str]] = {}
price_tracking: dict[str, dict] = {}  # user_id:product_id -> tracking info
last_search_results: dict[int, List[Product]] = {}  # user_id -> last search results

# Configuration files
HISTORY_FILE = getattr(config, 'HISTORY_FILE', 'search_history.json')
TRACKING_FILE = getattr(config, 'TRACKING_FILE', 'price_tracking.json')


def load_history():
    """Загрузить историю поиска из файла"""
    global search_history
    try:
        if os.path.exists(HISTORY_FILE):
            with open(HISTORY_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for user_id_str, queries in data.items():
                    user_id = int(user_id_str)
                    search_history[user_id] = deque(queries, maxlen=config.MAX_HISTORY)
    except Exception as e:
        logger.error(f"Error loading history: {e}")


def save_history():
    """Сохранить историю поиска в файл"""
    try:
        data = {str(user_id): list(queries) for user_id, queries in search_history.items()}
        with open(HISTORY_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving history: {e}")


def load_price_tracking():
    """Загрузить отслеживание цен из файла"""
    global price_tracking
    try:
        if os.path.exists(TRACKING_FILE):
            with open(TRACKING_FILE, 'r', encoding='utf-8') as f:
                price_tracking = json.load(f)
    except Exception as e:
        logger.error(f"Error loading price tracking: {e}")


def save_price_tracking():
    """Сохранить отслеживание цен в файл"""
    try:
        with open(TRACKING_FILE, 'w', encoding='utf-8') as f:
            json.dump(price_tracking, f, ensure_ascii=False, indent=2)
    except Exception as e:
        logger.error(f"Error saving price tracking: {e}")


def record_search_history(user_id: int, query: str) -> None:
    """Записать запрос в историю поиска"""
    history = search_history.setdefault(user_id, deque(maxlen=config.MAX_HISTORY))
    if not history or history[-1].lower() != query.lower():
        history.append(query)
    save_history()


def add_price_tracking(user_id: int, product_id: str, product: Product) -> None:
    """Добавить товар для отслеживания цены"""
    key = f"{user_id}:{product_id}"
    if key not in price_tracking:
        price_tracking[key] = {
            "user_id": user_id,
            "product_id": product_id,
            "name": product.name,
            "url": product.url,
            "store": product.store,
            "initial_price": product.price,
            "current_price": product.price,
            "currency": product.currency,
            "last_check": datetime.now().isoformat(),
            "added_at": datetime.now().isoformat(),
        }
        save_price_tracking()


def get_user_tracking(user_id: int) -> list:
    """Получить список отслеживаемых товаров пользователя"""
    return [info for key, info in price_tracking.items() if info["user_id"] == user_id]


def remove_price_tracking(user_id: int, tracking_key: str) -> bool:
    """Удалить товар из отслеживания"""
    key = f"{user_id}:{tracking_key}"
    if key in price_tracking:
        del price_tracking[key]
        save_price_tracking()
        return True
    return False


def get_popular_keyboard() -> InlineKeyboardMarkup:
    buttons = [InlineKeyboardButton(text=query, callback_data=f"quick_search:{query}") for query in config.POPULAR_SEARCHES]
    keyboard_rows = [buttons[i : i + 2] for i in range(0, len(buttons), 2)]
    return InlineKeyboardMarkup(inline_keyboard=keyboard_rows)


def record_search_history(user_id: int, query: str) -> None:
    history = search_history.setdefault(user_id, deque(maxlen=config.MAX_HISTORY))
    if not history or history[-1].lower() != query.lower():
        history.append(query)


def format_history(user_id: int) -> str:
    history = search_history.get(user_id, deque())
    if not history:
        return "ℹ️ У вас пока нет истории поисков. Напишите запрос и я сохраню его."
    message = "🕘 Ваша история поисков:\n\n"
    for i, query in enumerate(reversed(history), 1):
        message += f"{i}. {query}\n"
    return message


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start"""
    logger.info(f"User {message.from_user.id} started the bot")

    await message.answer(
        "🤖 <b>Добро пожаловать в бота поиска дешёвых товаров!</b>\n\n"
        "Я помогу вам найти товары в литовских интернет-магазинах.\n\n"
        "📝 <b>Как пользоваться:</b>\n"
        "1. Введите название товара на русском или литовском языке\n"
        "2. Я поищу товар на Pigu.lt и других популярных магазинах\n"
        "3. Вы получите список с ценами, названием и ссылкой\n\n"
        "💡 <b>Примеры запросов:</b>\n"
        "• iPhone 15 (техника)\n"
        "• Nike кроссовки (одежда и обувь)\n"
        "• Sony наушники (аудио)\n"
        "• Canon фотоаппарат (фото/видео)\n"
        "• IKEA стул (мебель)\n\n"
        "💡 <b>Доступные команды:</b>\n"
        "/help - справка\n"
        "/history - ваша история запросов\n"
        "/start - начать заново\n\n"
        "Нажмите кнопку ниже, чтобы быстро начать поиск:",
        parse_mode="HTML",
        reply_markup=get_popular_keyboard(),
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    logger.info(f"User {message.from_user.id} requested help")

    await message.answer(
        "🆘 <b>Справка</b>\n\n"
        "Этот бот помогает найти самые дешёвые товары в литовских интернет-магазинах.\n\n"
        "📋 <b>Как работает бот:</b>\n"
        "• Вводите название товара на русском или литовском языке (2+ символа)\n"
        "• Бот ищет товар на Pigu.lt и других магазинах\n"
        "• Показывает топ-5 результатов, отсортированных по цене\n"
        "• Каждый результат содержит цену, название и ссылку\n\n"
        "🛍️ <b>Категории товаров:</b>\n"
        "• Электроника и техника\n"
        "• Одежда и обувь\n"
        "• Дом и сад\n"
        "• Спорт и отдых\n"
        "• Книги и развлечения\n"
        "• И многое другое!\n\n"
        "⚡ <b>Быстрые команды:</b>\n"
        "/start - начать\n"
        "/history - ваша история поисков\n"
        "/help - эта справка\n\n"
        "💬 Просто напишите название товара или выберите кнопку ниже!",
        parse_mode="HTML",
        reply_markup=get_popular_keyboard(),
    )


@dp.message(Command("history"))
async def cmd_history(message: Message) -> None:
    """Обработчик команды /history"""
    logger.info(f"User {message.from_user.id} requested history")
    await message.answer(format_history(message.from_user.id), parse_mode="HTML")


@dp.message(Command("track"))
async def cmd_track(message: Message) -> None:
    """Обработчик команды /track - просмотр или добавление товара для отслеживания"""
    user_id = message.from_user.id
    args = message.text.split()[1:] if len(message.text.split()) > 1 else []
    
    # Если указан аргумент - добавить товар в отслеживание
    if args:
        try:
            item_index = int(args[0]) - 1  # 1-based to 0-based
            if user_id not in last_search_results or not last_search_results[user_id]:
                await message.answer(
                    "❌ Сначала выполните поиск, затем используйте /track <номер>",
                    parse_mode="HTML"
                )
                return
            
            products = last_search_results[user_id]
            if item_index < 0 or item_index >= len(products):
                await message.answer(
                    f"❌ Неверный номер. Доступны номера от 1 до {len(products)}.",
                    parse_mode="HTML"
                )
                return
            
            product = products[item_index]
            product_id = f"{product.store}_{product.name[:50].replace(' ', '_')}_{product.price}"
            
            add_price_tracking(user_id, product_id, product)
            await message.answer(
                f"✅ Товар добавлен в отслеживание:\n\n"
                f"📦 {product.name}\n"
                f"💰 {product.price} {product.currency}\n"
                f"🏪 {product.store}\n\n"
                f"Вы получите уведомление при изменении цены.",
                parse_mode="HTML"
            )
            logger.info(f"User {user_id} started tracking product: {product_id}")
            
        except ValueError:
            await message.answer(
                "❌ Используйте: /track <номер товара>\n\nСначала выполните поиск.",
                parse_mode="HTML"
            )
            return
    else:
        # Если без аргументов - показать список отслеживаемых товаров
        tracking = get_user_tracking(user_id)
        if not tracking:
            await message.answer(
                "📊 У вас нет отслеживаемых товаров.\n\n"
                "Используйте: /track <номер> для добавления товара из последнего поиска.",
                parse_mode="HTML"
            )
            return

        response = "📊 Ваши отслеживаемые товары:\n\n"
        for i, item in enumerate(tracking, 1):
            price_change = ""
            if item["current_price"] != item["initial_price"]:
                change_percent = ((item["current_price"] - item["initial_price"]) / item["initial_price"]) * 100
                price_change = f" ({change_percent:+.1f}%)"

            response += f"{i}. {item['name']}\n"
            response += f"   💰 {item['current_price']} {item['currency']}{price_change}\n"
            response += f"   🏪 {item['store']}\n"
            response += f"   🔗 <a href='{item['url']}'>Ссылка</a>\n\n"

        await message.answer(response, parse_mode="HTML")

    
    logger.info(f"User {user_id} started tracking product: {product_id}")


@dp.callback_query(lambda c: c.data and c.data.startswith("quick_search:"))
async def handle_quick_search(callback: CallbackQuery) -> None:
    query = callback.data.split("quick_search:", 1)[1]
    user_id = callback.from_user.id
    record_search_history(user_id, query)
    await callback.answer(f"Ищу {query}...")
    processing_msg = await callback.message.answer(
        "🔍 <b>Ищу товары...</b>\n\n"
        "Это может занять несколько секунд...",
        parse_mode="HTML",
    )

    try:
        products = await search_products(query, "LT")
        result_message = format_search_results(products)
        await callback.message.delete()
        await callback.message.answer(result_message, parse_mode="HTML", disable_web_page_preview=False)
        logger.info(f"User {user_id} received {len(products)} results from quick search")
    except Exception as e:
        logger.error(f"Error processing quick search request from user {user_id}: {e}")
        try:
            await callback.message.delete()
        except:
            pass
        await callback.message.answer(
            "❌ <b>Ошибка при поиске товаров</b>\n\n"
            "Попробуйте позже или измените поисковый запрос.",
            parse_mode="HTML",
        )


@dp.message()
async def handle_search(message: Message) -> None:
    """Обработчик текстовых сообщений (поиск товаров)"""
    query = message.text.strip()
    user_id = message.from_user.id

    logger.info(f"User {user_id} searching for: {query}")

    # Проверка валидности запроса
    if len(query) < 2:
        await message.answer(
            "❌ Пожалуйста, введите название товара (минимум 2 символа)",
            parse_mode="HTML",
        )
        return

    record_search_history(user_id, query)

    # Отправляем сообщение о поиске
    processing_msg = await message.answer(
        "🔍 <b>Ищу товары...</b>\n\n"
        "Это может занять несколько секунд...",
        parse_mode="HTML",
    )

    try:
        # Ищем товары
        products = await search_products(query, "LT")  # Литва

        # Форматируем результаты
        result_message = format_search_results(products)

        # Удаляем сообщение о поиске
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

        # Отправляем результаты
        await message.answer(result_message, parse_mode="HTML", disable_web_page_preview=False)

        # Сохраняем результаты для отслеживания
        last_search_results[user_id] = products

        logger.info(f"User {user_id} received {len(products)} results")

    except Exception as e:
        logger.error(f"Error processing search request from user {user_id}: {e}")

        # Удаляем сообщение о поиске
        try:
            await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)
        except:
            pass

        # Отправляем сообщение об ошибке
        await message.answer(
            "❌ <b>Ошибка при поиске товаров</b>\n\n"
            "Попробуйте позже или измените поисковый запрос.",
            parse_mode="HTML",
        )


async def check_price_changes():
    """Периодическая проверка изменения цен"""
    while True:
        try:
            logger.info("Checking price changes...")
            
            for key, tracking_info in list(price_tracking.items()):
                # Проверяем каждые 6 часов
                last_check = datetime.fromisoformat(tracking_info["last_check"])
                if (datetime.now() - last_check).total_seconds() < 6 * 3600:
                    continue
                
                # Получаем текущую цену через парсер
                try:
                    current_price = await get_product_price(
                        tracking_info["url"],
                        tracking_info["store"]
                    )
                    if current_price is None:
                        logger.warning(f"Could not fetch price for {tracking_info['url']}")
                        tracking_info["last_check"] = datetime.now().isoformat()
                        continue
                except Exception as e:
                    logger.error(f"Error fetching price for {tracking_info['url']}: {e}")
                    tracking_info["last_check"] = datetime.now().isoformat()
                    continue
                
                old_price = tracking_info["current_price"]
                tracking_info["last_check"] = datetime.now().isoformat()
                
                # Только отправляем уведомление если цена действительно изменилась
                if abs(current_price - old_price) > 0.01:  # Минимальное изменение
                    tracking_info["current_price"] = current_price
                    change_percent = ((current_price - old_price) / old_price) * 100 if old_price != 0 else 0
                    
                    message = (
                        f"💰 <b>Изменение цены!</b>\n\n"
                        f"📦 {tracking_info['name']}\n"
                        f"🏪 {tracking_info['store']}\n\n"
                        f"Старая цена: {old_price:.2f} {tracking_info['currency']}\n"
                        f"Новая цена: {current_price:.2f} {tracking_info['currency']}\n"
                        f"Изменение: {change_percent:+.1f}%\n\n"
                        f"🔗 <a href='{tracking_info['url']}'>Ссылка на товар</a>"
                    )
                    
                    try:
                        await bot.send_message(
                            chat_id=tracking_info["user_id"],
                            text=message,
                            parse_mode="HTML",
                            disable_web_page_preview=False
                        )
                        logger.info(f"Sent price change notification to user {tracking_info['user_id']}")
                    except Exception as e:
                        logger.error(f"Failed to send notification to user {tracking_info['user_id']}: {e}")
            
            save_price_tracking()
            
        except Exception as e:
            logger.error(f"Error in price check task: {e}")
        
        # Ждем 1 час перед следующей проверкой
        await asyncio.sleep(3600)


async def main():
    """Главная функция - запуск бота"""
    logger.info("Starting bot...")

    try:
        # Запускаем задачу проверки цен
        price_check_task = asyncio.create_task(check_price_changes())
        
        # Запускаем бота
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logger.info("Bot stopped")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    # Проверяем токен
    if config.TELEGRAM_BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        logger.error("ERROR: Please set TELEGRAM_BOT_TOKEN in .env file!")
        print("❌ ERROR: Please set TELEGRAM_BOT_TOKEN in .env file!")
        exit(1)

    # Загружаем сохраненные данные
    load_history()
    load_price_tracking()

    # Запускаем бота
    asyncio.run(main())
