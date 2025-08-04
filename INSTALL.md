# Инструкция по установке и запуску LLM-ассистента

## Требования

- **Docker Desktop** или **Docker Engine**
- **Make** (опционально, для удобства)
- Токены:
  - Telegram Bot Token (от @BotFather)
  - OpenRouter API Key (от https://openrouter.ai/)

## Быстрый запуск

### 1. Клонирование и настройка

```bash
# Клонируем репозиторий
git clone <repository-url>
cd llm-consultant

# Создаем .env файл из примера
cp env.example .env

# Редактируем .env файл - добавляем реальные токены
# TELEGRAM_BOT_TOKEN=ваш_токен_от_BotFather
# OPENROUTER_API_KEY=ваш_ключ_от_OpenRouter
```

### 2. Запуск через Make (рекомендуется)

```bash
# Сборка Docker образа
make build

# Запуск бота
make run

# Просмотр логов
make logs

# Остановка
make stop
```

### 3. Запуск через Docker (альтернатива)

```bash
# Сборка образа
docker build -t llm-consultant .

# Запуск контейнера
docker run -d \
  --name llm-consultant \
  --env-file .env \
  -v ./logs:/app/logs \
  -v ./config:/app/config \
  llm-consultant

# Просмотр логов
docker logs -f llm-consultant

# Остановка
docker stop llm-consultant
docker rm llm-consultant
```

## Получение токенов

### Telegram Bot Token

1. Найдите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям для создания бота
4. Скопируйте полученный токен в `.env` файл

### OpenRouter API Key

1. Зайдите на https://openrouter.ai/
2. Зарегистрируйтесь или войдите в аккаунт
3. Перейдите в раздел Keys: https://openrouter.ai/keys
4. Создайте новый API ключ
5. Скопируйте ключ в `.env` файл

## Конфигурация

### Основные настройки (`config/settings.yaml`)

```yaml
bot:
  name: "LLM Consultant"
  description: "Консультант по услугам компании"

llm:
  model: "google/gemini-2.0-flash-exp:free"  # Модель LLM
  max_tokens: 1000                           # Максимум токенов ответа
  temperature: 0.7                           # Творческость (0.0-2.0)
  timeout_seconds: 30                        # Таймаут запросов
  max_retries: 2                            # Повторные попытки
```

### Промпты (`config/prompts.yaml`)

Вы можете изменить поведение бота, отредактировав промпты в файле `config/prompts.yaml`:

- `system_prompt` - основная инструкция для LLM
- `welcome_message` - приветствие `/start`
- `help_message` - справка `/help`
- `contact_message` - контакты `/contact`
- `error_message` - сообщение при ошибках

## Команды бота

- `/start` - начало работы
- `/help` - справка
- `/contact` - контактная информация  
- `/clear` - очистить историю диалога
- `/memory` - показать историю диалога
- Любое текстовое сообщение - консультация через LLM

## Полезные команды

### Управление через Make

```bash
make help     # Показать все доступные команды
make setup    # Первоначальная настройка проекта
make build    # Пересобрать образ
make restart  # Перезапустить (stop + build + run)
make test     # Запустить тесты
make clean    # Полная очистка (контейнеры + образы)
```

### Просмотр логов

```bash
# Логи в реальном времени
make logs

# Или через Docker
docker logs -f llm-consultant

# Файлы логов на хосте (если примонтированы)
tail -f logs/app_$(date +%Y-%m-%d).log
tail -f logs/conversations_$(date +%Y-%m-%d).json
```

### Тестирование

```bash
# Запуск всех тестов
make test

# Локальный запуск тестов (если установлен Python)
python -m pytest tests/ -v
```

## Устранение проблем

### Бот не запускается

1. Проверьте токены в `.env` файле
2. Убедитесь что Docker запущен
3. Проверьте логи: `make logs`

### Бот не отвечает

1. Проверьте что у вас есть кредиты на OpenRouter
2. Проверьте интернет соединение
3. Посмотрите логи ошибок: `tail -f logs/errors_$(date +%Y-%m-%d).json`

### Проблемы с LLM

1. Проверьте статус OpenRouter: https://status.openrouter.ai/
2. Попробуйте другую модель в `config/settings.yaml`
3. Проверьте лимиты API ключа на OpenRouter

### Ошибки Docker

```bash
# Пересоздать образ
make clean
make build

# Проверить статус контейнера
docker ps -a

# Удалить зависшие контейнеры
docker container prune
```

## Структура проекта

```
llm-consultant/
├── src/                   # Исходный код
├── config/               # Конфигурационные файлы
├── logs/                 # Логи (создается автоматически)
├── tests/                # Тесты
├── Dockerfile           # Образ Docker
├── Makefile            # Команды автоматизации
├── pyproject.toml      # Зависимости Python
├── .env                # Переменные окружения (создать из env.example)
└── README.md           # Основная документация
```

## Разработка

### Локальный запуск без Docker

```bash
# Установка зависимостей
pip install uv
uv pip install .

# Запуск бота
python src/bot.py
```

### Изменение конфигурации

После изменения файлов в `config/` перезапустите бота:

```bash
make restart
```

Изменения применятся автоматически.