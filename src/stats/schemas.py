import uuid

from pydantic import BaseModel, StrictInt


class DailyStatsSchema(BaseModel):
    campaign_id: uuid.UUID
    day: StrictInt
    views_count: StrictInt
    clicks_count: StrictInt
    revenue: float