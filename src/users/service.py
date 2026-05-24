from fastapi import HTTPException, status, UploadFile
from motor.motor_asyncio import AsyncIOMotorClient
import logging
import os
import uuid
from datetime import datetime, timezone
from src.core.security import get_password_hash
from src.users.schemas import UserRegister

MAX_FILE_SIZE =  10 * 1024 * 1024  
ALLOWED_MIME_TYPES = ["image/jpeg", "image/png", "application/pdf"]

async def process_registration(user_data: UserRegister, db: AsyncIOMotorClient) -> dict:
    """Registers a new user in MongoDB."""
    try:
        existing_user = await db.users.find_one({"email": user_data.email})
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="A user with this email already exists."
            )

        new_user_id = str(uuid.uuid4())
        new_user = {
            "_id": new_user_id,
            "email": user_data.email,
            "password": get_password_hash(user_data.password),
            "role": "trader",  
            "kyc_status": "pending",
            "refresh_tokens": [],
            "created_at": datetime.now(timezone.utc)
        }

        await db.users.insert_one(new_user)
        
        return {
            "id": new_user_id,
            "email": new_user["email"],
            "role": new_user["role"],
            "kyc_status": new_user["kyc_status"]
        }

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Registration failed for {user_data.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to register user.")

async def process_kyc_upload(user_id: str, file: UploadFile, db: AsyncIOMotorClient) -> str:
    try:
        if file.content_type not in ALLOWED_MIME_TYPES:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Invalid file type. Only JPG, PNG, and PDF are allowed."
            )

        contents = await file.read()
        if len(contents) > MAX_FILE_SIZE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="File exceeds the maximum limit of 5MB."
            )

        upload_dir = os.path.join(os.getcwd(), "uploads", "kyc")
        os.makedirs(upload_dir, exist_ok=True)

        file_extension = file.filename.split(".")[-1]
        doc_id = str(uuid.uuid4())
        safe_filename = f"{user_id}_{doc_id}.{file_extension}"
        file_path = os.path.join(upload_dir, safe_filename)

        with open(file_path, "wb") as f:
            f.write(contents)

        document_metadata = {
            "_id": doc_id,
            "user_id": user_id,
            "original_filename": file.filename,
            "stored_path": file_path,
            "mime_type": file.content_type,
            "uploaded_at": datetime.now(timezone.utc),
            "status": "under_review"
        }
        await db.kyc_documents.insert_one(document_metadata)

        await db.users.update_one(
            {"_id": user_id},
            {"$set": {"kyc_status": "uploaded"}}
        )

        return doc_id

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"KYC upload failed for user {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to process document upload.")