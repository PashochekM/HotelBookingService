async def test_get_hotels(ac):
    response = await ac.get(
        "/hotels",
        params={
            "date_from": "2021-01-01",
            "date_to": "2021-12-31",
        },
    )
    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)


async def test_get_hotel(ac):
    response = await ac.get("/hotels/1")

    assert response.status_code == 200
    assert response.json()["data"]["id"] == 1


async def test_get_hotel_rooms(ac):
    response = await ac.get(
        "/hotels/1/rooms",
        params={
            "date_from": "2021-01-01",
            "date_to": "2021-12-31",
        },
    )

    assert response.status_code == 200
    assert isinstance(response.json()["data"], list)
