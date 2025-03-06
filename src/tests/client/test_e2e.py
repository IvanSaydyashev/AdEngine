import pytest
import uuid
from httpx import AsyncClient, ASGITransport, Response
from src.main import app
from src.config import reset_db


@pytest.mark.asyncio
async def test_basic_client_lifecycle():
    reset_db()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.get("/clients/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 404

        # Create client
        client_data = {
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "login": "test_user",
            "age": 25,
            "location": "Moscow",
            "gender": "Male"
        }
        response = await ac.post("/clients/bulk", json=[client_data])
        assert response.status_code == 201
        assert response.json()[0]["gender"] == "MALE"

        response = await ac.get("/clients/123e4567-e89b-12d3-a456-426614174000")
        assert response.status_code == 200
        assert response.json()["login"] == "test_user"

        updated_data = {**client_data, "login": "updated_user", "age": 30}
        response = await ac.post("/clients/bulk", json=[updated_data])
        assert response.status_code == 201

        response = await ac.get("/clients/123e4567-e89b-12d3-a456-426614174000")
        assert response.json()["login"] == "updated_user"
        assert response.json()["age"] == 30


@pytest.mark.asyncio
async def test_bulk_operations():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/clients/bulk", json=[])
        assert response.status_code == 201

        clients = [
            {
                "client_id": str(uuid.uuid4()),
                "login": f"client_{i}",
                "age": 20 + i,
                "location": "City",
                "gender": "Male"
            }
            for i in range(5)
        ]
        response = await ac.post("/clients/bulk", json=clients)
        assert response.status_code == 201
        assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_validation_scenarios():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/clients/bulk", json=[{
            "client_id": "invalid-uuid",
            "login": "test",
            "age": 25,
            "gender": "Male"
        }])
        assert response.status_code == 422

        response = await ac.post("/clients/bulk", json=[{
            "client_id": "123e4567-e89b-12d3-a456-426614174000",
            "age": 25,
            "gender": "Male"
        }])
        assert response.status_code == 422

        for age in [-10, 151]:
            response = await ac.post("/clients/bulk", json=[{
                "client_id": str(uuid.uuid4()),
                "login": "test",
                "age": age,
                "gender": "Male"
            }])
            assert response.status_code == 422

        for gender in ["Other", "unknown", 123]:
            response = await ac.post("/clients/bulk", json=[{
                "client_id": str(uuid.uuid4()),
                "login": "test",
                "age": 25,
                "gender": gender
            }])
            assert response.status_code == 422


@pytest.mark.asyncio
async def test_edge_cases():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        response = await ac.post("/clients/bulk", json=[{
            "client_id": str(uuid.uuid4()),
            "login": "a" * 256,
            "age": 25,
            "location": "b" * 1025,
            "gender": "Female"
        }])
        assert response.status_code == 422

        response = await ac.post("/clients/bulk", json=[{
            "client_id": str(uuid.uuid4()),
            "login": "okey",
            "age": 0,
            "location": "",
            "gender": "FEMALE"
        }])
        assert response.status_code == 201
