from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status
import logging
from src.stocks.models import Stock
from src.stocks.schemas import StockCreate

async def create_new_stock(stock_data: StockCreate, db: AsyncSession) -> Stock:
    async with db.begin(): 
        try:
            new_stock = Stock(
                symbol=stock_data.symbol.upper(),
                company_name=stock_data.company_name,
                current_price=stock_data.current_price
            )
            
            db.add(new_stock)
            await db.flush() 
            
            return new_stock
            
        except IntegrityError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Stock symbol '{stock_data.symbol.upper()}' already exists in the system."
            )
        except Exception as e:
            logging.error(f"Error creating stock {stock_data.symbol}: {str(e)}")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create stock."
            )

async def fetch_all_active_stocks(db: AsyncSession) -> list[Stock]:
    try:
        query = select(Stock).where(Stock.is_active == True).order_by(Stock.symbol)
        result = await db.execute(query)
        
        return list(result.scalars().all())
    except Exception as e:
        logging.error(f"Error fetching stocks: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve market data."
        )