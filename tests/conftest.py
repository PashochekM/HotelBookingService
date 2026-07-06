# ruff: noqa: E402
import json
from pathlib import Path
from unittest import mock

mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()

import pytest_asyncio
from httpx import AsyncClient, ASGITransport

from src.api.dependencies import get_db
from src.config import settings
from src.db import Base, engine_null_pool, async_session_maker_null_pool
from src.main import app
from src.models import *  # noqa
from src.schemas.users import UserAdd
from src.services.auth import AuthService
from src.utils.db_manager import DBManager

TESTS_DIR = Path(__file__).resolve().parent
USER_EMAIL = "man@woman.com"
USER_PASSWORD = "12345"
ADMIN_EMAIL = "admin@example.com"
ADMIN_PASSWORD = "admin-pass"


@pytest_asyncio.fixture(scope="session", autouse=True)
async def check_test_mode():
    assert settings.MODE == "TEST"


@pytest_asyncio.fixture()
async def db():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


async def get_db_null_pull():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


app.dependency_overrides[get_db] = get_db_null_pull


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_database(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest_asyncio.fixture(scope="session", autouse=True)
async def setup_hotels_rooms_data(setup_database, admin_ac):
    with open(TESTS_DIR / "mock_hotels.json", "r", encoding="utf-8") as f:
        hotel_data = json.load(f)

    with open(TESTS_DIR / "mock_rooms.json", "r", encoding="utf-8") as f:
        room_data = json.load(f)

    for hotel in hotel_data:
        response = await admin_ac.post("/hotels", json=hotel)
        assert response.status_code == 200, response.text

    for room in room_data:
        hotel_id = room["hotel_id"]
        room_payload = {k: v for k, v in room.items() if k != "hotel_id"}
        response = await admin_ac.post(f"/hotels/{hotel_id}/rooms", json=room_payload)
        assert response.status_code == 200, response.text


@pytest_asyncio.fixture(scope="session")
async def ac():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
async def register_user(setup_database, ac):
    response = await ac.post("/auth/register", json={"email": USER_EMAIL, "password": USER_PASSWORD})
    assert response.status_code == 200, response.text


@pytest_asyncio.fixture(scope="session")
async def register_admin(register_user):
    admin_data = UserAdd(
        email=ADMIN_EMAIL,
        hashed_password=AuthService.hash_password(ADMIN_PASSWORD),
        role="admin",
    )
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        await db.users.add_one(admin_data)
        await db.commit()


@pytest_asyncio.fixture(scope="session")
async def auth_ac(register_user):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/login", json={"email": USER_EMAIL, "password": USER_PASSWORD})
        assert response.status_code == 200, response.text
        assert "access_token" in client.cookies

        yield client


@pytest_asyncio.fixture(scope="session")
async def admin_ac(register_admin):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.post("/auth/login", json={"email": ADMIN_EMAIL, "password": ADMIN_PASSWORD})
        assert response.status_code == 200, response.text
        assert "access_token" in client.cookies

        yield client
