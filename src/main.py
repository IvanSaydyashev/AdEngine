import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager
import redis.asyncio as redis

from src.ad.router import router as ad_router
from src.advertiser.router import router as advertiser_router
from src.client.router import router as client_router
from src.campaign.router import router as campaign_router
from src.stats.router import router as stats_router
from src.time.router import router as time_router
from src.llm_api.router import router as llm_api_router
from src.config import get_db, get_redis, init_db, settings

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    yield

app = FastAPI(lifespan=lifespan)

# Include routers
app.include_router(client_router)
app.include_router(advertiser_router)
app.include_router(campaign_router)
app.include_router(ad_router)
app.include_router(stats_router)
app.include_router(time_router)
app.include_router(llm_api_router)

if __name__ == "__main__":
    uvicorn.run(app, host=settings.SERVER_HOST, port=int(settings.SERVER_PORT))
