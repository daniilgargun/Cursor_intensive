.PHONY: help build run stop restart logs clean test setup

help:
	@echo "Доступные команды:"
	@echo "  setup    - Первоначальная настройка проекта"
	@echo "  build    - Сборка Docker образа"
	@echo "  run      - Запуск контейнера"
	@echo "  stop     - Остановка контейнера"
	@echo "  restart  - Перезапуск контейнера"
	@echo "  logs     - Просмотр логов"
	@echo "  test     - Запуск тестов"
	@echo "  clean    - Очистка контейнеров и образов"

setup:
	@echo "Настройка проекта..."
	@mkdir -p logs config src tests
	@cp .env.example .env || echo "Создайте файл .env по примеру .env.example"
	@echo "Проект настроен. Заполните .env файл токенами."

build:
	docker build -t llm-consultant .

run:
	docker run -d \
		--name llm-consultant \
		--env-file .env \
		-v ./logs:/app/logs \
		-v ./config:/app/config \
		llm-consultant

stop:
	docker stop llm-consultant || true
	docker rm llm-consultant || true

restart: stop build run

logs:
	docker logs -f llm-consultant

test:
	docker run --rm \
		--env-file .env \
		-v ./tests:/app/tests \
		-v ./src:/app/src \
		-v ./config:/app/config \
		llm-consultant \
		bash -c "pip install pytest && python -m pytest tests/ -v"

clean:
	docker stop llm-consultant || true
	docker rm llm-consultant || true
	docker rmi llm-consultant || true
	docker system prune -f