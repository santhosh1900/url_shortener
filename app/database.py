import os
from sqlalchemy import create_engine, text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv

load_dotenv()

DB_USER = os.getenv("POSTGRES_USER")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD")
DB_NAME = os.getenv("POSTGRES_DB")
DB_PORT = os.getenv("POSTGRES_PORT")
DB_HOST = os.getenv("POSTGRES_HOST")
SYS_DB = os.getenv("SYSTEM_DB")

DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
SYS_DB_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{SYS_DB}'

engine = create_async_engine(DB_URL, echo=False, pool_size=10, max_overflow=20)
syncEngine = create_engine(SYS_DB_URL, echo=False)

asyncSession = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

Base = declarative_base()

async def createDatabaseIfNotExists():
    tmpEngine = create_async_engine(SYS_DB_URL, echo=False, isolation_level="AUTOCOMMIT")
    async with tmpEngine.connect() as conn:
        result = await conn.execute(
            text(f"SELECT 1 FROM pg_database WHERE datname='{DB_NAME}'")
        )
        exists = result.scalar()
        if not exists:
            await conn.execute(text(f"CREATE DATABASE {DB_NAME}"))
            print(f"✅ Database '{DB_NAME}' created successfully.")
        else:
            print(f"✅ Database '{DB_NAME}' already exists.")
    await tmpEngine.dispose()

async def getSession():
    async with asyncSession() as session:
        yield session