from datetime import timedelta

from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.auth import AuthService


async def get_me_with_token(token: str):
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        client.cookies.set("access_token", token)
        return await client.get("/auth/me")


async def test_register_duplicate_email_returns_409(ac):
    response = await ac.post(
        "/auth/register",
        json={
            "email": "man@woman.com",
            "password": "12345",
        },
    )

    assert response.status_code == 409


async def test_bad_token_returns_401():
    response = await get_me_with_token("bad-token")

    assert response.status_code == 401


async def test_expired_token_returns_401():
    expired_token = AuthService.create_access_token({"id": 1}, expires_delta=timedelta(seconds=-1))
    response = await get_me_with_token(expired_token)

    assert response.status_code == 401


async def test_get_missing_hotel_returns_404(ac):
    response = await ac.get("/hotels/999999")

    assert response.status_code == 404


async def test_get_hotels_invalid_dates_returns_422(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2026-08-10",
            "date_to": "2026-08-01",
        },
    )

    assert response.status_code == 422


async def test_get_rooms_for_missing_hotel_returns_404(ac):
    response = await ac.get(
        "/hotels/999999/rooms",
        params={
            "date_from": "2026-08-01",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 404


async def test_create_room_for_missing_hotel_returns_404(ac):
    response = await ac.post(
        "/hotels/999999/rooms",
        json={
            "title": "Nowhere",
            "price": 1000,
            "quantity": 1,
        },
    )

    assert response.status_code == 404


async def test_create_room_with_missing_facility_returns_404(ac):
    response = await ac.post(
        "/hotels/1/rooms",
        json={
            "title": "Room with unknown facility",
            "price": 1000,
            "quantity": 1,
            "facilities": [999999],
        },
    )

    assert response.status_code == 404


async def test_patch_room_in_wrong_hotel_does_not_update_room(ac):
    before_response = await ac.get("/hotels/1/rooms/1")
    assert before_response.status_code == 200
    old_title = before_response.json()["data"]["title"]

    response = await ac.patch("/hotels/2/rooms/1", json={"title": "Wrong hotel edit"})

    after_response = await ac.get("/hotels/1/rooms/1")
    assert response.status_code == 404
    assert after_response.status_code == 200
    assert after_response.json()["data"]["title"] == old_title


async def test_booking_with_invalid_dates_returns_422(auth_ac):
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 1,
            "date_from": "2026-08-10",
            "date_to": "2026-08-01",
        },
    )

    assert response.status_code == 422


async def test_booking_missing_room_returns_404(auth_ac):
    response = await auth_ac.post(
        "/bookings",
        json={
            "room_id": 999999,
            "date_from": "2026-08-01",
            "date_to": "2026-08-10",
        },
    )

    assert response.status_code == 404


async def test_upload_invalid_image_returns_400(ac):
    response = await ac.post(
        "/images/images",
        files={"file": ("bad.txt", b"not an image", "text/plain")},
    )

    assert response.status_code == 400
