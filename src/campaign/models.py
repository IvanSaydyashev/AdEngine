import uuid
from sqlalchemy import Column, VARCHAR, Integer, UUID, Float, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB

from src.config import Base


class CampaignModel(Base):
    __tablename__ = 'campaign'

    campaign_id = Column(UUID(as_uuid=True), primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    advertiser_id = Column(UUID(as_uuid=True), ForeignKey("advertiser.advertiser_id"), nullable=False)
    impressions_limit = Column(Integer, nullable=False)
    clicks_limit = Column(Integer, nullable=False)
    cost_per_impression = Column(Float, nullable=False)
    cost_per_click = Column(Float, nullable=False)
    ad_title = Column(VARCHAR, nullable=False)
    ad_text = Column(VARCHAR, nullable=False)
    start_date = Column(Integer, nullable=False, index=True)
    end_date = Column(Integer, nullable=False, index=True)
    targeting = Column(JSONB, nullable=True)

    def __repr__(self):
        return f"<CampaignModel(id={self.campaign_id}, title={self.ad_title})>" #pragma: no cover
