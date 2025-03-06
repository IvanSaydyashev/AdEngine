import httpx
from fastapi import APIRouter
from fastapi.encoders import jsonable_encoder
from fastapi.params import Depends, Query
from sqlalchemy.orm import Session
from src.config import get_db, get_redis, settings
from src.campaign.models import *
from src.campaign.schemas import *
from src.tools import *
from src.advertiser.models import *
import redis.asyncio as redis
from uuid import UUID
from pydantic import StrictBool

router = APIRouter()
api_url = settings.API_URL


@router.post("/advertisers/{advertiserId}/campaigns", tags=["Campaigns"], name="Создание рекламной кампании",
             description="Создаёт новую рекламную кампанию для указанного рекламодателя.", status_code=201)
async def post_advertiser_campaigns(advertiserId: UUID,
                                    campaign_data: CampaignSchema,
                                    isGenerate: StrictBool = Query(False),
                                    db: Session = Depends(get_db)):
    advertiser_existins = db.query(AdvertiserModel).filter(AdvertiserModel.advertiser_id == advertiserId).first()
    if not advertiser_existins:
        raise HTTPException(status_code=404, detail="Advertiser not found")

    targeting_data = jsonable_encoder(campaign_data.targeting)
    if targeting_data:
        targeting_data = except_null(targeting_data)

    if isGenerate:
        async with httpx.AsyncClient() as client:
            validation_payload = {
                "ad_name": campaign_data.ad_title,
                "advertiser_name": advertiser_existins.name,
                "targeting": targeting_data,
            }
            llm_response = await client.post(f"{api_url}/llm-action/generate", json=validation_payload)
        try:
            llm_response = llm_response.content.decode("utf-8")
            print(llm_response)
            campaign_data.ad_text = llm_response
        except:
            raise HTTPException(status_code=400, detail="Invalid LLM response")
    else:
        if campaign_data.ad_text is None:
            raise HTTPException(status_code=400, detail="Invalid ad text")
        async with httpx.AsyncClient() as client:
            validation_payload = {"ad_text": campaign_data.ad_text}
            llm_response = await client.post(f"{api_url}/llm-action/validate", json=validation_payload)
        try:
            llm_response = llm_response.json()
        except:
            raise HTTPException(status_code=400, detail="Invalid LLM response")

        if llm_response["status"] != "accept":
            raise HTTPException(status_code=400, detail=f"Your ad text is not valid: {llm_response['reason']}")

    new_campaign = CampaignModel(
        advertiser_id=advertiserId,
        impressions_limit=campaign_data.impressions_limit,
        clicks_limit=campaign_data.clicks_limit,
        cost_per_impression=campaign_data.cost_per_impression,
        cost_per_click=campaign_data.cost_per_click,
        ad_title=campaign_data.ad_title,
        ad_text=campaign_data.ad_text,
        start_date=campaign_data.start_date,
        end_date=campaign_data.end_date,
        targeting=jsonable_encoder(targeting_data) if targeting_data else None,
    )
    db.add(new_campaign)
    db.commit()
    db.refresh(new_campaign)

    return jsonable_encoder(new_campaign)


@router.get("/advertisers/{advertiserId}/campaigns", tags=["Campaigns"],
            name="Получение рекламных кампаний рекламодателя c пагинацией",
            description="Возвращает список рекламных кампаний для указанного рекламодателя с пагинацией.")
def get_advertiser_campaigns(advertiserId: UUID,
                             size: Optional[int] = None,
                             page: Optional[int] = None,
                             db: Session = Depends(get_db)):
    campaign_list = db.query(CampaignModel).filter(CampaignModel.advertiser_id == advertiserId).all()
    campaign_list = paginate(items=campaign_list, page=page, per_page=size)
    return jsonable_encoder(campaign_list)


@router.get("/advertisers/{advertiserId}/campaigns/{campaignId}", tags=["Campaigns"], name="Получение кампании по ID",
            description="Возвращает кампанию по ID.")
def get_advertiser_campaign(advertiserId: UUID, campaignId: UUID, db: Session = Depends(get_db)):
    campaign = db.query(CampaignModel).filter(CampaignModel.campaign_id == campaignId).one_or_none()
    if campaign is None or campaign.advertiser_id != advertiserId:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return jsonable_encoder(campaign)


@router.put("/advertisers/{advertiserId}/campaigns/{campaignId}", tags=["Campaigns"],
            name="Обновление рекламной кампании",
            description="Обновляет разрешённые параметры рекламной кампании до её старта.")
async def update_advertiser_campaign(advertiserId: UUID, campaignId: UUID, campaign_data: PutCampaignSchema,
                                     db: Session = Depends(get_db), redis_db: redis.Redis = Depends(get_redis)):
    campaign = db.query(CampaignModel).filter(CampaignModel.campaign_id == campaignId).one_or_none()
    if campaign is None or campaign.advertiser_id != advertiserId:
        raise HTTPException(status_code=404, detail="Campaign not found")

    today = await redis_db.get("current_date")

    today = int(today)
    isStarted = False

    if campaign.start_date <= today <= campaign.end_date:
        isStarted = True

    targeting_data = jsonable_encoder(campaign_data.targeting)
    if targeting_data:
        campaign.targeting = except_null(targeting_data)
    else:
        campaign.targeting = None

    if not isStarted:
        if campaign_data.impressions_limit is not None:
            campaign.impressions_limit = campaign_data.impressions_limit
        if campaign_data.clicks_limit is not None:
            campaign.clicks_limit = campaign_data.clicks_limit
        if campaign_data.start_date is not None:
            campaign.start_date = campaign_data.start_date
        if campaign_data.end_date is not None:
            campaign.end_date = campaign_data.end_date

    if campaign_data.cost_per_impression is not None:
        campaign.cost_per_impression = campaign_data.cost_per_impression
    if campaign_data.cost_per_click is not None:
        campaign.cost_per_click = campaign_data.cost_per_click
    if campaign_data.ad_title is not None:
        campaign.ad_title = campaign_data.ad_title
    if campaign_data.ad_text is not None:
        async with httpx.AsyncClient() as client:
            validation_payload = {"ad_text": campaign_data.ad_text}
            llm_response = await client.post(f"{api_url}/llm-action/validate", json=validation_payload)
        try:
            llm_response = llm_response.json()
        except:
            raise HTTPException(status_code=400, detail="Invalid LLM response")

        if llm_response["status"] != "accept":
            raise HTTPException(status_code=400, detail=f"Your ad text is not valid: {llm_response['reason']}")
        campaign.ad_text = campaign_data.ad_text
    db.commit()
    db.refresh(campaign)

    return jsonable_encoder(campaign)


@router.delete("/advertisers/{advertiserId}/campaigns/{campaignId}", tags=["Campaigns"],
               name="Удаление рекламной кампании",
               description="Удаляет рекламную кампанию рекламодателя по заданному campaignId.", status_code=204)
def delete_advertiser_campaign(advertiserId: UUID, campaignId: UUID, db: Session = Depends(get_db)):
    campaign = db.query(CampaignModel).filter(CampaignModel.campaign_id == campaignId).one_or_none()
    if campaign is None or campaign.advertiser_id != advertiserId:
        raise HTTPException(status_code=404, detail="Campaign not found")

    db.delete(campaign)
    db.commit()

    return {"status": "ok"}
