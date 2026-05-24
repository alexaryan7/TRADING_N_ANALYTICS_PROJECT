from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import SQLAlchemyError
from fastapi.exceptions import RequestValidationError
import contextlib
import logging
from src.core.config import settings
from src.core.database import engine, Base
from src.core.exceptions import global_exception_handler, sqlalchemy_exception_handler, custom_http_exception_handler
from src.auth.router import router as auth_router
from src.users.router import router as users_router
from src.stocks.router import router as stocks_router
from src.trading.router import router as trading_router
from src.market.router import router as market_router

@contextlib.asynccontextmanager
async def lifespan(app: FastAPI):
    logging.info("Starting up Trading Platform Engine...")
    try:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        logging.info("PostgreSQL tables verified/created successfully.")
    except Exception as e:
        logging.critical(f"Database initialization failed: {str(e)}")
        
    yield 
    
    logging.info("Shutting down Trading Platform Engine...")
    await engine.dispose()

app = FastAPI(
    title=settings.PROJECT_NAME,
    description="Real-Time Trading & Analytics Platform",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True, 
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(SQLAlchemyError, sqlalchemy_exception_handler)

app.include_router(auth_router)
app.include_router(users_router)
app.include_router(stocks_router)
app.include_router(trading_router)
app.include_router(market_router)

@app.get("/health")
async def health_check():
    return {"status": "online", "system": settings.PROJECT_NAME}