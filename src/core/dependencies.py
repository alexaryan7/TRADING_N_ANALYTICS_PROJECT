from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt
import logging
from src.core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

async def get_current_user(token: str=Depends(oauth2_scheme)) -> dict:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail = "Could not validate Credentials",
        headers={"WWW-Authenticate":"Bearer"}
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, settings.ALGORITHM)
        
        user_id: str = payload.get("sub")
        role: str = payload.get("role")
        token_type: str = payload.get("type")
        
        if token_type != "access":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail = "Invalid Token",
                headers={"WWW-Authenticate":"Bearer"}
            )
        if user_id is None or role is None:
            raise credentials_exception
        
        return {"user_id": user_id, "role": role}
    
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Expired Access Token"
        )
    except jwt.InvalidTokenError as e:
        logging.warning("Invalid JWT token attempt")
        raise credentials_exception
    except HTTPException:
        raise
    except Exception as e:
        logging.error("Error")
        raise HTTPException(status_code=500, detail="Internal Auth Error")
    
def required_role(required_roles: list[str]):
    def role_checker(current_user: dict = Depends (get_current_user)) -> dict:
        try:
            if current_user.get("role") not in required_roles:
                logging.warning("Unauthorized access")
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail = "No permission"
                )
            return current_user
        except HTTPException:
            raise
        except Exception as e:
            logging.error("Failed")
            raise HTTPException(status_code=500, detail="Permission Failed")
    return role_checker