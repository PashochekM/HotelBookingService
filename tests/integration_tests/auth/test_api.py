import pytest


@pytest.mark.parametrize(
    "email, password", [("cool_man@gay.com", "gaaay"), ("bad_man@gay.com", "pedic")]
)
async def test_register_login_logout(email, password, setup_hotels_rooms_data, ac):
    response = await ac.post(
        "/auth/register",
        json={
            "email": email,
            "password": password,
        },
    )
    assert response.status_code == 200, response.text
    assert (response.json()).get("status") == "ok"

    response = await ac.post(
        "/auth/login",
        json={
            "email": "s" + email,
            "password": password,
        },
    )

    assert response.status_code == 401

    response = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password + "s",
        },
    )

    assert response.status_code == 401

    response = await ac.post(
        "/auth/login",
        json={
            "email": email,
            "password": password,
        },
    )

    assert response.status_code == 200, response.text
    assert "access_token" in ac.cookies
    assert ac.cookies["access_token"] == response.json()["access_token"]

    response = await ac.get("/auth/me")
    assert response.status_code == 200
    assert response.json()["email"] == email

    response = await ac.post("/auth/logout")
    assert "access_token" not in ac.cookies
