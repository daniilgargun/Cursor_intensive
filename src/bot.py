#!/usr/bin/env python3
"""
Основной файл LLM-ассистента для первичной консультации клиентов.
Точка входа в приложение.
"""

import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers import setup_handlers
from logger import setup_logging


async def main():
    """Основная функция запуска бота."""
    # Настройка логирования в файлы
    setup_logging()
    
    # Загружаем переменные окружения из корня проекта
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    env_path = os.path.join(project_root, '.env')
    load_dotenv(env_path)
    
    # Проверяем наличие токена
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logging.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        sys.exit(1)
    
    logging.info("LLM Consultant Bot starting...")
    
    # Создаем бота и диспетчер
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    # Настраиваем обработчики
    setup_handlers(dp)
    
    try:
        logging.info("Бот запущен и готов к работе")
        await dp.start_polling(bot)
    except KeyboardInterrupt:
        logging.info("Получен сигнал остановки")
    except Exception as e:
        logging.error(f"Критическая ошибка при работе бота: {e}")
        raise
    finally:
        try:
            await bot.session.close()
            logging.info("Бот остановлен")
        except Exception as e:
            logging.error(f"Ошибка при закрытии сессии бота: {e}")


if __name__ == "__main__":
    asyncio.run(main())