FROM python:3.13.5-slim-bookworm

# Установка системных зависимостей для сборки Python-пакетов
RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Установка uv - пакетного менеджера
COPY --from=ghcr.io/astral-sh/uv:0.7.19 /uv /uvx /bin/

WORKDIR /app

# Настройка окружения
ENV UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Копируем только файлы зависимостей сначала
COPY pyproject.toml uv.lock ./

# Устанавливаем зависимости
RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --locked --no-install-project --no-dev

# Копируем остальной код
COPY . .

# Создаем непривилегированного пользователя
RUN useradd -m appuser && \
    chown -R appuser:appuser /app
USER appuser

# Переходим в директорию с Django проектом
WORKDIR /app/auth_service

# Открываем порт
EXPOSE 8000

# Запускаем миграции и затем сервер gunicorn
CMD ["sh", "-c", "uv run manage.py migrate && exec uv run gunicorn --bind 0.0.0.0:8000 --workers 3 auth_service.wsgi:application"]