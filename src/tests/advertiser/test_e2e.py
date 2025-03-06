import pytest
from httpx import AsyncClient, ASGITransport
from src.main import app
from src.config import reset_db


@pytest.mark.asyncio
async def test_bulk():
    reset_db()

    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/advertisers/bulk", json=[{"advertiser_id": "321e4567-e89b-12d3-a456-426614174000", "name": "test"}])
        assert response.status_code == 201
        assert response.json() == [{"advertiser_id": "321e4567-e89b-12d3-a456-426614174000", "name": "test"}]

@pytest.mark.asyncio
async def test_get_advertiser_by_id():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/advertisers/321e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 200
        assert response.json() == {"advertiser_id": "321e4567-e89b-12d3-a456-426614174000", "name": "test"}

@pytest.mark.asyncio
async def test_ml_scores():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/clients/bulk", json=[
            {"client_id": "123e4567-e89b-12d3-a456-426614174000", "login": "test", "age": 25, "location": "Moscow",
             "gender": "Male"},
        ])
        response = await ac.post("/ml-scores", json={"client_id": "123e4567-e89b-12d3-a456-426614174000", "advertiser_id": "321e4567-e89b-12d3-a456-426614174000", "score": 5})
        assert response.status_code == 200
        assert response.json() == {"client_id": "123e4567-e89b-12d3-a456-426614174000",
                                   "advertiser_id": "321e4567-e89b-12d3-a456-426614174000", "score": 5}


@pytest.mark.asyncio
async def test_bulk_empty_list():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/advertisers/bulk", json=[])
        assert response.status_code == 201


@pytest.mark.asyncio
async def test_bulk_invalid_data():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/advertisers/bulk", json=[{"advertiser_id": "invalid", "name": "test"}])
        assert response.status_code == 422

        response = await ac.post("/advertisers/bulk", json=[{"advertiser_id": "321e4567-e89b-12d3-a456-426614174000"}])
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_get_nonexistent_advertiser():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/advertisers/00000000-0000-0000-0000-000000000000")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_invalid_uuid_format():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/advertisers/not-a-uuid")
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_ml_score_invalid_entities():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/ml-scores", json={
            "client_id": "00000000-0000-0000-0000-000000000000",
            "advertiser_id": "321e4567-e89b-12d3-a456-426614174000",
            "score": 5
        })
        assert response.status_code == 404

        response = await ac.post("/ml-scores", json={
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "advertiser_id": "00000000-0000-0000-0000-000000000000",
            "score": 5
        })
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_ml_score_validation():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/ml-scores", json={
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "advertiser_id": "321e4567-e89b-12d3-a456-426614174000",
            "score": 10
        })
        assert response.status_code == 200

        response = await ac.post("/ml-scores", json={
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "advertiser_id": "321e4567-e89b-12d3-a456-426614174000",
            "score": "high"
        })
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_ml_score_update():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post("/ml-scores", json={
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "advertiser_id": "321e4567-e89b-12d3-a456-426614174000",
            "score": 3
        })

        response = await ac.post("/ml-scores", json={
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "advertiser_id": "321e4567-e89b-12d3-a456-426614174000",
            "score": 5
        })
        assert response.status_code == 200
        assert response.json()["score"] == 5
