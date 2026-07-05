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
from src.utils.db_manager import DBManager

TESTS_DIR = Path(__file__).resolve().parent


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
async def setup_hotels_rooms_data(setup_database):
    with open(TESTS_DIR / "mock_hotels.json", "r", encoding="utf-8") as f:
        hotel_data = json.load(f)

    with open(TESTS_DIR / "mock_rooms.json", "r", encoding="utf-8") as f:
        room_data = json.load(f)

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        for hotel in hotel_data:
            response = await ac.post("/hotels", json=hotel)
            assert response.status_code == 200, response.text

        for room in room_data:
            hotel_id = room["hotel_id"]
            room_payload = {k: v for k, v in room.items() if k != "hotel_id"}
            response = await ac.post(f"/hotels/{hotel_id}/rooms", json=room_payload)
            assert response.status_code == 200, response.text


@pytest_asyncio.fixture(scope="session")
async def ac():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest_asyncio.fixture(scope="session", autouse=True)
async def register_user(setup_hotels_rooms_data, ac):
    response = await ac.post(
        "/auth/register", json={"email": "man@woman.com", "password": "12345"}
    )
    assert response.status_code == 200, response.text


@pytest_asyncio.fixture(scope="session")
async def auth_ac(register_user, ac):
    response = await ac.post(
        "/auth/login", json={"email": "man@woman.com", "password": "12345"}
    )
    assert response.status_code == 200, response.text
    assert "access_token" in ac.cookies

    yield ac
