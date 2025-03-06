from pydantic import BaseModel, StrictStr
from enum import Enum

from src.campaign.schemas import TargetingSchema


class ACTIONS(Enum):
    GENERATE = "generate"
    VALIDATE = "validate"


class LLMValidateRequestSchema(BaseModel):
    ad_text: StrictStr

class LLMGenerateRequestSchema(BaseModel):
    ad_name: StrictStr
    advertiser_name: StrictStr
    targeting: TargetingSchema
