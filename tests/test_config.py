"""
Тесты конфигурации и обработки ошибок.
"""

import pytest
import os
import sys
import tempfile
import yaml

# Добавляем src в путь для импортов
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from config import load_config, load_prompts


class TestConfigErrorHandling:
    """Тесты обработки ошибок конфигурации."""
    
    def test_load_config_with_missing_file(self, monkeypatch):
        """Тест load_config с отсутствующим файлом."""
        # Подменяем путь на несуществующий файл
        def mock_get_project_root():
            return "/nonexistent/path"
        
        import config
        monkeypatch.setattr(config, 'get_project_root', mock_get_project_root)
        
        # Должен вернуть базовую конфигурацию без исключений
        result = load_config()
        assert isinstance(result, dict)
        assert 'bot' in result
        assert 'llm' in result
    
    def test_load_prompts_with_missing_file(self, monkeypatch):
        """Тест load_prompts с отсутствующим файлом."""
        # Подменяем путь на несуществующий файл
        def mock_get_project_root():
            return "/nonexistent/path"
        
        import config
        monkeypatch.setattr(config, 'get_project_root', mock_get_project_root)
        
        # Должен вернуть базовые промпты без исключений
        result = load_prompts()
        assert isinstance(result, dict)
        assert 'system_prompt' in result
        assert 'welcome_message' in result
    
    def test_load_config_with_invalid_yaml(self, monkeypatch):
        """Тест load_config с невалидным YAML."""
        # Создаем временный файл с невалидным YAML
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_file = f.name
        
        try:
            def mock_get_project_root():
                return os.path.dirname(temp_file)
            
            import config
            monkeypatch.setattr(config, 'get_project_root', mock_get_project_root)
            
            # Подменяем имя файла
            original_join = os.path.join
            def mock_join(path, *paths):
                if 'settings.yaml' in paths:
                    return temp_file
                return original_join(path, *paths)
            
            monkeypatch.setattr(os.path, 'join', mock_join)
            
            # Должен вернуть базовую конфигурацию без исключений
            result = load_config()
            assert isinstance(result, dict)
            assert 'bot' in result
        finally:
            os.unlink(temp_file)


class TestConfigValidation:
    """Тесты валидации конфигурации."""
    
    def test_config_has_all_required_sections(self):
        """Тест что конфигурация содержит все нужные секции."""
        config = load_config()
        
        # Проверяем секцию bot
        assert 'bot' in config
        bot_config = config['bot']
        assert 'name' in bot_config
        assert 'description' in bot_config
        
        # Проверяем секцию llm
        assert 'llm' in config
        llm_config = config['llm']
        assert 'model' in llm_config
        assert 'max_tokens' in llm_config
        assert 'temperature' in llm_config
        
        # Проверяем секцию logging
        assert 'logging' in config
        logging_config = config['logging']
        assert 'level' in logging_config
    
    def test_prompts_have_all_required_messages(self):
        """Тест что промпты содержат все нужные сообщения."""
        prompts = load_prompts()
        
        required_prompts = [
            'system_prompt',
            'welcome_message', 
            'help_message',
            'contact_message',
            'error_message'
        ]
        
        for prompt_name in required_prompts:
            assert prompt_name in prompts, f"Отсутствует промпт: {prompt_name}"
            assert isinstance(prompts[prompt_name], str), f"Промпт {prompt_name} не является строкой"
            assert len(prompts[prompt_name]) > 0, f"Промпт {prompt_name} пустой"
    
    def test_llm_config_values_are_valid(self):
        """Тест что значения LLM конфигурации валидны."""
        from config import get_llm_config
        llm_config = get_llm_config()
        
        # Проверяем типы и диапазоны значений
        assert isinstance(llm_config.get('max_tokens', 0), int)
        assert llm_config.get('max_tokens', 0) > 0
        
        assert isinstance(llm_config.get('temperature', 0.0), (int, float))
        assert 0.0 <= llm_config.get('temperature', 0.0) <= 2.0
        
        assert isinstance(llm_config.get('timeout_seconds', 0), int) 
        assert llm_config.get('timeout_seconds', 0) > 0
        
        assert isinstance(llm_config.get('model', ''), str)
        assert len(llm_config.get('model', '')) > 0


if __name__ == "__main__":
    pytest.main([__file__])