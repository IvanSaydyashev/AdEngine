from src.config import Base
from sqlalchemy import Column, UUID, Integer, Boolean, ForeignKey
import uuid

class AdViewModel(Base):
    __tablename__ = "ad_view"

    view_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.campaign_id"), nullable=False)
    client_id = Column(UUID(as_uuid=True), ForeignKey("client.client_id"), nullable=False)
    view_date = Column(Integer, nullable=False)
