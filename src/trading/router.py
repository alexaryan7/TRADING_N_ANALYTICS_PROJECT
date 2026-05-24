from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession
from motor.motor_asyncio import AsyncIOMotorClient
from src.core.database import get_postgres_session, get_mongo_db
from src.core.dependencies import get_current_user
from src.trading.schemas import OrderCreate, OrderResponse, PortfolioResponse
from src.trading.service import execute_trade, fetch_trade_history, fetch_portfolio

router = APIRouter(prefix="/api/trading")

@router.post("/order", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def place_order(
    order_in: OrderCreate,
    current_user: dict = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_postgres_session),
    mongo_db: AsyncIOMotorClient = Depends(get_mongo_db)
):
    return await execute_trade(order_in, current_user["user_id"], pg_db, mongo_db)

@router.get("/portfolio", response_model=list[PortfolioResponse])
async def get_portfolio(
    current_user: dict = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_postgres_session)
):
    return await fetch_portfolio(current_user["user_id"], pg_db)

@router.get("/history", response_model=list[OrderResponse])
async def get_transaction_history(
    limit: int = Query(50, ge=1, le=100, description="Max 100 per page"),
    offset: int = Query(0, ge=0),
    current_user: dict = Depends(get_current_user),
    pg_db: AsyncSession = Depends(get_postgres_session)
):
    return await fetch_trade_history(current_user["user_id"], limit, offset, pg_db)