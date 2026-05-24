from pydantic import BaseModel, Field
from datetime import datetime

class OrderCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10)
    order_type: str = Field(..., pattern="^(buy|sell)$")
    quantity: int = Field(..., gt=0, description="Quantity must be positive")
    price: float = Field(..., gt=0.0, description="Price must be positive")

class OrderResponse(BaseModel):
    id: int
    symbol: str
    order_type: str
    quantity: int
    price: float
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

class PortfolioResponse(BaseModel):
    symbol: str
    quantity: int

    class Config:
        from_attributes = True