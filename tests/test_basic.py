"""
Базовые тесты для LLM-ассистента.
Простые тесты без сложных моков согласно convention.md.
"""

import pytest
import os
import sys

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import load_config, load_prompts, get_llm_config
from conversation_memory import ConversationMemory
from logger import setup_logging


class TestConfig:
    """Тесты конфигурации."""
    
    def test_load_config_returns_dict(self):
        """Тест что load_config возвращает словарь."""
        config = load_config()
        assert isinstance(config, dict)
        assert 'bot' in config
        assert 'llm' in config
    
    def test_load_prompts_returns_dict(self):
        """Тест что load_prompts возвращает словарь."""
        prompts = load_prompts()
        assert isinstance(prompts, dict)
        assert 'system_prompt' in prompts
        assert 'welcome_message' in prompts
    
    def test_get_llm_config_has_required_fields(self):
        """Тест что LLM конфигурация содержит нужные поля."""
        llm_config = get_llm_config()
        assert 'model' in llm_config
        assert 'max_tokens' in llm_config
        assert 'temperature' in llm_config


class TestConversationMemory:
    """Тесты памяти диалогов."""
    
    def setup_method(self):
        """Настройка перед каждым тестом."""
        self.memory = ConversationMemory()
        # Очищаем историю для тестового пользователя
        self.test_user_id = 999999
        self.memory.clear_history(self.test_user_id)
    
    def test_memory_is_singleton(self):
        """Тест что память - синглтон."""
        memory1 = ConversationMemory()
        memory2 = ConversationMemory()
        assert memory1 is memory2
    
    def test_empty_history_for_new_user(self):
        """Тест что для нового пользователя история пуста."""
        history = self.memory.get_history(self.test_user_id)
        assert history == []
    
    def test_add_and_get_message(self):
        """Тест добавления и получения сообщения."""
        self.memory.add_message(self.test_user_id, "user", "Привет")
        self.memory.add_message(self.test_user_id, "assistant", "Привет! Как дела?")
        
        history = self.memory.get_history(self.test_user_id)
        assert len(history) == 2
        assert history[0]["role"] == "user"
        assert history[0]["content"] == "Привет"
        assert history[1]["role"] == "assistant"
        assert history[1]["content"] == "Привет! Как дела?"
    
    def test_history_limit(self):
        """Тест ограничения истории."""
        # Добавляем больше сообщений чем лимит
        for i in range(25):
            self.memory.add_message(self.test_user_id, "user", f"Сообщение {i}")
        
        # Проверяем что история ограничена
        history = self.memory.get_history(self.test_user_id, 50)
        assert len(history) <= 20  # Лимит в conversation_memory.py
    
    def test_clear_history(self):
        """Тест очистки истории."""
        self.memory.add_message(self.test_user_id, "user", "Тест")
        assert len(self.memory.get_history(self.test_user_id)) == 1
        
        self.memory.clear_history(self.test_user_id)
        assert len(self.memory.get_history(self.test_user_id)) == 0
    
    def test_get_stats(self):
        """Тест получения статистики."""
        self.memory.add_message(self.test_user_id, "user", "Тест")
        stats = self.memory.get_stats()
        
        assert isinstance(stats, dict)
        assert 'total_users' in stats
        assert 'total_messages' in stats
        assert stats['total_users'] >= 1
        assert stats['total_messages'] >= 1


class TestLogging:
    """Тесты логирования."""
    
    def test_setup_logging_no_errors(self):
        """Тест что setup_logging выполняется без ошибок."""
        try:
            setup_logging()
            assert True
        except Exception as e:
            pytest.fail(f"setup_logging вызвал исключение: {e}")


class TestProjectStructure:
    """Тесты структуры проекта."""
    
    def test_required_files_exist(self):
        """Тест что все необходимые файлы существуют."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        # Файлы, которые должны быть доступны в контейнере
        required_files = [
            'src/bot.py',
            'src/handlers.py', 
            'src/llm_client.py',
            'src/config.py',
            'src/logger.py',
            'src/conversation_memory.py',
            'config/settings.yaml',
            'config/prompts.yaml'
        ]
        
        for file_path in required_files:
            full_path = os.path.join(project_root, file_path)
            assert os.path.exists(full_path), f"Файл {file_path} не существует"
        
        # Проверяем дополнительные файлы только при локальном запуске (не в Docker)
        if not os.path.exists('/app'):  # Проверяем что мы не в Docker контейнере
            build_files = ['Dockerfile', 'Makefile', 'pyproject.toml']
            for file_path in build_files:
                full_path = os.path.join(project_root, file_path)
                assert os.path.exists(full_path), f"Файл {file_path} не существует (локальный запуск)"
    
    def test_directories_exist(self):
        """Тест что все необходимые директории существуют."""
        project_root = os.path.dirname(os.path.dirname(__file__))
        
        required_dirs = [
            'src',
            'config', 
            'logs',
            'tests'
        ]
        
        for dir_path in required_dirs:
            full_path = os.path.join(project_root, dir_path)
            assert os.path.exists(full_path), f"Директория {dir_path} не существует"
            assert os.path.isdir(full_path), f"{dir_path} не является директорией"


if __name__ == "__main__":
    pytest.main([__file__])