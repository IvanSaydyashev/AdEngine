from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse

from src.ad.schemas import *
from src.config import get_db, get_redis
from src.ad.services import *
from src.ad.utils import get_ml_scores_from_redis
from uuid import UUID
from src.ad.models import AdViewModel
router = APIRouter()


@router.get("/ads", tags=["Ads"], name="Получение рекламного объявления для клиента",
            description="Возвращает рекламное объявление, подходящее для показа клиенту с учетом таргетинга и ML скора.")
async def get_ads(
        client_id: UUID,
        db: Session = Depends(get_db),
        redis_db: redis.Redis = Depends(get_redis)
):
    today = await redis_db.get("current_date")
    try:
        today = int(today)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format"
        )
    client = db.get(ClientModel, client_id)
    if not client:
        raise HTTPException(
            status_code=404,
            detail="Client not found"
        )

    ml_scores = await get_ml_scores_from_redis(redis_db, str(client_id))

    if not ml_scores:
        ml_scores = db.query(MLScoreModel).filter(MLScoreModel.client_id == client.client_id).all()
        for ml in ml_scores:
            await redis_db.set(f'ml_scores:{client.client_id}:{ml.advertiser_id}', str(ml.score))

    best_campaign = select_best_campaign(
        db=db,
        ml_scores=ml_scores,
        client=client,
        current_date=today
    )

    if not best_campaign:
        return JSONResponse(
            content={"message": "No ads available"},
            status_code=404
        )

    is_unique_view = db.query(AdViewModel).filter(AdViewModel.client_id == client_id,
                                                  AdViewModel.view_date == today).one_or_none()
    if is_unique_view is None:
        new_view = AdViewModel(
            campaign_id=best_campaign.campaign_id,
            client_id=client_id,
            view_date=today,
        )
        db.add(new_view)
        db.commit()

        update_campaign_stats(
            action=Action.VIEW,
            today=today,
            db=db,
            campaign=best_campaign,
            cost_per_impression=best_campaign.cost_per_impression,
            cost_per_click=best_campaign.cost_per_click,
        )

    return {
        "ad_id": best_campaign.campaign_id,
        "ad_title": best_campaign.ad_title,
        "ad_text": best_campaign.ad_text,
        "advertiser_id": best_campaign.advertiser_id
    }


@router.post("/ads/{adsId}/click", tags=["Ads"], name="Фиксация перехода по рекламному объявлению",
             description="Фиксирует клик (переход) клиента по рекламному объявлению.", status_code=204)
async def click_ad(adsId: UUID, client_id: AdClickSchema, db: Session = Depends(get_db),
                   redis_db: redis.Redis = Depends(get_redis)):
    today = await redis_db.get("current_date")
    try:
        today = int(today)
    except:
        raise HTTPException(
            status_code=400,
            detail="Invalid date format"
        )
    campaign_existing = db.query(CampaignModel).filter(CampaignModel.campaign_id == adsId).first()
    if not campaign_existing:
        raise HTTPException(status_code=404, detail="Ad not found")

    update_campaign_stats(
        action=Action.CLICK,
        today=today,
        db=db,
        campaign=campaign_existing,
        cost_per_impression=float(str(campaign_existing.cost_per_impression)),
        cost_per_click=float(str(campaign_existing.cost_per_click)),
    )

    return {"client_id": str(client_id)}
