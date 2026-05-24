from fastapi import APIRouter, Depends, Response, Request
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.database import get_mongo_db
from src.auth.schemas import LoginRequest, TokenResponse, LogoutResponse
from src.auth.service import process_login, process_refresh, process_logout

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

@router.post("/login", response_model=TokenResponse)
async def login_user(
    credentials: LoginRequest,
    response: Response,
    db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    access_token = await process_login(credentials, response, db)
    return TokenResponse(access_token=access_token)

@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: Request,
    response: Response,
    db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    new_access_token = await process_refresh(request, response, db)
    return TokenResponse(
        access_token=new_access_token, 
        message="Session refreshed successfully."
    )

@router.post("/logout", response_model=LogoutResponse)
async def logout_user(
    request: Request,
    response: Response,
    db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    await process_logout(request, response, db)
    return LogoutResponse(success=True, message="Successfully logged out.")