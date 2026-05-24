from fastapi import APIRouter, Depends, UploadFile, File, status
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.database import get_mongo_db
from src.core.dependencies import get_current_user
from src.users.schemas import UserRegister, UserResponse, KYCUploadResponse
from src.users.service import process_registration, process_kyc_upload

router = APIRouter(prefix="/api/users")

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    user_data: UserRegister,
    db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    new_user = await process_registration(user_data, db)
    return UserResponse(
        **new_user, 
        message="Registration successful"
    )

@router.post("/kyc/upload", response_model=KYCUploadResponse)
async def upload_kyc_document(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
    db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    document_id = await process_kyc_upload(current_user["user_id"], file, db)
    
    return KYCUploadResponse(
        success=True,
        message="KYC document uploaded successfully and is pending review.",
        document_id=document_id
    )