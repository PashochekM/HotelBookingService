import base64

import pytest

from src.services.images import IMAGES_DIR

TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR4nGP4//8/AwAI/AL+p5qgoAAAAABJRU5ErkJggg=="
)


ADMIN_ENDPOINT_CASES = [
    ("post", "/hotels", {"json": {"title": "Access Hotel", "location": "Nowhere"}}),
    ("post", "/facilities", {"json": {"title": "Access Facility"}}),
    ("post", "/images/images", {"files": {"file": ("tiny.png", TINY_PNG, "image/png")}}),
    ("get", "/bookings", {}),
]


@pytest.mark.parametrize("method,path,kwargs", ADMIN_ENDPOINT_CASES)
async def test_anonymous_admin_endpoints_return_401(ac, method, path, kwargs):
    response = await getattr(ac, method)(path, **kwargs)

    assert response.status_code == 401


@pytest.mark.parametrize("method,path,kwargs", ADMIN_ENDPOINT_CASES)
async def test_user_admin_endpoints_return_403(auth_ac, method, path, kwargs):
    response = await getattr(auth_ac, method)(path, **kwargs)

    assert response.status_code == 403


async def test_admin_can_manage_hotels_rooms_facilities_and_images(admin_ac):
    bookings_response = await admin_ac.get("/bookings")
    assert bookings_response.status_code == 200, bookings_response.text
    assert isinstance(bookings_response.json()["data"], list)

    facility_response = await admin_ac.post("/facilities", json={"title": "Admin Access Facility"})
    assert facility_response.status_code == 200, facility_response.text

    hotel_response = await admin_ac.post(
        "/hotels",
        json={
            "title": "Admin Access Hotel",
            "location": "Admin City",
        },
    )
    assert hotel_response.status_code == 200, hotel_response.text
    hotel_id = hotel_response.json()["data"]["id"]

    update_hotel_response = await admin_ac.put(
        f"/hotels/{hotel_id}",
        json={
            "title": "Admin Access Hotel Updated",
            "location": "Admin City",
        },
    )
    assert update_hotel_response.status_code == 200, update_hotel_response.text

    patch_hotel_response = await admin_ac.patch(f"/hotels/{hotel_id}", json={"location": "Admin District"})
    assert patch_hotel_response.status_code == 200, patch_hotel_response.text

    room_response = await admin_ac.post(
        f"/hotels/{hotel_id}/rooms",
        json={
            "title": "Admin Access Room",
            "description": "Room created by admin access test",
            "price": 1500.0,
            "quantity": 2,
            "facilities": [],
        },
    )
    assert room_response.status_code == 200, room_response.text
    room_id = room_response.json()["data"]["id"]

    update_room_response = await admin_ac.put(
        f"/hotels/{hotel_id}/rooms/{room_id}",
        json={
            "title": "Admin Access Room Updated",
            "description": "Room updated by admin access test",
            "price": 1700.0,
            "quantity": 3,
            "facilities": [],
        },
    )
    assert update_room_response.status_code == 200, update_room_response.text

    patch_room_response = await admin_ac.patch(f"/hotels/{hotel_id}/rooms/{room_id}", json={"price": 1800.0})
    assert patch_room_response.status_code == 200, patch_room_response.text

    image_response = await admin_ac.post(
        "/images/images",
        files={"file": ("tiny.png", TINY_PNG, "image/png")},
    )
    assert image_response.status_code == 200, image_response.text
    uploaded_filename = image_response.json()["data"]["filename"]
    (IMAGES_DIR / uploaded_filename).unlink(missing_ok=True)

    delete_room_response = await admin_ac.delete(f"/hotels/{hotel_id}/rooms/{room_id}")
    assert delete_room_response.status_code == 200, delete_room_response.text

    delete_hotel_response = await admin_ac.delete(f"/hotels/{hotel_id}")
    assert delete_hotel_response.status_code == 200, delete_hotel_response.text
