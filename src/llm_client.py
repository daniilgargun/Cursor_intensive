"""
LLM клиент для работы с Google Gemini через OpenRouter.
Простой клиент без сложных абстракций.
"""

import os
import logging
from openai import OpenAI


class LLMClient:
    """Простой клиент для работы с LLM через OpenRouter."""
    
    def __init__(self):
        """Инициализация клиента с настройками."""
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.model = "google/gemini-2.0-flash-exp:free"
        
        # Простое хранение истории диалогов в памяти
        self.conversations = {}
        
        # Системный промпт для роли консультанта
        self.system_prompt = """Ты - консультант компании по оказанию услуг.

Твоя задача:
- Выявить потребности клиента
- Задать уточняющие вопросы для понимания проблем
- Предложить подходящие услуги компании
- Быть дружелюбным и профессиональным

Отвечай кратко и по делу. Если клиент задает общий вопрос, уточни детали.
Если не знаешь конкретных услуг компании, предложи связаться с менеджером."""

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
        try:
            # Получаем или создаем историю диалога для пользователя
            if user_id not in self.conversations:
                self.conversations[user_id] = []
            
            # Формируем сообщения с учетом истории
            messages = [{"role": "system", "content": self.system_prompt}]
            
            # Добавляем последние 3 пары сообщений из истории (ограничиваем контекст)
            recent_history = self.conversations[user_id][-6:]  # 3 пары (user + assistant)
            messages.extend(recent_history)
            
            # Добавляем текущее сообщение
            current_message = f"Клиент {user_name}: {user_message}" if user_name else user_message
            messages.append({"role": "user", "content": current_message})
            
            logging.info(f"Отправляем запрос к LLM: {user_message}")
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=1000,
                temperature=0.7
            )
            
            llm_response = response.choices[0].message.content
            logging.info(f"Получен ответ от LLM: {llm_response[:100]}...")
            
            # Сохраняем в историю диалога
            self.conversations[user_id].append({"role": "user", "content": current_message})
            self.conversations[user_id].append({"role": "assistant", "content": llm_response})
            
            return llm_response
            
        except Exception as e:
            logging.error(f"Ошибка при запросе к LLM: {e}")
            return "Извините, произошла ошибка при обработке вашего запроса. Попробуйте позже или обратитесь к нашему менеджеру."


def create_llm_client() -> LLMClient:
    """Создать экземпляр LLM клиента."""
    return LLMClient()