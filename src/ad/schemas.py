from pydantic import BaseModel
import uuid

class AdClickSchema(BaseModel):
    client_id: uuid.UUID
