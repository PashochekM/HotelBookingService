from httpx import ASGITransport, AsyncClient

from src.main import app


async def raise_unhandled_error():
    raise RuntimeError("test unhandled error")


if not any(getattr(route, "path", None) == "/__test__/unhandled" for route in app.routes):
    app.add_api_route("/__test__/unhandled", raise_unhandled_error, methods=["GET"])


async def test_request_id_header_is_generated(ac):
    response = await ac.get("/hotels/999999")

    assert response.status_code == 404
    assert response.headers["x-request-id"]


async def test_request_id_header_is_preserved(ac):
    response = await ac.get("/hotels/999999", headers={"X-Request-ID": "test-request-id"})

    assert response.status_code == 404
    assert response.headers["x-request-id"] == "test-request-id"


async def test_unhandled_exception_returns_500():
    transport = ASGITransport(app=app, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/__test__/unhandled")

    assert response.status_code == 500
    assert response.json() == {"detail": "Internal server error"}
    assert response.headers["x-request-id"]
