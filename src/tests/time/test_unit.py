import unittest
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)


class TestTimeEndpoints(unittest.TestCase):
    def test_set_positive_day_success(self):
        response = client.post("/time/advance", json={"current_date": 9999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"current_date": 9999})

    def test_negative_day_failure(self):
        response = client.post("/time/advance", json={"current_date": -1})
        self.assertEqual(response.status_code, 422)

    def test_non_integer_failure(self):
        test_cases = [
            {"current_date": "not_a_number"},
            {"current_date": 3.14},
            {"current_date": None},
            {"current_date": True},
            {}
        ]

        for case in test_cases:
            response = client.post("/time/advance", json=case)
            self.assertEqual(response.status_code, 422)