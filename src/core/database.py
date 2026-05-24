from sqlalchemy.orm import declarative_base
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import HTTPException
import logging
from src.core.config import settings
from motor.motor_asyncio import AsyncIOMotorClient

try:
    engine = create_async_engine(
        settings.POSTGRE_URL,
        pool_size= 50,
        max_overflow= 10
    )
    AsyncSessionLocal = async_sessionmaker(
        bind=engine
    )
    Base = declarative_base()
except Exception as e:
    logging.critical()
    raise SystemExit("")

async def get_postgres_session():
    session = AsyncSessionLocal()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise
    finally:
        session.close()
        
try:
    mongo_client = AsyncIOMotorClient(settings.MONGO_URL)
    mongo_db = mongo_client[settings.MONGO_DB_NAME]
except Exception as e:
    logging.critical()
    raise SystemExit("NoSQL databse connection failed")

async def get_mongo_db():
    try:
        yield get_mongo_db
    except Exception as e:
        logging.error("Mongo DB error")
        raise HTTPException(status_code=500, detail="Database failed")