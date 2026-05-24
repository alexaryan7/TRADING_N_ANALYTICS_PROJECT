from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import SQLAlchemyError
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import HTTPException, status
import logging
from datetime import datetime, timezone
from src.trading.models import Order, Portfolio
from src.trading.schemas import OrderCreate

async def execute_trade(
    order_data: OrderCreate, 
    user_id: str, 
    pg_db: AsyncSession, 
    mongo_db: AsyncIOMotorClient
) -> Order:
    async with pg_db.begin():
        try:
            new_order = Order(
                user_id=user_id,
                symbol=order_data.symbol.upper(),
                order_type=order_data.order_type,
                quantity=order_data.quantity,
                price=order_data.price,
                status="executed"
            )
            pg_db.add(new_order)
            await pg_db.flush() 
            query = select(Portfolio).where(
                Portfolio.user_id == user_id, 
                Portfolio.symbol == order_data.symbol.upper()
            )
            result = await pg_db.execute(query)
            portfolio_item = result.scalar_one_or_none()

            if order_data.order_type == "buy":
                if portfolio_item:
                    portfolio_item.quantity += order_data.quantity
                else:
                    new_portfolio = Portfolio(
                        user_id=user_id, 
                        symbol=order_data.symbol.upper(), 
                        quantity=order_data.quantity
                    )
                    pg_db.add(new_portfolio)
            
            elif order_data.order_type == "sell":
                if not portfolio_item or portfolio_item.quantity < order_data.quantity:
                    raise ValueError(f"Insufficient shares. You only own {portfolio_item.quantity if portfolio_item else 0} shares of {order_data.symbol.upper()}.")
                
                portfolio_item.quantity -= order_data.quantity

            log_entry = {
                "order_id": new_order.id,
                "user_id": user_id,
                "action": order_data.order_type,
                "symbol": order_data.symbol.upper(),
                "quantity": order_data.quantity,
                "price": order_data.price,
                "timestamp": datetime.now(timezone.utc)
            }
            await mongo_db.trade_logs.insert_one(log_entry)
            return new_order

        except ValueError as ve:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(ve))
        except SQLAlchemyError as db_err:
            logging.error(f"PostgreSQL Transaction failed for user {user_id}: {str(db_err)}")
            raise HTTPException(status_code=500, detail="Trade execution failed due to database constraint.")
        except Exception as e:
            logging.error(f"Unexpected error during trade execution: {str(e)}")
            raise HTTPException(status_code=500, detail="An unexpected error occurred processing your trade.")

async def fetch_trade_history(user_id: str, limit: int, offset: int, pg_db: AsyncSession) -> list[Order]:
    try:
        safe_limit = min(limit, 100)
        
        query = select(Order).where(Order.user_id == user_id).order_by(Order.created_at.desc()).limit(safe_limit).offset(offset)
        result = await pg_db.execute(query)
        return list(result.scalars().all())
    except Exception as e:
        logging.error(f"Error fetching history for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch transaction history.")

async def fetch_portfolio(user_id: str, pg_db: AsyncSession) -> list[Portfolio]:
    try:
        query = select(Portfolio).where(Portfolio.user_id == user_id, Portfolio.quantity > 0)
        result = await pg_db.execute(query)
        return list(result.scalars().all())
    except Exception as e:
        logging.error(f"Error fetching portfolio for {user_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch portfolio holdings.")