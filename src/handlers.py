"""
Обработчики сообщений для Telegram бота.
Простые функции для обработки команд и текстовых сообщений.
"""

import logging
from aiogram import Router, Dispatcher, types
from aiogram.filters import Command

from llm_client import create_llm_client


# Создаем роутер для обработчиков
router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start - приветствие пользователя."""
    welcome_text = (
        "🤖 Добро пожаловать! Я консультант компании.\n\n"
        "Я помогу вам найти подходящие услуги нашей компании.\n"
        "Задайте мне вопрос или воспользуйтесь командой /help для справки."
    )
    
    logging.info(f"Пользователь {message.from_user.id} ({message.from_user.username}) запустил бота")
    await message.answer(welcome_text)


@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help - справка по командам."""
    help_text = (
        "📋 Доступные команды:\n\n"
        "/start - начало работы с ботом\n"
        "/help - показать эту справку\n\n"
        "Просто напишите мне сообщение, и я отвечу на ваш вопрос!"
    )
    
    logging.info(f"Пользователь {message.from_user.id} запросил справку")
    await message.answer(help_text)


@router.message()
async def llm_handler(message: types.Message):
    """Обработчик текстовых сообщений - отправляет запрос к LLM."""
    user_text = message.text or "сообщение без текста"
    user_name = message.from_user.first_name or "клиент"
    
    logging.info(f"Получено сообщение от {message.from_user.id} ({user_name}): {user_text}")
    
    # Показываем что бот "печатает"
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    # Создаем LLM клиент и получаем ответ
    llm_client = create_llm_client()
    response_text = await llm_client.get_response(user_text, message.from_user.id, user_name)
    
    await message.answer(response_text)


def setup_handlers(dp: Dispatcher) -> None:
    """Настройка всех обработчиков для диспетчера."""
    dp.include_router(router)
    logging.info("Обработчики сообщений настроены")