"""
Система логирования для LLM-ассистента.
Простое логирование в JSON файлы по дням согласно vision.md.
"""

import json
import logging
import os
from datetime import datetime, date
from typing import Optional


def get_project_root() -> str:
    """Получить путь к корню проекта."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def setup_logging() -> None:
    """Настройка Python logging с записью в файлы по дням."""
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    
    # Создаем папку для логов если не существует
    os.makedirs(logs_dir, exist_ok=True)
    
    # Формируем имя файла с текущей датой
    today = date.today().strftime("%Y-%m-%d")
    log_file = os.path.join(logs_dir, f'app_{today}.log')
    
    # Настраиваем логирование
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_file, encoding='utf-8'),
            logging.StreamHandler()
        ]
    )
    
    logging.info(f"Логирование настроено. Файл: {log_file}")


def log_conversation(user_id: int, username: Optional[str], user_message: str, bot_response: str, response_time_ms: Optional[int] = None) -> None:
    """
    Логирование диалога пользователя в JSON файл.
    
    Args:
        user_id: ID пользователя Telegram
        username: Имя пользователя
        user_message: Сообщение пользователя  
        bot_response: Ответ бота
        response_time_ms: Время ответа в миллисекундах
    """
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    today = date.today().strftime("%Y-%m-%d")
    conversations_file = os.path.join(logs_dir, f'conversations_{today}.json')
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "username": username,
        "user_message": user_message,
        "bot_response": bot_response,
        "response_time_ms": response_time_ms
    }
    
    try:
        with open(conversations_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        logging.error(f"Ошибка записи лога диалога: {e}")


def log_llm_request(user_id: int, model: str, prompt_tokens: Optional[int] = None, completion_tokens: Optional[int] = None, response_time_ms: Optional[int] = None, status: str = "success", error: Optional[str] = None) -> None:
    """
    Логирование запроса к LLM в JSON файл.
    
    Args:
        user_id: ID пользователя
        model: Используемая модель LLM
        prompt_tokens: Количество токенов в промпте
        completion_tokens: Количество токенов в ответе
        response_time_ms: Время ответа в миллисекундах
        status: Статус запроса (success/error)
        error: Текст ошибки если есть
    """
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    today = date.today().strftime("%Y-%m-%d")
    llm_requests_file = os.path.join(logs_dir, f'llm_requests_{today}.json')
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "user_id": user_id,
        "model": model,
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": (prompt_tokens or 0) + (completion_tokens or 0) if prompt_tokens and completion_tokens else None,
        "response_time_ms": response_time_ms,
        "status": status,
        "error": error
    }
    
    try:
        with open(llm_requests_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        logging.error(f"Ошибка записи лога LLM запроса: {e}")


def log_error(error_type: str, error_message: str, user_id: Optional[int] = None, additional_data: Optional[dict] = None) -> None:
    """
    Логирование ошибок в отдельный JSON файл.
    
    Args:
        error_type: Тип ошибки
        error_message: Сообщение об ошибке
        user_id: ID пользователя если есть
        additional_data: Дополнительные данные
    """
    project_root = get_project_root()
    logs_dir = os.path.join(project_root, 'logs')
    today = date.today().strftime("%Y-%m-%d")
    errors_file = os.path.join(logs_dir, f'errors_{today}.json')
    
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "error_type": error_type,
        "error_message": error_message,
        "user_id": user_id,
        "additional_data": additional_data or {}
    }
    
    try:
        with open(errors_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
    except Exception as e:
        logging.error(f"Ошибка записи лога ошибки: {e}")