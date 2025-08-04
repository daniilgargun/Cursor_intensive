"""
LLM клиент для работы с Google Gemini через OpenRouter.
Простой клиент без сложных абстракций.
"""

import os
import logging
import time
import asyncio
from openai import OpenAI

from logger import log_llm_request, log_error
from config import get_llm_config, load_prompts
from conversation_memory import conversation_memory


class LLMClient:
    """Простой клиент для работы с LLM через OpenRouter."""
    
    def __init__(self):
        """Инициализация клиента с настройками из конфигурации."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        
        # Загружаем конфигурацию LLM
        llm_config = get_llm_config()
        self.model = llm_config.get('model', 'google/gemini-2.0-flash-exp:free')
        self.max_tokens = llm_config.get('max_tokens', 1000)
        self.temperature = llm_config.get('temperature', 0.7)
        self.history_limit = llm_config.get('history_limit', 6)
        self.timeout_seconds = llm_config.get('timeout_seconds', 30)
        self.max_retries = llm_config.get('max_retries', 2)
        self.retry_delay = llm_config.get('retry_delay_seconds', 1)
        
        # Используем глобальное хранилище истории диалогов
        
        # Загружаем промпты из конфигурации
        prompts = load_prompts()
        self.system_prompt = prompts.get('system_prompt', 'Ты консультант компании.')
        
        logging.info(f"LLM клиент инициализирован: модель={self.model}, max_tokens={self.max_tokens}, timeout={self.timeout_seconds}s")

    async def get_response(self, user_message: str, user_id: int, user_name: str = None) -> str:
        """
        Получить ответ от LLM на сообщение пользователя.
        
        Args:
            user_message: Сообщение пользователя
            user_id: ID пользователя для истории диалога
            user_name: Имя пользователя (опционально)
            
        Returns:
            Ответ от LLM
        """
        start_time = time.time()
        
        # Получаем историю диалога для пользователя
        history = conversation_memory.get_history(user_id, self.history_limit)
        
        # Формируем сообщения с учетом истории
        messages = [{"role": "system", "content": self.system_prompt}]
        messages.extend(history)
        
        # Добавляем текущее сообщение
        current_message = f"Клиент {user_name}: {user_message}" if user_name else user_message
        messages.append({"role": "user", "content": current_message})
        
        logging.info(f"Отправляем запрос к LLM: {user_message}")
        
        # Пробуем отправить запрос с повторными попытками
        for attempt in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    asyncio.to_thread(
                        self.client.chat.completions.create,
                        model=self.model,
                        messages=messages,
                        max_tokens=self.max_tokens,
                        temperature=self.temperature
                    ),
                    timeout=self.timeout_seconds
                )
                
                # Вычисляем время ответа
                response_time_ms = int((time.time() - start_time) * 1000)
                
                llm_response = response.choices[0].message.content
                logging.info(f"Получен ответ от LLM: {llm_response[:100]}...")
                
                # Логируем LLM запрос
                prompt_tokens = response.usage.prompt_tokens if response.usage else None
                completion_tokens = response.usage.completion_tokens if response.usage else None
                
                log_llm_request(
                    user_id=user_id,
                    model=self.model,
                    prompt_tokens=prompt_tokens,
                    completion_tokens=completion_tokens,
                    response_time_ms=response_time_ms,
                    status="success"
                )
                
                # Сохраняем в историю диалога
                conversation_memory.add_message(user_id, "user", current_message)
                conversation_memory.add_message(user_id, "assistant", llm_response)
                
                return llm_response
                
            except asyncio.TimeoutError:
                error_msg = f"Таймаут LLM запроса ({self.timeout_seconds}s) - попытка {attempt + 1}/{self.max_retries + 1}"
                logging.warning(error_msg)
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # Последняя попытка не удалась
                    self._log_llm_error(user_id, user_message, f"Timeout after {self.max_retries + 1} attempts", time.time() - start_time)
                    break
                    
            except Exception as e:
                error_msg = f"Ошибка LLM запроса: {str(e)} - попытка {attempt + 1}/{self.max_retries + 1}"
                logging.error(error_msg)
                
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay)
                    continue
                else:
                    # Последняя попытка не удалась
                    self._log_llm_error(user_id, user_message, str(e), time.time() - start_time)
                    break
        
        # Все попытки исчерпаны - возвращаем fallback сообщение
        return self._get_error_message()
    
    def _log_llm_error(self, user_id: int, user_message: str, error: str, elapsed_time: float) -> None:
        """Логирование ошибки LLM запроса."""
        response_time_ms = int(elapsed_time * 1000)
        
        # Логируем ошибку LLM запроса
        log_llm_request(
            user_id=user_id,
            model=self.model,
            response_time_ms=response_time_ms,
            status="error",
            error=error
        )
        
        # Логируем ошибку в отдельный файл
        log_error(
            error_type="llm_request_error",
            error_message=error,
            user_id=user_id,
            additional_data={"model": self.model, "message": user_message}
        )
    
    def _get_error_message(self) -> str:
        """Получить сообщение об ошибке из конфигурации."""
        try:
            prompts = load_prompts()
            return prompts.get('error_message', 'Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже.')
        except Exception:
            # Если даже конфигурация не загружается - используем hardcoded сообщение
            return 'Извините, произошла техническая ошибка. Попробуйте позже или обратитесь к менеджеру.'


def create_llm_client() -> LLMClient:
    """Создать экземпляр LLM клиента."""
    return LLMClient()