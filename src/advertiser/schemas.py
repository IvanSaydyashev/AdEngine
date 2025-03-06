import uuid

from pydantic import BaseModel, Field, StrictInt
from pydantic import StrictStr


class AdvertiserSchema(BaseModel):
    advertiser_id: uuid.UUID
    name: StrictStr = Field(min_length=1)

class MLScoreSchema(BaseModel):
    client_id: uuid.UUID
    advertiser_id: uuid.UUID
    score: StrictInt
