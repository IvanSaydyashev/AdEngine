import uuid

from pydantic import BaseModel, Field, field_validator
from pydantic import StrictInt, StrictStr

from src.config import Gender


class ClientSchema(BaseModel):
    client_id: uuid.UUID
    login: StrictStr = Field(min_length=1)
    age: StrictInt = Field(ge=0, le=100)
    location: StrictStr = Field(max_length=255)
    gender: Gender

    @field_validator("gender", mode="before")
    def validate_gender(cls, value):
        value = str(value).upper()
        if value not in Gender.__members__:
            raise ValueError(f"gender must be one of {Gender.__members__}")
        return Gender[value]
