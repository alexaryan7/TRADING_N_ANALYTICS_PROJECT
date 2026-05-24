from sqlalchemy import Column, Integer, String, Float, Boolean, Index
import logging
from src.core.database import Base

try:
    class Stock(Base):
        __tablename__ = "stocks"
        
        id = Column(Integer, primary_key=True, index=True)
        symbol = Column(String, unique=True, nullable=False)
        company_name = Column(String, nullable=False)
        current_price = Column(Float, nullable=False)
        is_active = Column(Boolean, default=True)

    Index('idx_stock_symbol', Stock.symbol)
    Index('idx_stock_active', Stock.is_active)
    
except Exception as e:
    logging.critical(f"Failed to define Stock model: {str(e)}")
    raise SystemExit("Critical database modeling error.")