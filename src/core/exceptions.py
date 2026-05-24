from fastapi import Request, HTTPException
import logging
from sqlalchemy.exc import SQLAlchemyError
from fastapi.responses import JSONResponse

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"unhandled system error on {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=500, content={"Success": False, "error": "Server Error"}
    )
    
async def sqlalchemy_exception_handler(request: Request, exc: SQLAlchemyError):
    logger.error(f"DB error on {request.method} {request.url}: {str(exc)}", exc_info=True)
    return JSONResponse(
        status_code=503, content={"Success": False, "error": "Unavailable"}
    )
    
async def custom_http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code, content={"Success": False, "error": exc.detail}
    )