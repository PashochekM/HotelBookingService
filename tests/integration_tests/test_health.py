from src.exceptions import InfrastructureError


async def test_health_returns_ok(ac):
    response = await ac.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


async def test_health_db_returns_ok(ac):
    response = await ac.get("/health/db")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "database": "ok"}


async def test_health_redis_returns_ok_when_ping_succeeds(ac, monkeypatch):
    async def ping():
        return None

    monkeypatch.setattr("src.api.health.redis_manager.ping", ping)

    response = await ac.get("/health/redis")

    assert response.status_code == 200
    assert response.json() == {"status": "ok", "redis": "ok"}


async def test_health_redis_returns_503_when_ping_fails(ac, monkeypatch):
    async def ping():
        raise InfrastructureError("Redis is unavailable")

    monkeypatch.setattr("src.api.health.redis_manager.ping", ping)

    response = await ac.get("/health/redis")

    assert response.status_code == 503
    assert response.json() == {"status": "error", "detail": "Redis is unavailable"}
