from sys import exc_info

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from src.config import get_db
from src.stats.models import *
from src.campaign.models import *
from src.advertiser.models import *
from uuid import UUID

router = APIRouter()


@router.get("/stats/campaigns/{campaignId}", tags=["Statistics"], name="Получение статистики по рекламной кампании",
            description="Возвращает агрегированную статистику (показы, переходы, затраты и конверсию) для заданной рекламной кампании.")
def get_campaign_stats(campaignId: UUID, db: Session = Depends(get_db)):
    campaign = db.query(CampaignModel).filter(CampaignModel.campaign_id == campaignId).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    stats = db.query(DailyStatsModel).filter(DailyStatsModel.campaign_id == campaignId).all()
    if not stats:
        raise HTTPException(status_code=404, detail="Campaign stats not found")

    total_impressions, total_clicks = 0, 0
    spent_clicks_total, spent_impressions_total = 0, 0

    for stat in stats:
        total_impressions += stat.impressions_count
        total_clicks += stat.clicks_count
        spent_clicks_total += stat.spent_clicks
        spent_impressions_total += stat.spent_impressions

    conversion = total_clicks / total_impressions * 100
    spent_total = spent_clicks_total + spent_impressions_total

    return {
        "impressions_count": total_impressions,
        "clicks_count": total_clicks,
        "conversion": conversion,
        "spent_impressions": spent_impressions_total,
        "spent_clicks": spent_clicks_total,
        "spent_total": spent_total
    }


@router.get("/stats/advertisers/{advertiserId}/campaigns/", tags=["Statistics"],
            name="Получение агрегированной статистики по всем кампаниям рекламодателя",
            description="Возвращает сводную статистику по всем рекламным кампаниям, принадлежащим заданному рекламодателю.")
def get_advertiser_campaigns_stats(advertiserId: UUID, db: Session = Depends(get_db)):
    advertiser = db.query(AdvertiserModel).filter(AdvertiserModel.advertiser_id == advertiserId).first()
    if not advertiser:
        raise HTTPException(status_code=404, detail="Advertiser not found")
    campaigns = db.query(CampaignModel).filter(CampaignModel.advertiser_id == advertiserId).all()
    if not campaigns:
        raise HTTPException(status_code=404, detail="Advertiser campaigns not found")

    stats = []
    for campaign in campaigns:
        stats += db.query(DailyStatsModel).filter(DailyStatsModel.campaign_id == campaign.campaign_id).all()
    total_impressions, total_clicks = 0, 0
    spent_clicks_total, spent_impressions_total = 0, 0
    if not stats:
        return {
            "impressions_count": 0,
            "clicks_count": 0,
            "conversion": 0,
            "spent_impressions": 0,
            "spent_clicks": 0,
            "spent_total": 0
        }
    for stat in stats:
        total_impressions += stat.impressions_count
        total_clicks += stat.clicks_count
        spent_clicks_total += stat.spent_clicks
        spent_impressions_total += stat.spent_impressions

    if total_impressions:
        conversion = total_clicks / total_impressions * 100
    else:
        conversion = 0
    spent_total = spent_clicks_total + spent_impressions_total

    return {
        "impressions_count": total_impressions,
        "clicks_count": total_clicks,
        "conversion": conversion,
        "spent_impressions": spent_impressions_total,
        "spent_clicks": spent_clicks_total,
        "spent_total": spent_total
    }


@router.get("/stats/campaigns/{campaignId}/daily", tags=["Statistics"],
            name="Получение ежедневной статистики по рекламной кампании",
            description="Возвращает массив ежедневной статистики для указанной рекламной кампании.")
def get_daily_stats(campaignId: UUID, db: Session = Depends(get_db)):
    campaign = db.query(CampaignModel).filter(CampaignModel.campaign_id == campaignId).first()
    if not campaign:
        raise HTTPException(status_code=404, detail="Campaign not found")
    stats = db.query(DailyStatsModel).filter(DailyStatsModel.campaign_id == campaignId).all()
    if not stats:
        raise HTTPException(status_code=404, detail="Campaign stats not found")

    response = []

    for stat in stats:
        response.append({
            "impressions_count": stat.impressions_count,
            "clicks_count": stat.clicks_count,
            "conversion": stat.clicks_count / stat.impressions_count * 100 if stat.impressions_count else 0,
            "spent_impressions": stat.spent_impressions,
            "spent_clicks": stat.spent_clicks,
            "spent_total": stat.spent_impressions + stat.spent_clicks,
            "date": stat.day
        })

    return response


@router.get("/stats/advertisers/{advertiserId}/campaigns/daily", tags=["Statistics"],
            name="Получение ежедневной агрегированной статистики по всем кампаниям рекламодателя",
            description="Возвращает массив ежедневной сводной статистики по всем рекламным кампаниям заданного рекламодателя.")
def get_advertiser_campaigns_daily_stats(advertiserId: UUID, db: Session = Depends(get_db)):
    campaigns = db.query(CampaignModel).filter(CampaignModel.advertiser_id == advertiserId).all()
    if not campaigns:
        raise HTTPException(status_code=404, detail="Advertiser campaigns not found")
    response = []
    for campaign in campaigns:
        stats = db.query(DailyStatsModel).filter(DailyStatsModel.campaign_id == campaign.campaign_id).all()
        for stat in stats:
            response.append({
                "impressions_count": stat.impressions_count,
                "clicks_count": stat.clicks_count,
                "spent_impressions": stat.spent_impressions,
                "spent_clicks": stat.spent_clicks,
                "spent_total": stat.spent_impressions + stat.spent_clicks,
                "date": stat.day
            })

    return response
