FROM python:3.11-slim

WORKDIR /app

# Установка uv для управления зависимостями
RUN pip install uv

# Копирование файла зависимостей
COPY pyproject.toml .

# Установка зависимостей с увеличенным таймаутом
ENV UV_HTTP_TIMEOUT=300
RUN uv pip install --system .

# Создание необходимых папок
RUN mkdir -p logs config

# Копирование конфигурационных файлов
COPY config/ ./config/
# COPY .env .

# Копирование исходного кода
COPY src/ ./src/

# Запуск приложения
CMD ["python", "src/bot.py"]