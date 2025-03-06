import uuid

from pydantic import BaseModel, Field, model_validator, field_validator
from pydantic import StrictInt, StrictStr
from typing import Optional

from src.config import Gender


class CampaignAdvertisementSchema(BaseModel):
    advertiser_id: uuid.UUID


class TargetingSchema(BaseModel):
    gender: Optional[Gender] = None
    age_from: Optional[StrictInt] = None
    age_to: Optional[StrictInt] = None
    location: Optional[StrictStr] = None

    @field_validator("gender", mode="before")
    def validate_gender(cls, value):
        if value is None:
            return value
        value = value.upper()
        if value not in Gender.__members__:
            raise ValueError(f"gender must be one of {Gender.__members__}")
        return Gender[value]

    @field_validator("location", mode="before")
    def validate_location(cls, value):
        if value == "":
            value = None
        return value

class CampaignSchema(BaseModel):
    impressions_limit: StrictInt = Field(ge=0)
    clicks_limit: StrictInt = Field(ge=0)
    cost_per_impression: float = Field(ge=0)
    cost_per_click: float = Field(ge=0)
    ad_title: StrictStr = Field(min_length=3, max_length=255)
    ad_text: StrictStr = Field(min_length=3, max_length=255)
    start_date: StrictInt = Field(ge=0)
    end_date: StrictInt = Field(ge=0)
    targeting: Optional[TargetingSchema] = None

    @model_validator(mode='after')
    def model_validate(cls, values):
        if values.end_date < values.start_date:
            raise ValueError('End date must be before start date')
        return values


class PutCampaignSchema(BaseModel):
    impressions_limit: Optional[float] = Field(None, ge=0)
    clicks_limit: Optional[float] = Field(None, ge=0)
    cost_per_impression: Optional[float] = Field(None, ge=0)
    cost_per_click: Optional[float] = Field(None, ge=0)
    ad_title: Optional[StrictStr] = Field(None, max_length=255)
    ad_text: Optional[StrictStr] = Field(None, max_length=255)
    start_date: Optional[StrictInt] = Field(None, ge=0)
    end_date: Optional[StrictInt] = Field(None, ge=0)
    targeting: Optional[TargetingSchema] = None
