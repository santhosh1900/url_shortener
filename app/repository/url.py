from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from app.model import URLMapping, URLAnalytics
from datetime import datetime, timedelta, timezone


class UrlRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def getByShortCode(self, shortCode: str):
        query = select(URLMapping).where(URLMapping.short_code == shortCode)
        res = await self.db.execute(query)
        return res.scalars().first()

    async def getByOriginalUrl(self, originalUrl: str):
        query = select(URLMapping).where(URLMapping.original_url == originalUrl)
        res = await self.db.execute(query)
        return res.scalars().first()

    async def create(self, shortCode: str, originalUrl: str):
        obj = URLMapping(short_code=shortCode, original_url=originalUrl)
        self.db.add(obj)
        try:
            await self.db.commit()
            await self.db.refresh(obj)
            return obj
        except IntegrityError:
            await self.db.rollback()
            raise

    async def incrementClick(self, obj: URLMapping):
        obj.click_count = obj.click_count + 1
        obj.last_accessed_at = datetime.now(timezone.utc)
        self.db.add(obj)
        await self.db.commit()
        await self.incrementHourlyClick(obj=obj)
    
    async def updateShortCode(self, obj: URLMapping, shortCode: str):
        obj.short_code = shortCode
        self.db.add(obj)
        await self.db.commit()
        await self.incrementHourlyClick(obj=obj)

    async def incrementHourlyClick(self, obj: URLMapping):
        now = datetime.now(timezone.utc)
        startOfHour = now.replace(minute=0, second=0, microsecond=0)
        endOfHour = startOfHour + timedelta(hours=1) - timedelta(seconds=1)
        query = select(URLAnalytics).where(
            URLAnalytics.url_id == obj.id,
            URLAnalytics.start_at == startOfHour,
            URLAnalytics.end_at == endOfHour
        )
        result = await self.db.execute(query)
        record = result.scalar_one_or_none()
        if record:
            record.click_count += 1
        else:
            record = URLAnalytics(
                url_id=obj.id,
                click_count=1,
                start_at=startOfHour,
                end_at=endOfHour
            )
            self.db.add(record)
        await self.db.commit()
        await self.db.refresh(record)

    async def listUrls(self, offset: int = 0, limit: int = 50):
        query = (
            select(URLMapping)
            .order_by(URLMapping.created_at.desc())
            .offset(offset - 1)
            .limit(limit)
        )
        res = await self.db.execute(query)
        return res.scalars().all()
    
    async def getDailyClickAnalytics(self, obj: URLMapping):
        dayTrunc = func.date_trunc('day', URLAnalytics.start_at)
        query = (
            select(
                dayTrunc.label('date'),
                func.sum(URLAnalytics.click_count).label('total_clicks')
            )
            .group_by(dayTrunc)
            .order_by(dayTrunc.desc())
        )

        result = await self.db.execute(query)
        return result.all()
