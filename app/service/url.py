import os
from sqlalchemy.ext.asyncio import AsyncSession
from dotenv import load_dotenv

from app.errors import AlreadyExistError, DataNotFoundError
from app.handler.dto import GetCodesPayload, URLPayload
from app.model.url import URLMapping
from app.repository.url import UrlRepository
from app.service.helper import HelperService
from app.service.shorten import ShortenerService
from app.cache import putCacheData

load_dotenv()

BASE_URL = os.getenv("BASE_URL")


class UrlService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.shortenService = ShortenerService()
        self.urlRepo = UrlRepository(db=db)
        self.helper = HelperService()


    async def checkForDuplicateShortCode(self, payload: URLPayload) -> str:
        payloadUrl = str(payload.url)
        urlData = await self.urlRepo.getByOriginalUrl(originalUrl=payloadUrl)
        shortUrlData = await self.urlRepo.getByShortCode(shortCode=payload.customName)

        if shortUrlData is None:
            if urlData:
                await self.urlRepo.updateShortCode(obj=urlData, shortCode=payload.customName)
                return f"{BASE_URL}/{payload.customName}"
            return None
        elif shortUrlData and shortUrlData.original_url != payloadUrl:
            raise AlreadyExistError(reason="URL Custom Name already existed, please try with other Custom Name")
        elif shortUrlData and shortUrlData.original_url == payloadUrl:
            return f"{BASE_URL}/{shortUrlData.short_code}"

    async def createShortenUrl(self, payload: URLPayload) -> str:
        payloadUrl = str(payload.url)

        if payload.customName:
            result = await self.checkForDuplicateShortCode(payload=payload)
            if result:
                await putCacheData(key=f"url:{payload.customName}", value=payloadUrl)
                return result
            
        existedUrl = await self.urlRepo.getByOriginalUrl(originalUrl=payloadUrl)
        if existedUrl:
            await putCacheData(key=f"url:{existedUrl.short_code}", value=existedUrl.original_url)
            return f"{BASE_URL}/{existedUrl.short_code}"

        shortenCode = self.shortenService.generateShortUrl(payloadUrl)
        existedUrl = await self.urlRepo.getByShortCode(shortCode=shortenCode)

        if existedUrl:
            self.shortenService.salt = self.shortenService.randomSuffix()
            shortenCode = self.shortenService.generateShortUrl(payloadUrl)

        newUrlData = await self.urlRepo.create(
            originalUrl=payloadUrl, shortCode=shortenCode
        )
        await putCacheData(
            key=f"url:{newUrlData.short_code}", value=newUrlData.original_url
        )

        self.shortenService.salt = ""
        return f"{BASE_URL}/{newUrlData.short_code}"

    async def getOriginalLink(self, shortenCode: str) -> str:
        urlData = await self.urlRepo.getByShortCode(shortCode=shortenCode)
        if urlData:
            await self.incrementClickCount(urlData=urlData)
            return urlData.original_url

    async def getUrlDataByShortenCode(self, shortenCode: str) -> URLMapping:
        return await self.urlRepo.getByShortCode(shortCode=shortenCode)

    async def incrementClickCount(self, urlData: URLMapping) -> None:
        await self.urlRepo.incrementClick(urlData)

    async def getUrlList(self, payload: GetCodesPayload) -> list[URLMapping]:
        dataList = await self.urlRepo.listUrls(offset=payload.page, limit=payload.limit)
        for urlData in dataList:
            urlData.created_at = self.helper.convertUtcToIst(urlData.created_at)
            urlData.updated_at = self.helper.convertUtcToIst(urlData.updated_at)
            urlData.last_accessed_at = self.helper.convertUtcToIst(
                urlData.last_accessed_at
            )
            urlData.analytics = f'{BASE_URL}/get-analytics/{urlData.short_code}'
            urlData.short_code = f"{BASE_URL}/{urlData.short_code}"
        return dataList

    async def getDailyClicksData(self, shortenCode: str):
        urlData = await self.urlRepo.getByShortCode(shortCode=shortenCode)
        if urlData:
            dataList = await self.urlRepo.getDailyClickAnalytics(obj=urlData)
            return [
                {
                    "date": date.strftime("%d/%m/%Y"),
                    "total_clicks": total_clicks,
                    "url": urlData.original_url,
                    "short_url": f"{BASE_URL}/{urlData.short_code}",
                }
                for date, total_clicks in dataList
            ]
        raise DataNotFoundError(reason="URL Data Not found")
