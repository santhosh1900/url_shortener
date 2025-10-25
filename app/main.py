import asyncio
import os
from contextlib import asynccontextmanager
from fastapi import Depends, FastAPI
from fastapi_limiter import FastAPILimiter
from fastapi_limiter.depends import RateLimiter
from dotenv import load_dotenv
import uvicorn

from app.database import Base, createDatabaseIfNotExists, engine
import app.handler.url as urlRouter
import app.handler.auth as authRouter
from app.cache import redisClient, closeCacheConnection

load_dotenv()

@asynccontextmanager
async def lifespan(app: FastAPI):
    try:
        await createDatabaseIfNotExists()
        await FastAPILimiter.init(redisClient)

        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        print("✅ Tables created successfully.")

        yield

        await engine.dispose()
        await closeCacheConnection()
        print("🛑 Database connection closed.")
    except asyncio.CancelledError:
        pass
    except Exception as e:
        print("Error during lifespan startup:", e)
        raise


RATE_LIMITTER_SECONDS = int(os.getenv("RATE_LIMITTER_SECONDS", 60))
RATE_LIMITTER_REQUESTS = int(os.getenv("RATE_LIMITTER_REQUESTS", 100))
PORT = int(os.getenv("PORT", 8080))

limiter = RateLimiter(times=RATE_LIMITTER_REQUESTS, seconds=RATE_LIMITTER_SECONDS)
GLOBAL_DEPENDENCY = [Depends(limiter)]

app = FastAPI(lifespan=lifespan, dependencies=GLOBAL_DEPENDENCY)

app.include_router(urlRouter.router)
app.include_router(authRouter.router)

if __name__ == "__main__":
    uvicorn.run(app=app, host="0.0.0.0", port=PORT)
