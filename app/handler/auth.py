from fastapi import APIRouter, HTTPException, status

from app.handler.dto import LoginPayload, TokenResponse
from app.service.auth import AuthService

router = APIRouter(prefix="/admin-login", tags=["Auth"])

@router.post("", response_model=TokenResponse)
async def login(payload: LoginPayload):
    authService = AuthService()

    if payload.username != authService.username or payload.password != authService.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    token = authService.createAccessToken({"sub": payload.username})
    return {"access_token": token, "token_type": "bearer"}