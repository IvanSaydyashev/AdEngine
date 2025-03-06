from pydantic import BaseModel, StrictInt, Field


class TimeSchema(BaseModel):
    current_date: StrictInt = Field(ge=0)
