"""
Обработчики сообщений для Telegram бота.
Простые функции для обработки команд и текстовых сообщений.
"""

import logging
import time
from aiogram import Router, Dispatcher, types
from aiogram.filters import Command

from llm_client import create_llm_client
from logger import log_conversation
from config import load_prompts
from conversation_memory import conversation_memory


# Создаем роутер для обработчиков
router = Router()


@router.message(Command("start"))
async def start_handler(message: types.Message):
    """Обработчик команды /start - приветствие пользователя."""
    try:
        prompts = load_prompts()
        welcome_text = prompts.get('welcome_message', 'Добро пожаловать!')
        
        logging.info(f"Пользователь {message.from_user.id} ({message.from_user.username}) запустил бота")
        await message.answer(welcome_text)
    except Exception as e:
        logging.error(f"Ошибка в обработчике /start: {e}")
        await message.answer("Добро пожаловать! Я консультант компании. Напишите ваш вопрос.")


@router.message(Command("help"))
async def help_handler(message: types.Message):
    """Обработчик команды /help - справка по командам."""
    try:
        prompts = load_prompts()
        help_text = prompts.get('help_message', 'Справка временно недоступна.')
        
        logging.info(f"Пользователь {message.from_user.id} запросил справку")
        await message.answer(help_text)
    except Exception as e:
        logging.error(f"Ошибка в обработчике /help: {e}")
        await message.answer("Доступные команды:\n/start - начало работы\n/help - справка\n/contact - контакты")


@router.message(Command("contact"))
async def contact_handler(message: types.Message):
    """Обработчик команды /contact - контактная информация."""
    try:
        prompts = load_prompts()
        contact_text = prompts.get('contact_message', 'Контактная информация временно недоступна.')
        
        logging.info(f"Пользователь {message.from_user.id} запросил контакты")
        await message.answer(contact_text)
    except Exception as e:
        logging.error(f"Ошибка в обработчике /contact: {e}")
        await message.answer("Для связи с нами обратитесь к менеджеру.")


@router.message(Command("clear"))
async def clear_handler(message: types.Message):
    """Обработчик команды /clear - очистка истории диалога."""
    try:
        user_id = message.from_user.id
        conversation_memory.clear_history(user_id)
        
        logging.info(f"Пользователь {user_id} очистил историю диалога")
        await message.answer("✅ История диалога очищена. Я забыл все наши предыдущие сообщения.")
    except Exception as e:
        logging.error(f"Ошибка в обработчике /clear: {e}")
        await message.answer("Произошла ошибка при очистке истории.")


@router.message(Command("memory"))
async def memory_handler(message: types.Message):
    """Обработчик команды /memory - показать состояние памяти диалога."""
    try:
        user_id = message.from_user.id
        history = conversation_memory.get_history(user_id, 20)  # Показываем больше для отладки
        
        if not history:
            await message.answer("📝 История диалога пуста.")
            return
        
        # Формируем сообщение с историей
        memory_text = f"📝 История диалога ({len(history)} сообщений):\n\n"
        
        for i, msg in enumerate(history[-10:], 1):  # Показываем последние 10
            role_icon = "👤" if msg["role"] == "user" else "🤖"
            content = msg["content"][:100] + "..." if len(msg["content"]) > 100 else msg["content"]
            memory_text += f"{i}. {role_icon} {content}\n\n"
        
        if len(history) > 10:
            memory_text += f"... и еще {len(history) - 10} сообщений\n\n"
        
        memory_text += "Используйте /clear для очистки истории."
        
        logging.info(f"Пользователь {user_id} запросил состояние памяти")
        await message.answer(memory_text)
    except Exception as e:
        logging.error(f"Ошибка в обработчике /memory: {e}")
        await message.answer("Произошла ошибка при получении истории.")


@router.message()
async def llm_handler(message: types.Message):
    """Обработчик текстовых сообщений - отправляет запрос к LLM."""
    start_time = time.time()
    
    user_text = message.text or "сообщение без текста"
    user_name = message.from_user.first_name or "клиент"
    user_id = message.from_user.id
    username = message.from_user.username
    
    logging.info(f"Получено сообщение от {user_id} ({user_name}): {user_text}")
    
    # Показываем что бот "печатает"
    await message.bot.send_chat_action(message.chat.id, "typing")
    
    try:
        # Создаем LLM клиент и получаем ответ
        llm_client = create_llm_client()
        response_text = await llm_client.get_response(user_text, user_id, user_name)
        
        # Отправляем ответ
        await message.answer(response_text)
        
        # Вычисляем время ответа
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Логируем диалог
        log_conversation(
            user_id=user_id,
            username=username,
            user_message=user_text,
            bot_response=response_text,
            response_time_ms=response_time_ms
        )
        
        logging.info(f"Ответ отправлен пользователю {user_id}, время: {response_time_ms}ms")
        
    except Exception as e:
        prompts = load_prompts()
        error_message = prompts.get('error_message', 'Извините, произошла ошибка. Попробуйте позже.')
        await message.answer(error_message)
        
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # Логируем диалог с ошибкой
        log_conversation(
            user_id=user_id,
            username=username,
            user_message=user_text,
            bot_response=error_message,
            response_time_ms=response_time_ms
        )
        
        logging.error(f"Ошибка при обработке сообщения от {user_id}: {e}")


def setup_handlers(dp: Dispatcher) -> None:
    """Настройка всех обработчиков для диспетчера."""
    dp.include_router(router)
    logging.info("Обработчики сообщений настроены")