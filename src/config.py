"""
Загрузка конфигурации из YAML файлов.
Простая загрузка без валидации согласно convention.md.
"""

import yaml
import os
import logging
from typing import Dict, Any


def get_project_root() -> str:
    """Получить путь к корню проекта."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config() -> Dict[str, Any]:
    """
    Загрузить основные настройки из config/settings.yaml.
    
    Returns:
        Словарь с настройками бота и LLM
    """
    project_root = get_project_root()
    settings_path = os.path.join(project_root, 'config', 'settings.yaml')
    
    try:
        with open(settings_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        logging.info(f"Конфигурация загружена из {settings_path}")
        return config
    except FileNotFoundError:
        logging.error(f"Файл конфигурации не найден: {settings_path}")
        # Возвращаем базовую конфигурацию по умолчанию
        return {
            'bot': {
                'name': 'LLM Consultant',
                'description': 'Консультант по услугам компании'
            },
            'llm': {
                'model': 'google/gemini-2.0-flash-exp:free',
                'max_tokens': 1000,
                'temperature': 0.7
            },
            'logging': {
                'level': 'INFO',
                'format': 'json'
            }
        }
    except Exception as e:
        logging.error(f"Ошибка при загрузке конфигурации: {e}")
        # Не поднимаем исключение, возвращаем базовую конфигурацию
        return {
            'bot': {
                'name': 'LLM Consultant',
                'description': 'Консультант по услугам компании'
            },
            'llm': {
                'model': 'google/gemini-2.0-flash-exp:free',
                'max_tokens': 1000,
                'temperature': 0.7,
                'timeout_seconds': 30,
                'max_retries': 2,
                'retry_delay_seconds': 1
            },
            'logging': {
                'level': 'INFO',
                'format': 'json'
            }
        }


def load_prompts() -> Dict[str, str]:
    """
    Загрузить промпты из config/prompts.yaml.
    
    Returns:
        Словарь с промптами для LLM
    """
    project_root = get_project_root()
    prompts_path = os.path.join(project_root, 'config', 'prompts.yaml')
    
    try:
        with open(prompts_path, 'r', encoding='utf-8') as f:
            prompts = yaml.safe_load(f)
        logging.info(f"Промпты загружены из {prompts_path}")
        return prompts
    except FileNotFoundError:
        logging.error(f"Файл промптов не найден: {prompts_path}")
        # Возвращаем базовые промпты по умолчанию
        return {
            'system_prompt': """Ты - консультант компании по оказанию услуг.

Твоя задача:
- Выявить потребности клиента
- Задать уточняющие вопросы для понимания проблем
- Предложить подходящие услуги компании
- Быть дружелюбным и профессиональным

Отвечай кратко и по делу. Если клиент задает общий вопрос, уточни детали.
Если не знаешь конкретных услуг компании, предложи связаться с менеджером.""",
            'welcome_message': """🤖 Добро пожаловать! Я консультант компании.

Я помогу вам найти подходящие услуги нашей компании.
Задайте мне вопрос или воспользуйтесь командой /help для справки.""",
            'help_message': """📋 Доступные команды:

/start - начало работы с ботом
/help - показать эту справку

Просто напишите мне сообщение, и я отвечу на ваш вопрос!"""
        }
    except Exception as e:
        logging.error(f"Ошибка при загрузке промптов: {e}")
        # Не поднимаем исключение, возвращаем базовые промпты
        return {
            'system_prompt': """Ты - консультант компании по оказанию услуг.

Твоя задача:
- Выявить потребности клиента
- Задать уточняющие вопросы для понимания проблем
- Предложить подходящие услуги компании
- Быть дружелюбным и профессиональным

Отвечай кратко и по делу. Если клиент задает общий вопрос, уточни детали.
Если не знаешь конкретных услуг компании, предложи связаться с менеджером.""",
            'welcome_message': """🤖 Добро пожаловать! Я консультант компании.

Я помогу вам найти подходящие услуги нашей компании.
Задайте мне вопрос или воспользуйтесь командой /help для справки.""",
            'help_message': """📋 Доступные команды:

/start - начало работы с ботом
/help - показать эту справку
/contact - контактная информация

Просто напишите мне сообщение, и я отвечу на ваш вопрос!""",
            'contact_message': """📞 Контактная информация:

🏢 Наша компания предоставляет профессиональные услуги
📧 Для связи обратитесь к менеджеру""",
            'error_message': """😔 Извините, произошла ошибка при обработке вашего запроса.

Попробуйте:
• Переформулировать вопрос
• Повторить запрос через несколько минут
• Обратиться к нашему менеджеру

Мы работаем над решением проблемы!"""
        }


def get_bot_config() -> Dict[str, Any]:
    """Получить конфигурацию бота."""
    config = load_config()
    return config.get('bot', {})


def get_llm_config() -> Dict[str, Any]:
    """Получить конфигурацию LLM."""
    config = load_config()
    return config.get('llm', {})


def get_logging_config() -> Dict[str, Any]:
    """Получить конфигурацию логирования."""
    config = load_config()
    return config.get('logging', {})