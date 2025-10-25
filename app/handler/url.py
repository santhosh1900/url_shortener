from http import HTTPStatus
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import getSession
from app.cache import getCacheData
from app.errors import AlreadyExistError, DataNotFoundError, InvalidDataError
from app.handler.dto import GetCodesPayload, URLPayload
from app.service import UrlService
from app.database import asyncSession
from app.service.auth import AuthService

router = APIRouter(prefix="", tags=["URLs"])

async def backendTask(shortenCode: str) -> None:
    db = asyncSession()
    urlService = UrlService(db=db)
    urlData = await urlService.getUrlDataByShortenCode(shortenCode=shortenCode)
    if (urlData):
        await urlService.incrementClickCount(urlData)
    db.close()

@router.get("/")
async def getHome():
    return {
        "message": "Welcome to URL shortener"
    }

@router.post("/get-shorten-url", status_code=HTTPStatus.CREATED)
async def generateShortenUrl(payload: URLPayload, db: AsyncSession = Depends(getSession)):
    try:
        urlService = UrlService(db=db)
        shortenUrl = await urlService.createShortenUrl(payload=payload)
        return {
            "success": True,
            "url": shortenUrl,
        }
    except InvalidDataError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except AlreadyExistError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Unknown Error Occured, please try again latter"
        )
    
@router.post("/get-urls", status_code=HTTPStatus.OK,)
async def getCodes(payload: GetCodesPayload, db: AsyncSession = Depends(getSession), _: None = Depends(AuthService().getCurrentAdmin)):
    urlService = UrlService(db=db)
    return await urlService.getUrlList(payload=payload)

@router.get("/get-analytics/{shortenCode}", status_code=HTTPStatus.OK)
async def getAnalytics(
    shortenCode: str,
    db: AsyncSession = Depends(getSession)
):
    try:
        urlService = UrlService(db=db)
        return await urlService.getDailyClicksData(shortenCode=shortenCode)
    except DataNotFoundError as e:
        raise HTTPException(
            status_code=404,
            detail=e
        )
    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail="Unknown Error Occured, please try again latter"
        )

@router.get("/{shortenCode}")
async def getUrl(
    shortenCode: str,
    backgroundTasks: BackgroundTasks,
    db: AsyncSession = Depends(getSession)
):
    url = await getCacheData(key=f'url:{shortenCode}')
    if url:
        backgroundTasks.add_task(backendTask, shortenCode)
        return RedirectResponse(url=url, status_code=HTTPStatus.TEMPORARY_REDIRECT)
    else:
        urlService = UrlService(db=db)
        url = await urlService.getOriginalLink(shortenCode=shortenCode)
        if url:
            return RedirectResponse(url=url, status_code=HTTPStatus.TEMPORARY_REDIRECT)
    raise HTTPException(
        status_code=404,
        detail=f"URL not found"
    )

