from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.core.database import get_postgres_session
from src.core.dependencies import get_current_user, require_role
from src.stocks.schemas import StockCreate, StockResponse
from src.stocks.service import create_new_stock, fetch_all_active_stocks

router = APIRouter(prefix="/api/stocks")

@router.post("/", response_model=StockResponse, status_code=status.HTTP_201_CREATED)
async def add_stock(
    stock_in: StockCreate,
    current_admin: dict = Depends(require_role(["admin"])),
    db: AsyncSession = Depends(get_postgres_session)
):
    return await create_new_stock(stock_in, db)

@router.get("/", response_model=list[StockResponse])
async def get_stocks(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_postgres_session)
):
    return await fetch_all_active_stocks(db)