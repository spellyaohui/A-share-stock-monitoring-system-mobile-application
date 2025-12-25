from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class StockResponse(BaseModel):
    id: int
    code: str
    name: str
    market: Optional[str] = None
    industry: Optional[str] = None
    full_code: Optional[str] = None

    class Config:
        from_attributes = True

class StockSearch(BaseModel):
    id: int
    code: str
    name: str

    class Config:
        from_attributes = True

class StockRealtime(BaseModel):
    stock_id: int
    code: str
    name: str
    price: float
    open: float
    high: float
    low: float
    close: float
    yesterday_close: float
    volume: int
    amount: float
    change: float
    timestamp: str

class MonitorCreate(BaseModel):
    stock_id: int
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rise_threshold: Optional[float] = None
    fall_threshold: Optional[float] = None

class MonitorUpdate(BaseModel):
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rise_threshold: Optional[float] = None
    fall_threshold: Optional[float] = None
    is_active: Optional[bool] = None

class MonitorResponse(BaseModel):
    id: int
    stock_id: int
    price_min: Optional[float] = None
    price_max: Optional[float] = None
    rise_threshold: Optional[float] = None
    fall_threshold: Optional[float] = None
    is_active: bool
    created_at: datetime
    stock: Optional[StockResponse] = None

    class Config:
        from_attributes = True

class MonitorWithRealtime(MonitorResponse):
    current_price: Optional[float] = None
    change: Optional[float] = None
