from pydantic import BaseModel, Field

class StockCreate(BaseModel):
    symbol: str = Field(..., min_length=1, max_length=10, description="e.g., AAPL, TSLA")
    company_name: str = Field(..., min_length=2, max_length=100)
    current_price: float = Field(..., gt=0.0, description="Starting price must be > 0")

class StockResponse(BaseModel):
    id: int
    symbol: str
    company_name: str
    current_price: float
    is_active: bool

    class Config:
        from_attributes = True 