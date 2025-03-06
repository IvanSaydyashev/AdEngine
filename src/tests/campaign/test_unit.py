import unittest
import uuid

import httpx
from fastapi.testclient import TestClient
from src.main import app
from src.config import reset_db


class TestCampaignEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()
        self.client = TestClient(app)
        self.advertiser_id = uuid.UUID("133e4567-e89b-12d3-a456-426614174000")

        self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": str(self.advertiser_id), "name": "advertiser12"}])

        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 500,
                "end_date": 999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 201)
        self.campaign_id = uuid.UUID(response.json()["campaign_id"])

    def test_invalid_generate_option(self):
        for option in ["123", None]:
            response = self.client.post(
                f"/advertisers/{self.advertiser_id}/campaigns",
                params={"isGenerate": f"{option}"},
                json={
                    "ad_title": "Test Ad",
                    "ad_text": "Test text",
                    "impressions_limit": 1000,
                    "clicks_limit": 100,
                    "cost_per_impression": 0.5,
                    "cost_per_click": 1.0,
                    "start_date": 500,
                    "end_date": 999,
                    "targeting": {}
                }
            )
            self.assertEqual(response.status_code, 422)

    def test_get_campaigns(self):
        response = self.client.get(f"/advertisers/{self.advertiser_id}/campaigns")
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.json(), list)

    def test_get_campaign_by_id(self):
        response = self.client.get(f"/advertisers/{self.advertiser_id}/campaigns/{self.campaign_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["campaign_id"], str(self.campaign_id))

    def test_update_campaign(self):
        response = self.client.put(
            f"/advertisers/{self.advertiser_id}/campaigns/{self.campaign_id}",
            json={
                "ad_title": "Updated Ad",
                "ad_text": "Updated text",
                "cost_per_impression": 0.6,
                "cost_per_click": 1.2,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["ad_title"], "Updated Ad")

    def test_delete_advertiser_campaign(self):
        response = self.client.delete(f"/advertisers/{self.advertiser_id}/campaigns/{self.campaign_id}")
        self.assertEqual(response.status_code, 204)

    def test_invalid_create_campaign(self):
        invalid_uuid = str(uuid.uuid4())
        response = self.client.post(
            f"/advertisers/{invalid_uuid}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 0,
                "end_date": 999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 404)

    def test_valid_create_campaign_generate(self):
        timeout = httpx.Timeout(20.0, read=None)
        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": True},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 0,
                "end_date": 999,
                "targeting": {}
            },
            timeout=timeout
        )
        print(response.content)
        self.assertEqual(response.status_code, 201)

    def test_invalid_advertiser_id_format(self):
        response = self.client.post(
            f"/advertisers/123/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 500,
                "end_date": 999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_create_campaign_missing_fields(self):
        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 500,
                "end_date": 999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_create_campaign_invalid_data_types(self):
        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": "1000",
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 500,
                "end_date": 999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_validate_gender_valid_input(self):
        valid_genders = ["MALE", "FEMALE", "ALL"]
        for gender in valid_genders:
            response = self.client.post(
                f"/advertisers/{self.advertiser_id}/campaigns",
                params={"isGenerate": False},
                json={
                    "ad_title": "Test Ad",
                    "ad_text": "Test text",
                    "impressions_limit": 1000,
                    "clicks_limit": 100,
                    "cost_per_impression": 0.5,
                    "cost_per_click": 1.0,
                    "start_date": 500,
                    "end_date": 999,
                    "targeting": {
                        "gender": f"{gender}"
                    }
                }
            )
            self.assertEqual(response.status_code, 201)

    def test_validate_gender_invalid_input(self):
        invalid_genders = [None, "UNKNOWN", "ALIEN"]
        for gender in invalid_genders:
            response = self.client.post(
                f"/advertisers/{self.advertiser_id}/campaigns",
                params={"isGenerate": False},
                json={
                    "ad_title": "Test Ad",
                    "ad_text": "Test text",
                    "impressions_limit": "1000",
                    "clicks_limit": 100,
                    "cost_per_impression": 0.5,
                    "cost_per_click": 1.0,
                    "start_date": 500,
                    "end_date": 999,
                    "targeting": {
                        "gender": gender
                    }
                }
            )
            self.assertEqual(response.status_code, 422)

    def test_create_campaign_invalid_date_range(self):
        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 999,
                "end_date": 500,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 422)

    def test_campaign_not_found(self):
        response = self.client.get(f"/advertisers/{self.advertiser_id}/campaigns/00000000-0000-0000-0000-000000000000")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Campaign not found")

        different_advertiser_id = uuid.UUID("233e4567-e89b-12d3-a456-426614174001")
        response = self.client.get(f"/advertisers/{different_advertiser_id}/campaigns/{self.campaign_id}")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Campaign not found")

    def test_campaign_already_started(self):
        response = self.client.post(
            f"/advertisers/{self.advertiser_id}/campaigns",
            params={"isGenerate": False},
            json={
                "ad_title": "Test Ad",
                "ad_text": "Test text",
                "impressions_limit": 1000,
                "clicks_limit": 100,
                "cost_per_impression": 0.5,
                "cost_per_click": 1.0,
                "start_date": 0,
                "end_date": 999999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 201)
        campaign_id = response.json()["campaign_id"]

        response = self.client.put(
            f"/advertisers/{self.advertiser_id}/campaigns/{campaign_id}",
            json={
                "ad_title": "Updated Ad",
                "ad_text": "Updated text",
                "cost_per_impression": 0.6,
                "cost_per_click": 1.2,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json()["detail"], "Campaign is already started")
