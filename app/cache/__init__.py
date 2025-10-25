import os
import json
from typing import Any, Optional
from redis.asyncio import Redis, ConnectionPool

from dotenv import load_dotenv

load_dotenv()

REDIS_HOST = os.getenv("REDIS_HOST", 10)
REDIS_PORT = os.getenv("REDIS_PORT", 10)
REDIS_URL = f'{REDIS_HOST}://{REDIS_HOST}:{REDIS_PORT}'

redisPool = ConnectionPool.from_url(REDIS_URL, decode_responses=True)
redisClient = Redis(connection_pool=redisPool)

async def getCacheData(key: str) -> Optional[Any]:
    value = await redisClient.get(key)
    if value:
        return json.loads(value)
    return None

async def putCacheData(key: str, value: Any, ttl: int = 3600) -> None:
    serialized_value = json.dumps(value)
    await redisClient.set(key, serialized_value, ex=ttl)

async def deleteCacheData(key: str) -> int:
    return await redisClient.delete(key)

async def closeCacheConnection() -> None:
    await redisClient.close()
    await redisPool.disconnect()
    