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
            raw_data = await self._run_in_executor(ak.stock_zh_a_spot_em)
            self._market_data_time = datetime.now()
            
            # 更新内存缓存
            if raw_data is not None and not raw_data.empty:
                self._realtime_cache = {}
                
                # 数据清洗：将 '-' 和 NaN 替换为 0
                df = raw_data.copy()
                numeric_columns = ['最新价', '涨跌额', '涨跌幅', '今开', '最高', '最低', '昨收', 
                                   '成交量', '成交额', '振幅', '换手率', '市盈率-动态', '市净率',
                                   '总市值', '流通市值', '量比', '涨速', '5分钟涨跌', '60日涨跌幅', '年初至今涨跌幅']
                
                for col in numeric_columns:
                    if col in df.columns:
                        # 将 '-' 替换为 NaN，然后填充为 0
                        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                
                # 非交易时间处理：如果最新价为0但昨收有值，使用昨收作为最新价
                mask = (df['最新价'] == 0) & (df['昨收'] > 0)
                df.loc[mask, '最新价'] = df.loc[mask, '昨收']
                df.loc[mask, '涨跌幅'] = 0  # 非交易时间涨跌幅为0
                df.loc[mask, '涨跌额'] = 0
                
                # 保存清洗后的数据
                self._market_data = df
                
                for _, row in df.iterrows():
                    code = row['代码']
                    self._realtime_cache[code] = {
                        'code': code,
                        'name': row['名称'],
                        'price': float(row.get('最新价', 0) or 0),
                        'change': float(row.get('涨跌额', 0) or 0),
                        'change_percent': float(row.get('涨跌幅', 0) or 0),
                        'open': float(row.get('今开', 0) or 0),
                        'high': float(row.get('最高', 0) or 0),
                        'low': float(row.get('最低', 0) or 0),
                        'pre_close': float(row.get('昨收', 0) or 0),
                        'volume': int(row.get('成交量', 0) or 0),
                        'amount': float(row.get('成交额', 0) or 0),
                        'amplitude': float(row.get('振幅', 0) or 0),
                        'turnover_rate': float(row.get('换手率', 0) or 0),
                        'pe_ratio': float(row.get('市盈率-动态', 0) or 0),
                        'pb_ratio': float(row.get('市净率', 0) or 0),
                        'total_value': float(row.get('总市值', 0) or 0),
                        'circulating_value': float(row.get('流通市值', 0) or 0),
                        'volume_ratio': float(row.get('量比', 0) or 0),
                        'rise_speed': float(row.get('涨速', 0) or 0),
                        'change_5min': float(row.get('5分钟涨跌', 0) or 0),
                        'change_60day': float(row.get('60日涨跌幅', 0) or 0),
                        'change_ytd': float(row.get('年初至今涨跌幅', 0) or 0),
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
        import numpy as np
        
        if self._market_data is None or self._market_data.empty:
            return {}
        
        df = self._market_data.copy()
        
        # 数据清洗
        df['涨跌幅'] = pd.to_numeric(df['涨跌幅'], errors='coerce').fillna(0)
        df['涨跌幅'] = df['涨跌幅'].replace([np.inf, -np.inf], 0)
        df['最新价'] = pd.to_numeric(df['最新价'], errors='coerce').fillna(0)
        
        # 过滤掉没有有效价格的股票
        df = df[df['最新价'] > 0]
        
        if df.empty:
            return {}
        
        total = len(df)
        up = len(df[df['涨跌幅'] > 0])
        down = len(df[df['涨跌幅'] < 0])
        flat = total - up - down
        
        # 涨跌停统计（涨跌幅超过 9.5% 视为涨跌停）
        limit_up = len(df[df['涨跌幅'] >= 9.5])
        limit_down = len(df[df['涨跌幅'] <= -9.5])
        
        # 确保所有数值都是 Python 原生类型
        return {
            'total_stocks': int(total),
            'up_stocks': int(up),
            'down_stocks': int(down),
            'flat_stocks': int(flat),
            'limit_up': int(limit_up),
            'limit_down': int(limit_down),
            'up_ratio': float(round(up / total * 100, 2)) if total > 0 else 0.0,
            'down_ratio': float(round(down / total * 100, 2)) if total > 0 else 0.0,
            'cache_time': self._cache_time.isoformat() if self._cache_time else None
        }
    
    def get_top_stocks(self, by: str = 'amount', limit: int = 10) -> List[Dict[str, Any]]:
        """
        获取排行榜数据
        by: amount(成交额), change(涨幅), turnover(换手率)
        """
        import math
        import numpy as np
        
        def clean_value(val):
            """清理单个值中的 NaN 和 Inf"""
            if isinstance(val, (float, np.floating)):
                if math.isnan(val) or math.isinf(val):
                    return 0
                return float(val)
            elif isinstance(val, np.integer):
                return int(val)
            return val
        
        def clean_record(record):
            """清理记录中的所有值"""
            return {k: clean_value(v) for k, v in record.items()}
        
        if self._market_data is None or self._market_data.empty:
            return []
        
        df = self._market_data.copy()
        
        # 数据清洗
        numeric_columns = ['成交额', '涨跌幅', '换手率', '成交量', '最新价', '总市值']
        for col in numeric_columns:
            if col in df.columns:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
                # 替换 inf 值
                df[col] = df[col].replace([np.inf, -np.inf], 0)
        
        # 过滤掉没有有效价格的股票（价格为0或NaN的）
        df = df[df['最新价'] > 0]
        
        if df.empty:
            return []
        
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
        
        # 非交易时间特殊处理：如果成交额全为0，按市值排序
        if not self.is_trading_time() and by == 'amount':
            if df['成交额'].sum() == 0 and '总市值' in df.columns:
                sort_column = '总市值'
                logger.info("非交易时间，成交额为0，改用市值排序")
        
        try:
            sorted_df = df.nlargest(limit, sort_column) if not ascending else df.nsmallest(limit, sort_column)
            records = sorted_df[['代码', '名称', '最新价', '涨跌幅', '成交额', '换手率']].to_dict('records')
            # 清理每条记录中的 NaN 值
            return [clean_record(r) for r in records]
        except Exception as e:
            logger.error(f"获取排行榜数据失败: {e}")
            return []
    
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
