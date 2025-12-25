"""
市场数据缓存服务
定时获取全市场数据并缓存到数据库，避免频繁调用 AkShare API
支持可配置的缓存时间，交易时间和非交易时间使用不同的缓存策略
"""
import asyncio
from datetime import datetime, time, timedelta
from typing import Optional, Dict, List, Any
import akshare as ak
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
import json

from app.core.logging import get_logger
from app.config import get_settings

logger = get_logger(__name__)

# 线程池用于执行同步的 AkShare 调用
executor = ThreadPoolExecutor(max_workers=2)


class MarketCacheService:
    """市场数据缓存服务"""
    
    def __init__(self):
        # 内存缓存
        self._realtime_cache: Dict[str, Any] = {}
        self._cache_time: Optional[datetime] = None
        
        # 从配置获取缓存时间
        settings = get_settings()
        self._cache_ttl_trading = settings.CACHE_TTL_MARKET_TRADING  # 交易时间缓存（默认5分钟）
        self._cache_ttl_non_trading = settings.CACHE_TTL_MARKET_NON_TRADING  # 非交易时间缓存（默认2小时）
        
        # 全市场数据缓存
        self._market_data: Optional[pd.DataFrame] = None
        self._market_data_time: Optional[datetime] = None
        
        # 板块数据缓存
        self._sectors_cache: Dict[str, Any] = {}
        self._sectors_cache_time: Optional[datetime] = None
        self._sectors_ttl = settings.CACHE_TTL_SECTORS  # 板块缓存（默认30分钟）
        
        # 龙虎榜数据缓存
        self._lhb_cache: List[Dict] = []
        self._lhb_cache_time: Optional[datetime] = None
        self._lhb_ttl = settings.CACHE_TTL_LHB  # 龙虎榜缓存（默认1小时）
        
        logger.info(f"市场缓存服务初始化: 交易时间TTL={self._cache_ttl_trading}秒, 非交易时间TTL={self._cache_ttl_non_trading}秒")
        
    async def _run_in_executor(self, func, *args):
        """在线程池中运行同步函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(executor, func, *args)
    
    def is_trading_time(self) -> bool:
        """判断是否在交易时间"""
        now = datetime.now()
        # 周末不交易
        if now.weekday() >= 5:
            return False
        
        current_time = now.time()
        # 上午 9:15 - 11:30，下午 13:00 - 15:00
        morning_start = time(9, 15)
        morning_end = time(11, 30)
        afternoon_start = time(13, 0)
        afternoon_end = time(15, 0)
        
        return (morning_start <= current_time <= morning_end or 
                afternoon_start <= current_time <= afternoon_end)
    
    async def refresh_market_data(self) -> bool:
        """
        刷新全市场数据
        建议在以下时间调用：
        - 开盘前 9:00
        - 盘中每 5 分钟（如果需要实时数据）
        - 收盘后 15:30
        """
        try:
            logger.info("开始刷新全市场数据...")
            start_time = datetime.now()
            
            # 获取全市场实时数据
            self._market_data = await self._run_in_executor(ak.stock_zh_a_spot_em)
            self._market_data_time = datetime.now()
            
            # 更新内存缓存
            if self._market_data is not None and not self._market_data.empty:
                self._realtime_cache = {}
                for _, row in self._market_data.iterrows():
                    code = row['代码']
                    self._realtime_cache[code] = {
                        'code': code,
                        'name': row['名称'],
                        'price': row['最新价'],
                        'change': row['涨跌额'],
                        'change_percent': row['涨跌幅'],
                        'open': row['今开'],
                        'high': row['最高'],
                        'low': row['最低'],
                        'pre_close': row['昨收'],
                        'volume': row['成交量'],
                        'amount': row['成交额'],
                        'amplitude': row['振幅'],
                        'turnover_rate': row['换手率'],
                        'pe_ratio': row['市盈率-动态'],
                        'pb_ratio': row['市净率'],
                        'total_value': row['总市值'],
                        'circulating_value': row['流通市值'],
                        'volume_ratio': row['量比'],
                        'rise_speed': row['涨速'],
                        'change_5min': row['5分钟涨跌'],
                        'change_60day': row['60日涨跌幅'],
                        'change_ytd': row['年初至今涨跌幅'],
                    }
                self._cache_time = datetime.now()
            
            elapsed = (datetime.now() - start_time).total_seconds()
            logger.info(f"全市场数据刷新完成，共 {len(self._realtime_cache)} 只股票，耗时 {elapsed:.2f} 秒")
            return True
            
        except Exception as e:
            logger.error(f"刷新全市场数据失败: {e}")
            return False
    
    def get_stock_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        从缓存获取单只股票的实时数据
        如果缓存过期或不存在，返回 None
        """
        if not self._realtime_cache:
            return None
        
        # 使用统一的缓存有效性检查
        if not self.is_cache_valid():
            return None
        
        return self._realtime_cache.get(stock_code)
    
    def get_market_stats(self) -> Dict[str, Any]:
        """获取市场统计数据"""
        if self._market_data is None or self._market_data.empty:
            return {}
        
        df = self._market_data
        total = len(df)
        up = len(df[df['涨跌幅'] > 0])
        down = len(df[df['涨跌幅'] < 0])
        flat = total - up - down
        
        # 涨跌停统计（涨跌幅超过 9.5% 视为涨跌停）
        limit_up = len(df[df['涨跌幅'] >= 9.5])
        limit_down = len(df[df['涨跌幅'] <= -9.5])
        
        return {
            'total_stocks': total,
            'up_stocks': up,
            'down_stocks': down,
            'flat_stocks': flat,
            'limit_up': limit_up,
            'limit_down': limit_down,
            'up_ratio': round(up / total * 100, 2) if total > 0 else 0,
            'down_ratio': round(down / total * 100, 2) if total > 0 else 0,
            'cache_time': self._cache_time.isoformat() if self._cache_time else None
        }
    
    def get_top_stocks(self, by: str = 'amount', limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取排行榜数据
        by: amount(成交额), change(涨幅), turnover(换手率)
        """
        if self._market_data is None or self._market_data.empty:
            return []
        
        df = self._market_data
        
        column_map = {
            'amount': '成交额',
            'change': '涨跌幅',
            'turnover': '换手率',
            'volume': '成交量'
        }
        
        sort_column = column_map.get(by, '成交额')
        ascending = False  # 默认降序
        
        if by == 'change_down':  # 跌幅榜
            sort_column = '涨跌幅'
            ascending = True
        
        sorted_df = df.nlargest(limit, sort_column) if not ascending else df.nsmallest(limit, sort_column)
        
        return sorted_df[['代码', '名称', '最新价', '涨跌幅', '成交额', '换手率']].to_dict('records')
    
    def is_cache_valid(self) -> bool:
        """检查缓存是否有效"""
        if not self._cache_time:
            return False
        
        elapsed = (datetime.now() - self._cache_time).total_seconds()
        
        # 根据是否交易时间使用不同的缓存策略
        if self.is_trading_time():
            # 交易时间内使用较短的缓存时间
            return elapsed <= self._cache_ttl_trading
        else:
            # 非交易时间使用较长的缓存时间
            return elapsed <= self._cache_ttl_non_trading
    
    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息"""
        is_trading = self.is_trading_time()
        current_ttl = self._cache_ttl_trading if is_trading else self._cache_ttl_non_trading
        
        elapsed = 0
        remaining = current_ttl
        if self._cache_time:
            elapsed = int((datetime.now() - self._cache_time).total_seconds())
            remaining = max(0, current_ttl - elapsed)
        
        return {
            'cache_time': self._cache_time.isoformat() if self._cache_time else None,
            'stock_count': len(self._realtime_cache),
            'is_valid': self.is_cache_valid(),
            'is_trading_time': is_trading,
            'cache_ttl': current_ttl,
            'cache_elapsed': elapsed,
            'cache_remaining': remaining,
            'ttl_trading': self._cache_ttl_trading,
            'ttl_non_trading': self._cache_ttl_non_trading
        }
    
    # 板块数据缓存方法
    def is_sectors_cache_valid(self) -> bool:
        """检查板块缓存是否有效"""
        if not self._sectors_cache_time or not self._sectors_cache:
            return False
        elapsed = (datetime.now() - self._sectors_cache_time).total_seconds()
        return elapsed <= self._sectors_ttl
    
    def get_sectors_cache(self) -> Optional[Dict[str, Any]]:
        """获取板块缓存数据"""
        if self.is_sectors_cache_valid():
            return self._sectors_cache
        return None
    
    def set_sectors_cache(self, data: Dict[str, Any]):
        """设置板块缓存数据"""
        self._sectors_cache = data
        self._sectors_cache_time = datetime.now()
        logger.info(f"板块数据已缓存，TTL={self._sectors_ttl}秒")
    
    # 龙虎榜数据缓存方法
    def is_lhb_cache_valid(self) -> bool:
        """检查龙虎榜缓存是否有效"""
        if not self._lhb_cache_time or not self._lhb_cache:
            return False
        elapsed = (datetime.now() - self._lhb_cache_time).total_seconds()
        return elapsed <= self._lhb_ttl
    
    def get_lhb_cache(self) -> Optional[List[Dict]]:
        """获取龙虎榜缓存数据"""
        if self.is_lhb_cache_valid():
            return self._lhb_cache
        return None
    
    def set_lhb_cache(self, data: List[Dict]):
        """设置龙虎榜缓存数据"""
        self._lhb_cache = data
        self._lhb_cache_time = datetime.now()
        logger.info(f"龙虎榜数据已缓存，TTL={self._lhb_ttl}秒")


# 全局单例
market_cache = MarketCacheService()
