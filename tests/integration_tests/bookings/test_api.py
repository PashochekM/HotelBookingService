import pytest
import pytest_asyncio

from tests.conftest import get_db_null_pull


@pytest_asyncio.fixture(scope="module")
async def clear_booking_db():
    async for _db in get_db_null_pull():
        await _db.bookings.delete_all()
        await _db.commit()


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
