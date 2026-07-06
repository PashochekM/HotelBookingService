from src.schemas.facilities import FacilityAdd


async def test_create_and_get_facilities(ac, admin_ac):
    facility = FacilityAdd(
        title="Wi-fi",
    )
    response = await admin_ac.post("/facilities", json=facility.model_dump())

    assert response.status_code == 200
    data = response.json()["data"]

    response = await ac.get("/facilities")

    assert data in response.json()["data"]
