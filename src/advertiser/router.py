from types import new_class
from typing import List

import redis
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy import or_, and_
from sqlalchemy.orm import Session

from src.client.models import ClientModel
from src.config import get_db, get_redis
from src.advertiser.models import *
from src.advertiser.schemas import *
from uuid import UUID
router = APIRouter()


@router.get("/advertisers/{advertiserId}", tags=["Advertisers"], name="Получение рекламодателя по ID",
            description="Возвращает информацию о рекламодателе по его ID.")
def get_advertiser_by_id(advertiserId: UUID, db: Session = Depends(get_db)):
    existing_client = db.query(AdvertiserModel).filter(
        AdvertiserModel.advertiser_id == advertiserId).one_or_none()
    if not existing_client:
        raise HTTPException(status_code=404, detail="Client not found")
    return existing_client


@router.post("/advertisers/bulk", tags=["Advertisers"], name="Массовое создание/обновление рекламодателей",
             description="Создаёт новых или обновляет существующих рекламодателей", status_code=201)
def bulk(advertiser_data: List[AdvertiserSchema], db: Session = Depends(get_db)):
    try:
        for advertiser in advertiser_data:
            advertiser_id_uuid = advertiser.advertiser_id
            existing_advertiser = db.query(AdvertiserModel).filter(
                AdvertiserModel.advertiser_id == advertiser_id_uuid).one_or_none()
            if existing_advertiser:
                existing_advertiser.name = advertiser.name
            else:
                new_advertiser = AdvertiserModel(
                    advertiser_id=advertiser.advertiser_id,
                    name=advertiser.name,
                )
                db.add(new_advertiser)
        db.commit()
    except:
        db.rollback()
        raise HTTPException(status_code=400, detail="Bulk data is not valid")
    return advertiser_data


@router.post("/ml-scores", tags=["Advertisers"], name="Добавление или обновление ML скора",
             description="Добавляет или обновляет ML скор для указанной пары клиент-рекламодатель.")
async def ml_scores(ml_data: MLScoreSchema, db: Session = Depends(get_db), redis: redis.Redis = Depends(get_redis)):
    existing_client = db.query(ClientModel).filter(ClientModel.client_id == ml_data.client_id).one_or_none()
    existing_advertiser = db.query(AdvertiserModel).filter(
        AdvertiserModel.advertiser_id == ml_data.advertiser_id).one_or_none()

    if not existing_client or not existing_advertiser:
        raise HTTPException(status_code=404, detail="Advertiser or Client not found")

    ml_score_existing = db.query(MLScoreModel).filter(MLScoreModel.client_id == ml_data.client_id,
                                                      MLScoreModel.advertiser_id == ml_data.advertiser_id).one_or_none()
    new_score = ml_data.score
    if not ml_score_existing:
        new_ml_score = MLScoreModel(
            score_id=uuid.uuid4(),
            client_id=ml_data.client_id,
            advertiser_id=ml_data.advertiser_id,
            score=new_score
        )
        db.add(new_ml_score)
    else:
        ml_score_existing.score = new_score
    redis_key = f"ml_scores:{ml_data.client_id}:{ml_data.advertiser_id}"
    await redis.set(redis_key, new_score)

    db.commit()
    return ml_data
