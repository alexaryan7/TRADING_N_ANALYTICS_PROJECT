from passlib.context import CryptContext
import jwt
from datetime import datetime, timedelta, timezone
import logging
from src.core.config import settings
from fastapi import HTTPException

try:
    get_context = CryptContext(schemes=["bcrypt"], deprecated = "auto")
except Exception as e:
    logging.critical()
    raise SystemExit()

def verify_password(plain_password: str, hashed_password: str):
    try:
        return get_context.verify(plain_password, hashed_password)
    except Exception as e:
        logging.error("Error verifying password")
        return False

def get_password_hash(password: str) -> str:
    try:
        return get_context.hash(password)
    except Exception as e:
        logging.error("Error hashing password")
        raise HTTPException(status_code=500, detail="Internal Error")
    
def create_access_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "access"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt
    except Exception as e:
        logging.error("Failed to create Access token")
        raise HTTPException(status_code=500, detail="Token Generation failure")
    
def create_refresh_token(data: dict) -> str:
    try:
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire, "type": "refresh"})
        
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, settings.ALGORITHM)
        return encoded_jwt
    except:
        logging.error("Failed to create refresh token")
        raise HTTPException(status_code=500, detail="Token Generation failure")
    