from fastapi import HTTPException, status, Response, Request
from motor.motor_asyncio import AsyncIOMotorClient
import jwt
import logging
from src.core.security import verify_password, create_access_token, create_refresh_token
from src.core.config import settings
from src.auth.schemas import LoginRequest

async def process_login(credentials: LoginRequest, response: Response, db: AsyncIOMotorClient) -> str:
    try:
        user = await db.users.find_one({"email": credentials.email})
        if not user or not verify_password(credentials.password, user.get("password", "")):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="Invalid email or password."
            )

        user_id_str = str(user["_id"])
        role = user.get("role", "trader")
        access_token = create_access_token(data={"sub": user_id_str, "role": role})
        refresh_token = create_refresh_token(data={"sub": user_id_str})
        await db.users.update_one(
            {"_id": user_id_str},
            {"$addToSet": {"refresh_tokens": refresh_token}}
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,   
            secure=True,     
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return access_token

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Login process failed for {credentials.email}: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred during login.")

async def process_refresh(request: Request, response: Response, db: AsyncIOMotorClient) -> str:
    try:
        old_refresh_token = request.cookies.get("refresh_token")
        if not old_refresh_token:
            raise HTTPException(status_code=401, detail="Refresh token missing. Please log in.")

        try:
            payload = jwt.decode(old_refresh_token, settings.SECRET_KEY, algorithms=["HS256"])
            user_id = payload.get("sub")
            if payload.get("type") != "refresh":
                raise jwt.InvalidTokenError()
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Session expired. Please log in again.")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid session token.")

        user = await db.users.find_one({"_id": user_id, "refresh_tokens": old_refresh_token})
        if not user:
            response.delete_cookie("refresh_token")
            raise HTTPException(status_code=401, detail="Session revoked. Please log in.")

        role = user.get("role", "trader")

        new_access_token = create_access_token(data={"sub": user_id, "role": role})
        new_refresh_token = create_refresh_token(data={"sub": user_id})

        await db.users.update_one(
            {"_id": user_id},
            {
                "$pull": {"refresh_tokens": old_refresh_token},
                "$addToSet": {"refresh_tokens": new_refresh_token}
            }
        )

        response.set_cookie(
            key="refresh_token",
            value=new_refresh_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60
        )

        return new_access_token

    except HTTPException:
        raise
    except Exception as e:
        logging.error(f"Token refresh failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to refresh session.")

async def process_logout(request: Request, response: Response, db: AsyncIOMotorClient):
    try:
        refresh_token = request.cookies.get("refresh_token")
        
        if refresh_token:
            try:
                payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=["HS256"], options={"verify_exp": False})
                user_id = payload.get("sub")
                
                await db.users.update_one(
                    {"_id": user_id},
                    {"$pull": {"refresh_tokens": refresh_token}}
                )
            except Exception as e:
                logging.warning(f"Could not cleanly remove token from DB during logout: {str(e)}")

        response.delete_cookie("refresh_token")
        
    except Exception as e:
        logging.error(f"Logout error: {str(e)}")
        raise HTTPException(status_code=500, detail="An error occurred while logging out.")