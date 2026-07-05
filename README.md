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
docker compose up --build
```

The API is exposed on `http://localhost:8888`.

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
