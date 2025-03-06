import uuid
from sqlalchemy import Column, VARCHAR, INTEGER, UUID, Enum

from src.config import Base
from src.config import Gender


class ClientModel(Base):
    __tablename__ = 'client'

    client_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    login = Column(VARCHAR, nullable=False)
    age = Column(INTEGER, nullable=False)
    location = Column(VARCHAR, nullable=False)
    gender = Column(Enum(Gender), nullable=False)
