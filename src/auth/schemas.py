from pydantic import BaseModel, EmailStr
from typing import Optional

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    message: Optional[str] = "Authentication Successful"
    
class LogoutResponse(BaseModel):
    success: bool
    message: str