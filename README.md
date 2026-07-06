# Hotel Booking Service

FastAPI service for hotel rooms, facilities, bookings, image uploads, and user authentication.

## Local Environment

The project uses separate env files for each runtime:

- `.env` - local application run. This is read by `src.config.Settings`.
- `.env.test` - local pytest run. This is loaded by `pytest-dotenv`.
- `.env.docker` - Docker Compose run. This is used by the API container.
- `.env.example`, `.env.test.example`, `.env.docker.example` - committed templates.

Create local files from templates before running the app:

```powershell
Copy-Item .env.example .env
Copy-Item .env.test.example .env.test
Copy-Item .env.docker.example .env.docker
```

## Install

Use a virtual environment instead of the global Python installation:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## Run Locally

Make sure PostgreSQL and Redis match `.env`, then run:

```powershell
uvicorn src.main:app --reload
```

## Run With Docker

Create `.env.docker` from `.env.docker.example`, then run:

```powershell
Copy-Item .env.docker.example .env.docker -Force
docker compose up --build
```

The API is exposed on:

```text
http://localhost:8888
```

Swagger UI:

```text
http://localhost:8888/docs
```

The compose stack starts the API, PostgreSQL, and Redis. The API container applies Alembic migrations before starting Uvicorn.

PostgreSQL is also exposed on `localhost:5433` for tools such as DataGrip or PyCharm Database. Demo credentials match `.env.docker.example`:

```text
database=booking
user=postgres
password=postgres
```

Stop the stack:

```powershell
docker compose down
```

Stop the stack and remove the demo database volume:

```powershell
docker compose down -v
```

## Health Checks

The API exposes `GET /health` for liveness, `GET /health/db` for PostgreSQL, and `GET /health/redis` for Redis. Docker Compose marks the API container healthy through `/health`.

## Demo Flow

After `docker compose up --build`, open Swagger at `http://localhost:8888/docs` and run:

1. `POST /auth/register` with `admin@mail.com`.
2. `POST /auth/login`.
3. Promote the user to admin in the Docker database:

```sql
UPDATE users SET role = 'admin' WHERE email = 'admin@mail.com';
```

4. Create a hotel with `POST /hotels`.
5. Create a room with `POST /hotels/{hotel_id}/rooms`.
6. Create a booking with `POST /bookings`.
7. Cancel the booking with `PATCH /bookings/{booking_id}/cancel`.

## Tests

Tests use `.env.test`. A local PostgreSQL instance must be available with:

```text
host=localhost
port=5432
database=test
user=postgres
password=change-me
```

Run:

```powershell
pytest --collect-only -q
pytest -q
```

If the database does not exist, create it manually:

```sql
CREATE DATABASE test;
```

## Migrations

Alembic uses the same settings object as the application. Run migrations against the active env:

```powershell
alembic upgrade head
```

## CI

GitHub Actions runs Docker Compose config validation, compile checks, Alembic migrations, and pytest against PostgreSQL 16 on push and pull requests.
