from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import List
import os


class Settings(BaseSettings):
    """应用配置类"""
    APP_NAME: str = "Stock Monitor System"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False

    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # 数据库配置
    MYSQL_HOST: str = "localhost"
    MYSQL_PORT: int = 3306
    MYSQL_USER: str = "root"
    MYSQL_PASSWORD: str = ""
    MYSQL_DB: str = "stock_monitor"

    @property
    def DATABASE_URL(self) -> str:
        return f"mysql+aiomysql://{self.MYSQL_USER}:{self.MYSQL_PASSWORD}@{self.MYSQL_HOST}:{self.MYSQL_PORT}/{self.MYSQL_DB}"

    # 安全配置 - 生产环境必须通过环境变量设置
    SECRET_KEY: str = "your-secret-key-change-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080  # 7天

    # CORS 配置 - 允许的前端源
    CORS_ORIGINS: str = "http://localhost:3001,http://localhost:3002,http://127.0.0.1:3001,http://127.0.0.1:3002"
    
    @property
    def cors_origins_list(self) -> List[str]:
        """解析 CORS 允许的源列表"""
        if self.DEBUG:
            return ["*"]  # 开发模式允许所有源
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

    # 定时任务配置
    STOCK_UPDATE_INTERVAL: int = 300  # 股票数据更新间隔（秒）
    MONITOR_CHECK_INTERVAL: int = 60  # 监测检查间隔（秒）

    # 缓存配置
    CACHE_TTL_REALTIME: int = 30  # 实时数据缓存时间（秒）
    CACHE_TTL_KLINE: int = 300  # K线数据缓存时间（秒）
    CACHE_TTL_FINANCIAL: int = 3600  # 财务数据缓存时间（秒）
    
    # 市场数据缓存配置（避免频繁调用 AkShare API）
    CACHE_TTL_MARKET_TRADING: int = 300  # 交易时间内市场数据缓存（秒），默认5分钟
    CACHE_TTL_MARKET_NON_TRADING: int = 7200  # 非交易时间市场数据缓存（秒），默认2小时
    CACHE_TTL_SECTORS: int = 1800  # 板块数据缓存（秒），默认30分钟
    CACHE_TTL_LHB: int = 3600  # 龙虎榜数据缓存（秒），默认1小时

    class Config:
        env_file = ".env"
        extra = "ignore"  # 忽略额外的环境变量


@lru_cache()
def get_settings() -> Settings:
    """获取配置单例"""
    settings = Settings()
    
    # 生产环境检查 SECRET_KEY
    if not settings.DEBUG and settings.SECRET_KEY == "your-secret-key-change-in-production-min-32-chars":
        import warnings
        warnings.warn(
            "警告：正在使用默认的 SECRET_KEY，生产环境请通过环境变量设置安全的密钥！",
            UserWarning
        )
    
    return settings
