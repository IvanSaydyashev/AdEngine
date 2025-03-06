import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
import redis.asyncio as redis
from src.config import settings
@pytest.mark.asyncio
async def test_valid_day():
    r = redis.Redis.from_url(settings.REDIS_URL)
    await r.flushall()
    await r.set("current_date", "0")
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/time/advance",
            json={"current_date": 333}
        )
        assert response.status_code == 200

@pytest.mark.asyncio
async def test_invalid_inputs():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post(
            "/time/advance",
            json={"current_date": -1}
        )
        assert response.status_code == 422

        response = await ac.post(
            "/time/advance",
            json={"current_date": "invalid"}
        )
        assert response.status_code == 422
