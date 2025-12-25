from sqlalchemy import Column, Integer, String, Date, Numeric, BigInteger, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Stock(Base):
    __tablename__ = "stocks"

    id = Column(Integer, primary_key=True, index=True)
    code = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(50), nullable=False, index=True)
    market = Column(String(10))
    industry = Column(String(50))
    full_code = Column(String(20), index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    monitors = relationship("Monitor", back_populates="stock")

class StockDaily(Base):
    __tablename__ = "stock_daily"

    id = Column(Integer, primary_key=True, index=True)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    trade_date = Column(Date, nullable=False, index=True)
    open = Column(Numeric(10, 2))
    high = Column(Numeric(10, 2))
    low = Column(Numeric(10, 2))
    close = Column(Numeric(10, 2))
    volume = Column(BigInteger)
    amount = Column(Numeric(20, 2))
    turnover_rate = Column(Numeric(5, 2))
