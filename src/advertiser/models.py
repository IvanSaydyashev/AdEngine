import uuid
from sqlalchemy import Column, VARCHAR, UUID, ForeignKey, Integer

from src.config import Base


class AdvertiserModel(Base):
    __tablename__ = 'advertiser'

    advertiser_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    name = Column(VARCHAR, nullable=False)

class MLScoreModel(Base):
    __tablename__ = "ml_score"

    score_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.client_id"))
    advertiser_id = Column(UUID(as_uuid=True), ForeignKey("advertiser.advertiser_id"), primary_key=True)
    score = Column(Integer, nullable=False)
