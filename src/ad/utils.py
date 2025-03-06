import redis.asyncio as redis
from typing import List
from src.advertiser.models import MLScoreModel

async def get_ml_scores_from_redis(r: redis.Redis, client_id: str) -> List[MLScoreModel]:
    pattern = f"ml_scores:{client_id}:*"
    keys = await r.keys(pattern)

    response = []
    for key in keys:
        score = int(await r.get(key))
        key = str(key)
        advertiser_id = key.split(":")[2]

        response.append(
            MLScoreModel(
                client_id=client_id,
                advertiser_id=advertiser_id,
                score=score,
            )
        )

    return response