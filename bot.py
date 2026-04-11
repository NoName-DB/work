"""
Основной файл Telegram бота для поиска дешёвых товаров
"""
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import Message
import logging

import config
from search import search_products, format_search_results
from logger import setup_logging

# Настройка логирования
setup_logging()
logger = logging.getLogger(__name__)

# Инициализация бота и диспетчера
bot = Bot(token=config.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start"""
    logger.info(f"User {message.from_user.id} started the bot")

    await message.answer(
        "🤖 <b>Добро пожаловать в бота поиска дешёвых товаров!</b>\n\n"
        "Я помогу вам найти самые дешёвые товары в интернет-магазинах Европы.\n\n"
        "📝 <b>Как пользоваться:</b>\n"
        "1. Введите название товара (например: iPhone 13, кроссовки Nike)\n"
        "2. Я поищу товар в Amazon, eBay и других магазинах\n"
        "3. Вы получите список с ценами, отсортированный от дешёвого к дорогому\n\n"
        "💡 <b>Доступные команды:</b>\n"
        "/help - справка\n"
        "/start - начать заново\n\n"
        "Введите название товара для поиска:",
        parse_mode="HTML",
    )


@dp.message(Command("help"))
async def cmd_help(message: Message) -> None:
    """Обработчик команды /help"""
    logger.info(f"User {message.from_user.id} requested help")

    await message.answer(
        "🆘 <b>Справка</b>\n\n"
        "Этот бот помогает найти самые дешёвые товары в интернете.\n\n"
        "📋 <b>Как работает бот:</b>\n"
        "• Вводите название товара (2+ символа)\n"
        "• Бот ищет товар в 3 крупных магазинах\n"
        "• Показывает топ-5 результатов, отсортированных по цене\n"
        "• Каждый результат содержит цену, название и ссылку\n\n"
        "⚡ <b>Быстрые команды:</b>\n"
        "/start - начать\n"
        "/help - эта справка\n\n"
        "💬 Просто напишите название товара!",
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

    # Отправляем сообщение о поиске
    processing_msg = await message.answer(
        "🔍 <b>Ищу товары...</b>\n\n"
        "Это может занять несколько секунд...",
        parse_mode="HTML",
    )

    try:
        # Ищем товары
        products = await search_products(query)

        # Форматируем результаты
        result_message = format_search_results(products)

        # Удаляем сообщение о поиске
        await bot.delete_message(chat_id=message.chat.id, message_id=processing_msg.message_id)

        # Отправляем результаты
        await message.answer(result_message, parse_mode="HTML", disable_web_page_preview=False)

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


async def main():
    """Главная функция - запуск бота"""
    logger.info("Starting bot...")

    try:
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

    # Запускаем бота
    asyncio.run(main())
