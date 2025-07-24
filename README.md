# Telegram Authentication Service

## Описание

**Сервис аутентификации Telegram** — это микросервис для аутентификации пользователей через Telegram Web App. Сервис обеспечивает безопасную аутентификацию, выдачу и обновление JWT-токенов, а также интеграцию с другими микросервисами через RESTful API. Он предназначен для работы с Telegram Mini Apps, валидируя данные `initData` и управляя пользовательскими сессиями.

**Основные функции:**
- **Аутентификация пользователей**: Проверка `initData` из Telegram Web App, создание или обновление пользовательских данных.
- **Управление токенами**: Генерация и обновление пары JWT-токенов (access и refresh).
- **API-ориентированность**: RESTful API для интеграции с фронтендом или другими микросервисами.
- **Логирование**: Детализированное логирование для отладки и мониторинга.

**Роль в системе:**
- Обеспечение безопасной аутентификации пользователей Telegram.
- Хранение данных о пользователях Telegram в базе данных.
- Интеграция с другими сервисами через API для передачи пользовательских данных и токенов.

## Технологии и зависимости

### Технологический стек
- **Python**: 3.13.5
- **Django**: 5.2.4
- **Django REST Framework**: Для создания RESTful API.
- **Simple JWT**: Для управления JWT-токенами.
- **Pytest**: Для юнит- и функционального тестирования.
- **PostgreSQL**: Для хранения данных.

### Ключевые зависимости
- `django`: Фреймворк для веб-разработки.
- `djangorestframework`: Инструменты для создания RESTful API.
- `djangorestframework-simplejwt`: Управление JWT-токенами.
- `pytest`, `pytest-django`: Фреймворк для тестирования.
- Полный список зависимостей указан в `pyproject.toml`.

## Начало работы

### Требования
- Python >= 3.13.5
- uv (для управления зависимостями)
- PostgreSQL

### Установка

1. **Клонирование репозитория**:
   ```bash
   git clone https://github.com/pabloERSH/auth-service.git
   cd auth-service
   ```

2. **Установка зависимостей**:
   ```bash
   uv sync
   ```

3. **Настройка окружения**:
   - Скопируйте файл примера окружения:
     ```bash
     cp .env.example .env
     ```
   - Обновите `.env` с настройками базы данных и других параметров:
     ```
     SECRET_KEY=your_secret_key
     DEBUG=True
     DB_NAME=your_db_name
     DB_USER=your_username
     DB_PASSWORD=your_password
     DB_HOST=127.0.0.1
     DB_PORT=5432
     BOT_TOKEN=your_telegram_bot_token
     ```

4. **Запуск миграций базы данных**:
   ```bash
   uv run python manage.py migrate
   ```

5. **Запуск локального сервера**:
   ```bash
   uv run python manage.py runserver
   ```
   Сервис будет доступен по адресу: [http://localhost:8000](http://localhost:8000).

## Запуск через Docker

### Требования
- Docker
- Docker Compose

1. **Настройка окружения**:
   Проверьте `.env`, следующие значения должны быть заданы:
   ```
   DB_NAME=your_container_db_name
   DB_USER=your_container_db_username
   DB_PASSWORD=your_container_db_password
   SECRET_KEY=your_secret_key
   BOT_TOKEN=your_telegram_bot_token
   ```

2. **Запуск локального сервера**:
   Создать и запустить все требуемые контейнеры:
   ```bash
   docker-compose up -d --build
   ```
   После этого сервис станет доступен на порту, указанном в `docker-compose.yml`.

   Для остановки сервиса:
   ```bash
   docker-compose stop
   ```

   Для повторного запуска:
   ```bash
   docker-compose start
   ```

   Для остановки и удаления всех созданных контейнеров:
   ```bash
   docker-compose down
   ```

## Документация API

Сервис предоставляет RESTful API под префиксом `/api/v1`. Эндпоинты для аутентификации и обновления токенов не требуют предварительной авторизации.

### Эндпоинты аутентификации

- **POST /api/v1/tguser/auth/login/**
  - **Описание**: Аутентифицирует пользователя через Telegram Web App, возвращает данные пользователя и пару JWT-токенов.
  - **Заголовки**:
    - `Content-Type: application/json`
    - `Accept: application/json`
  - **Параметры**:
    - `initData` (строка, обязательный): Данные `initData` из Telegram Web App.
  - **Пример запроса**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/login/ \
         -H "Content-Type: application/json" \
         -d '{"initData": "user=%7B%22id%22%3A123456789%2C%22first_name%22%3A%22John%22%2C%22last_name%22%3A%22Doe%22%2C%22username%22%3A%22johndoe%22%7D&auth_date=1698765432&hash=abc123..."}'
    ```
  - **Ответ (200 OK)**:
    ```json
    {
      "data": {
        "user": {
          "telegram_id": 123456789,
          "username": "johndoe"
        },
        "tokens": {
          "access": "<access_token>",
          "refresh": "<refresh_token>"
        }
      },
      "message": "Authentication success!"
    }
    ```

- **POST /api/v1/tguser/auth/refresh/**
  - **Описание**: Обновляет пару JWT-токенов на основе переданного refresh-токена.
  - **Заголовки**:
    - `Content-Type: application/json`
    - `Accept: application/json`
  - **Параметры**:
    - `refresh_token` (строка, обязательный): Refresh-токен для обновления.
  - **Пример запроса**:
    ```bash
    curl -X POST http://localhost:8000/api/v1/auth/refresh/ \
         -H "Content-Type: application/json" \
         -d '{"refresh_token": "<refresh_token>"}'
    ```
  - **Ответ (200 OK)**:
    ```json
    {
      "data": {
        "user": {
          "telegram_id": 123456789,
          "username": "johndoe"
        },
        "tokens": {
          "access": "<new_access_token>",
          "refresh": "<new_refresh_token>"
        }
      },
      "message": "Refresh tokens success!"
    }
    ```

## Тестирование

Запустите все тесты с помощью Pytest:
```bash
cd auth_service
uv run pytest
```
Или с анализом покрытия:
```bash
uv run pytest --cov=telegram_user --cov-report=html
```

Тестовый набор включает:
- **Юнит-тесты для парсинга данных** (`test_tg_parser.py`):
  - Проверка валидации хэша (`_check_hash`) для корректных и некорректных данных.
  - Тестирование общей валидации `initData` (`_validate_and_parse`) на случаи отсутствия `BOT_TOKEN`, устаревших данных и некорректного хэша.
  - Проверка парсинга пользовательских данных (`parse_userData`) на наличие обязательных полей и корректность формата.
- **Юнит-тесты для сервиса аутентификации** (`test_tg_user_auth.py`):
  - Тестирование генерации JWT-токенов (`_generate_jwt_token`) с проверкой структуры и содержимого токенов.
  - Проверка метода аутентификации (`authenticate`) на успешное создание/обновление пользователя и генерацию токенов.
  - Тестирование обновления токенов (`refresh_user_token`) на успешное обновление и корректность возвращаемых данных.
- **Функциональные тесты для API** (`test_views.py`):
  - Тестирование эндпоинта `/api/v1/auth/login/` на успешную аутентификацию, отсутствие `initData` и некорректные данные.
  - Тестирование эндпоинта `/api/v1/auth/refresh/` на успешное обновление токенов, отсутствие refresh-токена и некорректный токен.

## Пример взаимодействия с фронтендом

Ниже приведен пример JavaScript-кода для взаимодействия с API сервиса аутентификации через Telegram Web App.

```javascript
// Функция для аутентификации через Telegram Web App
async function authenticateWithTelegram() {
  try {
    // Проверяем наличие Telegram Web App
    if (!window.Telegram?.WebApp) {
      throw new Error('Telegram Web App is not available');
    }

    // Получаем initData из Telegram Web App
    const initData = window.Telegram.WebApp.initData;

    const response = await fetch('http://localhost:8000/api/v1/tguser/auth/login/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ initData }),
    });

    const result = await response.json();

    if (response.ok) {
      // Сохраняем токены, например, в localStorage
      localStorage.setItem('access_token', result.data.tokens.access);
      localStorage.setItem('refresh_token', result.data.tokens.refresh);
      console.log('Authentication successful:', result.data.user);
      return result.data;
    } else {
      throw new Error(result.error || 'Authentication failed');
    }
  } catch (error) {
    console.error('Authentication error:', error.message);
    throw error;
  }
}

// Функция для обновления токенов
async function refreshTokens() {
  try {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) {
      throw new Error('No refresh token found');
    }

    const response = await fetch('http://localhost:8000/api/v1/tguser/auth/refresh/', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
      },
      body: JSON.stringify({ refresh_token: refreshToken }),
    });

    const result = await response.json();

    if (response.ok) {
      // Обновляем токены в localStorage
      localStorage.setItem('access_token', result.data.tokens.access);
      localStorage.setItem('refresh_token', result.data.tokens.refresh);
      console.log('Tokens refreshed successfully:', result.data.user);
      return result.data;
    } else {
      throw new Error(result.error || 'Token refresh failed');
    }
  } catch (error) {
    console.error('Token refresh error:', error.message);
    throw error;
  }
}

// Пример использования
document.addEventListener('DOMContentLoaded', async () => {
  try {
    const authData = await authenticateWithTelegram();
    console.log('User authenticated:', authData.user);

    // Обновление токенов через 10 минут
    setTimeout(async () => {
      const refreshedData = await refreshTokens();
      console.log('Tokens refreshed:', refreshedData.user);
    }, 10 * 60 * 1000);
  } catch (error) {
    console.error('Error during authentication:', error);
  }
});