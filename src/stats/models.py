from sqlalchemy import Column, UUID, Integer, ForeignKey, Float

from src.config import Base


class DailyStatsModel(Base):
    __tablename__ = "daily_stat"

    campaign_id = Column(UUID(as_uuid=True), ForeignKey("campaign.campaign_id"), primary_key=True)
    day = Column(Integer, primary_key=True)
    impressions_count = Column(Integer, nullable=False)
    clicks_count = Column(Integer, nullable=False)
    spent_impressions = Column(Float, nullable=False)
    spent_clicks = Column(Float, nullable=False)
