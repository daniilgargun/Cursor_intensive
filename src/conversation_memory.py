"""
Простое хранилище истории диалогов в памяти.
Синглтон для сохранения состояния между запросами.
"""

from typing import Dict, List, Any


class ConversationMemory:
    """Простое хранилище истории диалогов в памяти."""
    
    _instance = None
    _conversations: Dict[int, List[Dict[str, str]]] = {}
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConversationMemory, cls).__new__(cls)
        return cls._instance
    
    def get_history(self, user_id: int, limit: int = 6) -> List[Dict[str, str]]:
        """
        Получить историю диалога для пользователя.
        
        Args:
            user_id: ID пользователя
            limit: Максимальное количество сообщений
            
        Returns:
            Список последних сообщений
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        # Возвращаем последние N сообщений
        return self._conversations[user_id][-limit:]
    
    def add_message(self, user_id: int, role: str, content: str) -> None:
        """
        Добавить сообщение в историю диалога.
        
        Args:
            user_id: ID пользователя
            role: Роль (user/assistant)
            content: Содержимое сообщения
        """
        if user_id not in self._conversations:
            self._conversations[user_id] = []
        
        self._conversations[user_id].append({
            "role": role,
            "content": content
        })
        
        # Ограничиваем историю (оставляем последние 20 сообщений)
        if len(self._conversations[user_id]) > 20:
            self._conversations[user_id] = self._conversations[user_id][-20:]
    
    def clear_history(self, user_id: int) -> None:
        """Очистить историю диалога для пользователя."""
        if user_id in self._conversations:
            del self._conversations[user_id]
    
    def get_stats(self) -> Dict[str, Any]:
        """Получить статистику по диалогам."""
        return {
            "total_users": len(self._conversations),
            "total_messages": sum(len(history) for history in self._conversations.values()),
            "users_with_history": [user_id for user_id, history in self._conversations.items() if len(history) > 0]
        }


# Создаем глобальный экземпляр
conversation_memory = ConversationMemory()