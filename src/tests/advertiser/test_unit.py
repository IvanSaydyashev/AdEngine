import unittest
import uuid

from fastapi.testclient import TestClient
from src.main import app
from src.config import reset_db


class TestAdvertiserEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()
        self.client = TestClient(app)

        self.advertiser_id = "133e4567-e89b-12d3-a456-426614174000"
        self.client_id = "123e4567-e89b-12d3-a456-426614174000"

        self.client.post("/clients/bulk", json=[
            {"client_id": self.client_id, "login": "client1",
             "age": 20, "gender": "MALE", "location": "USA"}])

    def test_get_advertiser_by_id(self):
        self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": self.advertiser_id, "name": "advertiser1"}])

        response = self.client.get("/advertisers/invalid_uuid")

        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/advertisers/{self.advertiser_id}")

        self.assertEqual(response.status_code, 200)

    def test_bulk(self):
        response = self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": self.advertiser_id, "name": "advertiser1"}])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), [
            {"advertiser_id": self.advertiser_id, "name": "advertiser1"}])

        response = self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": self.advertiser_id, "name": "updated_advertiser1"}
        ])

        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.json(), [
            {"advertiser_id": self.advertiser_id, "name": "updated_advertiser1"}
        ])

    def test_bulk_invalid_data(self):
        client = TestClient(app)
        response = client.post("/advertisers/bulk", json=[
            {"advertiser_id": "invalid_advertiser_id", "name": "advertiser1"}])

        self.assertEqual(response.status_code, 422)

    def test_bulk_empty_data(self):
        response = self.client.post("/advertisers/bulk", json=[])

        self.assertEqual(response.status_code, 201)

    def test_ml_scores(self):
        self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": self.advertiser_id, "name": "advertiser1"}])

        response = self.client.post("/ml-scores", json={
            "client_id": self.client_id,
            "advertiser_id": self.advertiser_id,
            "score": 5
        })
        self.assertEqual(response.status_code, 200)

    def test_invalid_ml_scores(self):
        response = self.client.post("/ml-scores", json={
            "client_id": self.client_id,
            "advertiser_id": self.advertiser_id,
            "score": 0.5
        })

        self.assertEqual(response.status_code, 422)
