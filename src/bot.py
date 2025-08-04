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


async def main():
    """Основная функция запуска бота."""
    # Настройка логирования
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Загружаем переменные окружения из .env файла (только для локальной разработки)
    # В продакшене (Railway/Docker) переменные уже установлены в системе
    if not os.getenv('RAILWAY_ENVIRONMENT'):  # Railway устанавливает эту переменную
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        env_path = os.path.join(project_root, '.env')
        load_dotenv(env_path)
        logging.info("Загружены переменные окружения из .env файла")
    else:
        logging.info("Обнаружена среда Railway, используем системные переменные окружения")
    
    # Проверяем наличие токена
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    openrouter_key = os.getenv('OPENROUTER_API_KEY')
    
    # Диагностика переменных окружения
    logging.info(f"TELEGRAM_BOT_TOKEN найден: {'Да' if bot_token else 'Нет'}")
    logging.info(f"OPENROUTER_API_KEY найден: {'Да' if openrouter_key else 'Нет'}")
    
    if not bot_token:
        logging.error("TELEGRAM_BOT_TOKEN не найден в переменных окружения")
        logging.error("Убедитесь что в Railway в разделе Variables добавлена переменная TELEGRAM_BOT_TOKEN")
        sys.exit(1)
        
    if not openrouter_key:
        logging.warning("OPENROUTER_API_KEY не найден - LLM функционал не будет работать")
    
    logging.info("LLM Consultant Bot starting...")
    
    # Создаем бота и диспетчер
    bot = Bot(token=bot_token)
    dp = Dispatcher()
    
    # Настраиваем обработчики
    setup_handlers(dp)
    
    try:
        logging.info("Бот запущен и готов к работе")
        await dp.start_polling(bot)
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())