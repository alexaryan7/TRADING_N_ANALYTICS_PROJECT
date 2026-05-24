from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(..., min_length=8, description="Password must be at least 8 characters long")
    
class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    kyc_status: str
    message: Optional[str] = None
    
class KYCUploadResponse(BaseModel):
    success: bool
    message: str
    document_id: str