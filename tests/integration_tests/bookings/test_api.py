import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from src.main import app
from tests.conftest import get_db_null_pull


@pytest_asyncio.fixture(scope="module")
async def clear_booking_db():
    async for _db in get_db_null_pull():
        await _db.bookings.delete_all()
        await _db.commit()


async def clear_bookings():
    async for _db in get_db_null_pull():
        await _db.bookings.delete_all()
        await _db.commit()


async def register_and_login_user(email: str, password: str) -> AsyncClient:
    transport = ASGITransport(app=app)
    client = AsyncClient(transport=transport, base_url="http://test")
    response = await client.post("/auth/register", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    response = await client.post("/auth/login", json={"email": email, "password": password})
    assert response.status_code == 200, response.text
    return client


@pytest.mark.parametrize(
    "room_id, date_from, date_to, status_code",
    [
        (2, "2021-01-01", "2021-02-01", 200),
        (2, "2021-01-01", "2021-02-01", 200),
        (2, "2021-01-01", "2021-02-01", 200),
        (2, "2021-01-01", "2021-02-01", 409),
    ],
)
async def test_add_booking(room_id, date_from, date_to, status_code, auth_ac, db):
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == status_code
    if status_code == 200:
        assert isinstance(response.json(), dict)
        assert (response.json())["data"].get("user_id") == 1
        assert (response.json())["data"].get("status") == "active"


@pytest.mark.parametrize(
    "room_id, date_from, date_to, count_booking",
    [
        (2, "2021-01-01", "2021-02-01", 1),
        (2, "2021-01-01", "2021-02-01", 2),
        (2, "2021-01-01", "2021-02-01", 3),
    ],
)
async def test_add_and_get_my_bookings(
    room_id, date_from, date_to, count_booking, auth_ac, clear_booking_db
):
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": room_id,
            "date_from": date_from,
            "date_to": date_to,
        },
    )
    assert response.status_code == 200

    response = await auth_ac.get("/bookings/me")

    assert response.status_code == 200
    assert len(response.json()["data"]) == count_booking


async def test_booking_can_start_on_previous_checkout_date(auth_ac, clear_booking_db):
    first_response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-08-01",
            "date_to": "2026-08-10",
        },
    )
    assert first_response.status_code == 200

    second_response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-08-10",
            "date_to": "2026-08-12",
        },
    )

    assert second_response.status_code == 200


async def test_user_can_cancel_own_booking(auth_ac):
    await clear_bookings()
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-09-01",
            "date_to": "2026-09-05",
        },
    )
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]
    assert response.json()["data"]["status"] == "active"

    response = await auth_ac.patch(f"/bookings/{booking_id}/cancel")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == booking_id
    assert response.json()["data"]["status"] == "cancelled"

    response = await auth_ac.get("/bookings/me")

    assert response.status_code == 200
    bookings = response.json()["data"]
    assert any(booking["id"] == booking_id and booking["status"] == "cancelled" for booking in bookings)


async def test_cancel_booking_twice_returns_409(auth_ac):
    await clear_bookings()
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-09-06",
            "date_to": "2026-09-08",
        },
    )
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]
    assert (await auth_ac.patch(f"/bookings/{booking_id}/cancel")).status_code == 200

    response = await auth_ac.patch(f"/bookings/{booking_id}/cancel")

    assert response.status_code == 409


async def test_user_cannot_cancel_other_user_booking(auth_ac):
    await clear_bookings()
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-09-09",
            "date_to": "2026-09-11",
        },
    )
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]

    other_ac = await register_and_login_user("other-booking-user@example.com", "other-pass")
    try:
        response = await other_ac.patch(f"/bookings/{booking_id}/cancel")
    finally:
        await other_ac.aclose()

    assert response.status_code == 404


async def test_admin_can_cancel_any_booking_and_see_status(auth_ac, admin_ac):
    await clear_bookings()
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 2,
            "date_from": "2026-09-12",
            "date_to": "2026-09-14",
        },
    )
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]

    response = await admin_ac.patch(f"/bookings/{booking_id}/cancel")

    assert response.status_code == 200
    assert response.json()["data"]["status"] == "cancelled"

    response = await admin_ac.get("/bookings")

    assert response.status_code == 200
    assert any(booking["id"] == booking_id and booking["status"] == "cancelled" for booking in response.json()["data"])


async def test_cancelled_booking_does_not_block_room(auth_ac):
    await clear_bookings()
    booking_payload = {
        "room_id": 2,
        "date_from": "2026-09-15",
        "date_to": "2026-09-20",
    }
    response = await auth_ac.post("/bookings", json=booking_payload)
    assert response.status_code == 200
    booking_id = response.json()["data"]["id"]
    assert (await auth_ac.patch(f"/bookings/{booking_id}/cancel")).status_code == 200

    for _ in range(3):
        response = await auth_ac.post("/bookings", json=booking_payload)
        assert response.status_code == 200

    response = await auth_ac.post("/bookings", json=booking_payload)

    assert response.status_code == 409
