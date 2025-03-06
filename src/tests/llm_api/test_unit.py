import unittest
from fastapi.testclient import TestClient
from src.main import app


class TestLLMActionEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        self.client = TestClient(app)

    def test_llm_validate_accept(self):
        request_data = {
            "ad_text": "This is a valid ad text."
        }
        response = self.client.post(
            "/llm-action/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "accept")

    def test_llm_validate_reject(self):
        request_data = {
            "ad_text": "We are fraudsters."
        }
        response = self.client.post(
            "/llm-action/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["status"], "reject")

    def test_llm_validate_invalid_data(self):
        request_data = {
            "invalid_key": "Invalid data"
        }
        response = self.client.post(
            "/llm-action/validate",
            json=request_data
        )
        self.assertEqual(response.status_code, 422)

    def test_llm_generate_success(self):
        request_data = {
            "targeting": {"age_from": 18, "age_to": 24, "gender": "MALE"},
            "ad_name": "Summer Sale",
            "advertiser_name": "Fashion Advertiser",
        }
        response = self.client.post(
            "/llm-action/generate",
            json=request_data
        )
        self.assertEqual(response.status_code, 200)

    def test_llm_generate_invalid_data(self):
        request_data = {
            "invalid_key": "Invalid data"
        }
        response = self.client.post(
            "/llm-action/generate",
            json=request_data
        )
        self.assertEqual(response.status_code, 422)