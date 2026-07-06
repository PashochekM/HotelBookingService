# Hotel Booking Service

Backend-сервис для бронирования номеров в отелях. Проект написан на FastAPI и показывает типичный набор задач backend-разработки: REST API, авторизация, работа с PostgreSQL, миграции, кеширование, загрузка изображений, тесты, Docker и CI.

## Возможности

- Регистрация, вход и выход пользователя.
- JWT-авторизация через cookie.
- Роли пользователей: обычный пользователь и администратор.
- CRUD для отелей, номеров и удобств.
- Поиск доступных отелей и номеров по датам.
- Создание и отмена бронирований.
- Проверка доступности номера с учетом активных бронирований.
- Загрузка изображений и генерация уменьшенных копий.
- Health-check endpoints для приложения, PostgreSQL и Redis.
- Redis-кеширование read-only endpoints.

## Стек

- Python 3.12
- FastAPI
- SQLAlchemy 2.0 async
- Alembic
- PostgreSQL
- Redis
- Pydantic v2
- PyJWT, passlib, bcrypt
- Pytest, pytest-asyncio, HTTPX
- Ruff
- Docker, Docker Compose
- GitHub Actions

## Архитектура

Проект разделен на несколько слоев:

- `src/api` - роутеры FastAPI, зависимости, middleware.
- `src/services` - бизнес-логика приложения.
- `src/repos` - работа с базой данных.
- `src/models` - SQLAlchemy ORM-модели.
- `src/schemas` - Pydantic-схемы запросов и ответов.
- `src/migrations` - Alembic-миграции.
- `src/tasks` - фоновые задачи.
- `tests` - unit и integration tests.

Основная идея: API-слой не работает с БД напрямую, а вызывает сервисы. Сервисы используют репозитории через `DBManager`, который управляет сессией и транзакциями.

## Переменные окружения

В проекте используются отдельные env-файлы для разных режимов:

- `.env` - локальный запуск приложения.
- `.env.test` - запуск тестов.
- `.env.docker` - запуск через Docker Compose.
- `.env.example`, `.env.test.example`, `.env.docker.example` - шаблоны, которые лежат в репозитории.

Создать локальные env-файлы можно так:

Windows PowerShell:

```powershell
Copy-Item .env.example .env
Copy-Item .env.test.example .env.test
Copy-Item .env.docker.example .env.docker
```

Linux/macOS:

```bash
cp .env.example .env
cp .env.test.example .env.test
cp .env.docker.example .env.docker
```

## Локальный запуск

Создайте виртуальное окружение и установите зависимости:

Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Linux/macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Убедитесь, что PostgreSQL и Redis доступны с параметрами из `.env`, затем примените миграции:

```bash
alembic upgrade head
```

Запустите приложение:

```bash
uvicorn src.main:app --reload
```

Swagger UI будет доступен по адресу:

```text
http://localhost:8000/docs
```

## Запуск через Docker

Создайте `.env.docker` из шаблона:

Windows PowerShell:

```powershell
Copy-Item .env.docker.example .env.docker -Force
```

Linux/macOS:

```bash
cp .env.docker.example .env.docker
```

Запустите контейнеры:

```bash
docker compose up --build
```

Docker Compose поднимает:

- API-сервис;
- PostgreSQL;
- Redis.

API доступен по адресу:

```text
http://localhost:8888
```

Swagger UI:

```text
http://localhost:8888/docs
```

Контейнер API применяет Alembic-миграции перед стартом Uvicorn.

PostgreSQL доступен с хоста на `localhost:5433`:

```text
database=booking
user=postgres
password=postgres
```

Остановить контейнеры:

```bash
docker compose down
```

Остановить контейнеры и удалить volume с демо-БД:

```bash
docker compose down -v
```

## Демо-данные

После запуска Docker Compose можно заполнить базу демо-данными:

```bash
docker compose exec api python -m src.scripts.seed_demo
```

Для локального запуска без Docker:

```bash
python -m src.scripts.seed_demo
```

Пример сценария в Swagger:

1. Войти как администратор: `POST /auth/login`, `admin@mail.com / admin`.
2. Проверить справочники: `GET /facilities`, `GET /hotels`.
3. Зарегистрировать обычного пользователя: `POST /auth/register`.
4. Войти обычным пользователем: `POST /auth/login`.
5. Создать бронирование: `POST /bookings`.
6. Отменить бронирование: `PATCH /bookings/{booking_id}/cancel`.

## Health checks

Сервис предоставляет endpoints для проверки состояния:

- `GET /health` - приложение запущено.
- `GET /health/db` - доступность PostgreSQL.
- `GET /health/redis` - доступность Redis.

Docker Compose использует `/health` для healthcheck API-контейнера.

## Кеширование

Read-only endpoints, например `GET /hotels` и `GET /facilities`, используют кеш через `fastapi-cache2`.

В Docker-режиме кеш хранится в Redis. Если Redis недоступен при локальной разработке, приложение переключается на in-memory cache.

Посмотреть демо-ключи в Redis:

```bash
docker compose exec redis redis-cli keys "*"
```

## Тесты

Тесты используют `.env.test`. Для локального запуска нужен PostgreSQL:

```text
host=localhost
port=5432
database=test
user=postgres
password=change-me
```

Если тестовой базы нет, создайте ее вручную:

```sql
CREATE DATABASE test;
```

Запуск тестов:

```bash
pytest --collect-only -q
pytest -q
```

## Линтеры и форматирование

В проекте используется Ruff:

```bash
python -m ruff check .
python -m ruff format --check .
```

Автоисправление простых проблем:

```bash
python -m ruff check . --fix
python -m ruff format .
```

## Миграции

Alembic использует те же настройки подключения к БД, что и приложение.

Применить миграции:

```bash
alembic upgrade head
```

Создать новую миграцию:

```bash
alembic revision --autogenerate -m "migration message"
```

## CI

GitHub Actions запускается на `push` и `pull_request`.

CI-пайплайн выполняет:

1. Установку зависимостей.
2. Ruff lint и format check.
3. Компиляцию исходников.
4. Применение Alembic-миграций.
5. Pytest.
6. Проверку `docker compose config`.
7. Сборку Docker-образа.

Локально тот же набор проверок можно запустить так:

```bash
python -m ruff check .
python -m ruff format --check .
python -m compileall src tests
pytest -q
docker compose config
docker build -t hotel-booking-service:ci .
```

## Что демонстрирует проект

Проект показывает базовые навыки backend-разработки:

- проектирование REST API;
- разделение приложения на слои;
- работу с async SQLAlchemy;
- миграции БД через Alembic;
- авторизацию и роли;
- обработку ошибок;
- интеграционные тесты;
- Docker-инфраструктуру;
- CI-пайплайн для проверки качества кода.
