import unittest
import uuid

from fastapi.testclient import TestClient
from src.main import app
from src.config import reset_db


class TestStatsEndpoints(unittest.TestCase):
    def setUp(self) -> None:
        reset_db()
        self.client = TestClient(app)
        self.client_id = uuid.UUID("123e4567-e89b-12d3-a456-426614174000")
        self.advertiser_id = uuid.UUID("133e4567-e89b-12d3-a456-426614174000")
        self.client.post("/clients/bulk", json=[{
            "client_id": str(self.client_id),
            "login": "new_login",
            "age": 30,
            "gender": "Female",
            "location": "Moscow"
        }])
        self.client.post("/advertisers/bulk", json=[
            {"advertiser_id": str(self.advertiser_id), "name": "advertiser12"}])

    def test_get_campaign_stats(self):
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
                "targeting": {
                }
            }
        )
        self.assertEqual(response.status_code, 201)
        campaign_id = response.json()["campaign_id"]

        for impression in range(100):
            self.client.get("/ads", params={"client_id": str(self.client_id)})
        for click in range(50):
            self.client.post(f"/ads/{campaign_id}/click", params={"adsID": str(campaign_id)},
                             json={"client_id": str(self.client_id)})

        response = self.client.get(f"/stats/campaigns/{campaign_id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["impressions_count"], 100)
        self.assertEqual(response.json()["clicks_count"], 50)
        self.assertEqual(response.json()["conversion"], 50)
        self.assertEqual(response.json()["spent_impressions"], 50)
        self.assertEqual(response.json()["spent_clicks"], 50)
        self.assertEqual(response.json()["spent_total"], 100)

    def test_get_campaign_stats_not_found(self):
        response = self.client.get(f"/stats/campaigns/00000000-0000-0000-0000-000000000000")
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Campaign not found")

    def test_get_advertiser_campaigns_stats(self):
        campaign_ids = []
        for camp in range(3):
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
            campaign_id = uuid.UUID(response.json()["campaign_id"])
            campaign_ids.append(campaign_id)

            for impression in range(100):
                self.client.get("/ads", params={"client_id": str(self.client_id)})
            for click in range(50):
                self.client.post(f"/ads/{campaign_id}/click", params={"adsID": str(campaign_id)},
                                 json={"client_id": str(self.client_id)})

        response = self.client.get(f"/stats/advertisers/{str(self.advertiser_id)}/campaigns/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json()["impressions_count"], 300)
        self.assertEqual(response.json()["clicks_count"], 150)
        self.assertEqual(response.json()["conversion"], 50)
        self.assertEqual(response.json()["spent_impressions"], 150)
        self.assertEqual(response.json()["spent_clicks"], 150)
        self.assertEqual(response.json()["spent_total"], 300)

    def test_get_advertiser_campaigns_stats_not_found(self):
        response = self.client.get(f'/stats/advertisers/{uuid.UUID("00000000-0000-0000-0000-000000000000")}/campaigns/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Advertiser not found")

    def test_get_daily_stats(self):
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

        for impression in range(100):
            response = self.client.get("/ads", params={"client_id": str(self.client_id)})
            print(response.content)
        for click in range(50):
            self.client.post(f"/ads/{campaign_id}/click", params={"adsID": str(campaign_id)},
                             json={"client_id": str(self.client_id)})

        response = self.client.get(f"/stats/campaigns/{campaign_id}/daily")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]["impressions_count"], 100)
        self.assertEqual(response.json()[0]["clicks_count"], 50)
        self.assertEqual(response.json()[0]["conversion"], 50)
        self.assertEqual(response.json()[0]["spent_impressions"], 50)
        self.assertEqual(response.json()[0]["spent_clicks"], 50)
        self.assertEqual(response.json()[0]["spent_total"], 100)

    def test_get_daily_stats_not_found(self):
        response = self.client.get(f'/stats/campaigns/{uuid.UUID("00000000-0000-0000-0000-000000000000")}/daily')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Campaign not found")

    def test_get_advertiser_campaigns_daily_stats(self):
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
                "end_date": 9999999,
                "targeting": {}
            }
        )
        self.assertEqual(response.status_code, 201)
        campaign_id = uuid.UUID(response.json()["campaign_id"])

        for impression in range(100):
            self.client.get("/ads", params={"client_id": str(self.client_id)})
        for click in range(50):
            self.client.post(f"/ads/{campaign_id}/click", params={"adsID": str(campaign_id)},
                             json={"client_id": str(self.client_id)})

        response = self.client.get(f"/stats/advertisers/{self.advertiser_id}/campaigns/daily")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.json()), 1)
        for stat in response.json():
            self.assertEqual(stat["impressions_count"], 100)
            self.assertEqual(stat["clicks_count"], 50)
            self.assertEqual(stat["spent_impressions"], 50)
            self.assertEqual(stat["spent_clicks"], 50)
            self.assertEqual(stat["spent_total"], 100)

    def test_get_advertiser_campaigns_daily_stats_not_found(self):
        response = self.client.get(
            f'/stats/advertisers/{uuid.UUID("00000000-0000-0000-0000-000000000000")}/campaigns/daily')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.json()["detail"], "Advertiser campaigns not found")
