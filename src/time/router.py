from fastapi import APIRouter
from fastapi.params import Depends
import redis.asyncio as redis
from src.time.schemas import *
from src.config import get_redis
from fastapi import HTTPException
router = APIRouter()

@router.post('/time/advance',
             tags=['Time'],
             name="Установка текущей даты",
             description="Устанавливает текущий день в системе в заданную дату.",
             status_code=200)
async def SetTime(current_date: TimeSchema, redis_db: redis.Redis = Depends(get_redis)):
    now_date = await redis_db.get("current_date")
    if int(now_date) > current_date.current_date:
        raise HTTPException(status_code=400, detail="Cannot set date to past")
    await redis_db.set('current_date', current_date.current_date)
    return {"current_date": current_date.current_date}
