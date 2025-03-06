import unittest
from fastapi.testclient import TestClient

from src.main import app
from src.config import reset_db
from fastapi import status


class TestClientEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()
        self.client = TestClient(app)
        self.valid_client_id = "333e4567-e89b-12d3-a456-426614174000"
        self.undefined_client_id = "123e4567-e89b-12d3-a456-426614174000"
        self.base_client_data = {
            "client_id": self.valid_client_id,
            "login": "user1",
            "age": 25,
            "location": "Moscow",
            "gender": "Male"
        }

    def test_get_client_by_id(self):
        self.client.post("/clients/bulk", json=[self.base_client_data])

        response = self.client.get(f"/clients/{self.valid_client_id}")
        self.assertEqual(response.status_code, 200)

        response = self.client.get("/clients/invalid_uuid")
        self.assertEqual(response.status_code, 422)

        response = self.client.get(f"/clients/{self.undefined_client_id}")
        self.assertEqual(response.status_code, 404)

    def test_bulk_create_clients(self):
        response = self.client.post("/clients/bulk", json=[self.base_client_data])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        updated_data = {
            **self.base_client_data,
            "login": "new_login",
            "age": 30,
            "gender": "Female"
        }
        response = self.client.post("/clients/bulk", json=[updated_data])
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        self.assertEqual(response.json()[0]["login"], "new_login")
        self.assertEqual(response.json()[0]["age"], 30)
        self.assertEqual(response.json()[0]["gender"], "FEMALE")

    def test_partial_update(self):
        initial_data = {
            "client_id": self.valid_client_id,
            "login": "original_login",
            "age": 25,
            "location": "Paris",
            "gender": "Male"
        }
        self.client.post("/clients/bulk", json=[initial_data])

        partial_data = {
            "client_id": self.valid_client_id,
            "login": "updated_login",
            "location": "Paris",
            "age": 30,
            "gender": "Male"
        }
        response = self.client.post("/clients/bulk", json=[partial_data])
        self.assertEqual(response.status_code, 201)

        response_data = response.json()[0]
        self.assertEqual(response_data["location"], "Paris")
        self.assertEqual(response_data["gender"], "MALE")

    def test_bulk_input_validation(self):
        invalid_data = {**self.base_client_data, "age": "twenty-five"}
        response = self.client.post("/clients/bulk", json=[invalid_data])
        self.assertEqual(response.status_code, 422)

        invalid_data = {**self.base_client_data, "gender": "Invalid"}
        response = self.client.post("/clients/bulk", json=[invalid_data])
        self.assertEqual(response.status_code, 422)

        invalid_data = {**self.base_client_data, "client_id": "invalid"}
        response = self.client.post("/clients/bulk", json=[invalid_data])
        self.assertEqual(response.status_code, 422)

        invalid_data = {**self.base_client_data}
        del invalid_data["login"]
        response = self.client.post("/clients/bulk", json=[invalid_data])
        self.assertEqual(response.status_code, 422)

    def test_edge_cases(self):
        data = {**self.base_client_data, "age": 0}
        response = self.client.post("/clients/bulk", json=[data])
        self.assertEqual(response.status_code, 201)

        data = {**self.base_client_data, "age": 150}
        response = self.client.post("/clients/bulk", json=[data])
        self.assertEqual(response.status_code, 422)

        data = {**self.base_client_data, "location": "A" * 256}
        response = self.client.post("/clients/bulk", json=[data])
        self.assertEqual(response.status_code, 422)

    def test_empty_and_null_values(self):
        response = self.client.post("/clients/bulk", json=[])
        self.assertEqual(response.status_code, 201)

        data = {**self.base_client_data, "location": None}
        response = self.client.post("/clients/bulk", json=[data])
        self.assertEqual(response.status_code, 422)

    def test_unsupported_methods(self):
        response = self.client.put("/clients/bulk", json=[self.base_client_data])
        self.assertEqual(response.status_code, 405)

        response = self.client.delete(f"/clients/{self.valid_client_id}")
        self.assertEqual(response.status_code, 405)

