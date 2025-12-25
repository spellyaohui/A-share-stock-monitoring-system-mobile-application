from sqlalchemy import Column, Integer, BigInteger, String, Text, Numeric, Boolean, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Monitor(Base):
    __tablename__ = "monitors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    price_min = Column(Numeric(10, 2))
    price_max = Column(Numeric(10, 2))
    rise_threshold = Column(Numeric(5, 2))
    fall_threshold = Column(Numeric(5, 2))
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    user = relationship("User", backref="monitors")
    stock = relationship("Stock", back_populates="monitors")
    notifications = relationship("Notification", back_populates="monitor", cascade="all, delete-orphan")

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    stock_id = Column(Integer, ForeignKey("stocks.id", ondelete="CASCADE"), nullable=False)
    monitor_id = Column(Integer, ForeignKey("monitors.id", ondelete="CASCADE"), nullable=False)
    type = Column(String(20))
    content = Column(Text)
    is_sent = Column(Boolean, default=False, index=True)
    sent_at = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())

    monitor = relationship("Monitor", back_populates="notifications")

class NotificationConfig(Base):
    __tablename__ = "notification_configs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    api_url = Column(String(500))
    api_headers = Column(JSON)
    api_method = Column(String(10), default="POST")
    api_body_template = Column(Text)
    is_enabled = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
