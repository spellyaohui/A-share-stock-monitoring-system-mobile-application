"""
数据获取服务
统一管理多个数据源，提供数据获取的统一接口
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from app.services.stock_api import stock_api_service
from app.services.akshare_api import akshare_service
from app.core.logging import get_logger

logger = get_logger(__name__)


class DataFetcher:
    """数据获取服务类 - 统一管理多个数据源"""
    
    def __init__(self):
        self.primary_source = stock_api_service  # 主数据源：东方财富
        self.backup_source = akshare_service     # 备用数据源：AkShare
        self.cache = {}
        self.cache_ttl = 60  # 通用缓存60秒
        self.monitor_cache_ttl = 10  # 监测行情缓存10秒（更实时）
    
    def _is_cache_valid(self, key: str) -> bool:
        """检查缓存是否有效"""
        if key not in self.cache:
            return False
        cache_time, _ = self.cache[key]
        return (datetime.now() - cache_time).total_seconds() < self.cache_ttl
    
    def _get_cache(self, key: str) -> Optional[Any]:
        """获取缓存数据"""
        if self._is_cache_valid(key):
            _, data = self.cache[key]
            return data
        return None
    
    def _set_cache(self, key: str, data: Any):
        """设置缓存数据"""
        self.cache[key] = (datetime.now(), data)
    
    async def get_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取实时行情 - 优先使用市场缓存
        
        Args:
            stock_code: 股票代码
            
        Returns:
            实时行情数据
        """
        # 1. 优先从市场缓存获取（最快）
        try:
            from app.services.market_cache import market_cache
            cached_quote = market_cache.get_stock_realtime(stock_code)
            if cached_quote:
                return cached_quote
        except Exception as e:
            logger.debug(f"市场缓存获取失败: {stock_code}, {e}")
        
        # 2. 检查本地缓存
        cache_key = f"quote_{stock_code}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 3. 主数据源
            quote = await self.primary_source.get_realtime_quote(stock_code)
            if quote:
                self._set_cache(cache_key, quote)
                return quote
            
            # 4. 备用数据源
            logger.info(f"主数据源失败，使用备用数据源: {stock_code}")
            quote = await self.backup_source.get_realtime_quote(stock_code)
            if quote:
                self._set_cache(cache_key, quote)
                return quote
            
            logger.warning(f"所有数据源都无法获取行情: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"获取实时行情异常: {stock_code}, 错误: {str(e)}")
            return None
    
    async def get_realtime_quote_for_monitor(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取监测个股的实时行情 - 优化版本
        
        数据获取优先级（按速度排序）：
        1. 本地缓存（10秒TTL）
        2. 东方财富 API（异步 HTTP，最快）
        3. 新浪 API（东方财富内置备用）
        4. AkShare 个股接口（同步阻塞，较慢，最后备用）
        
        Args:
            stock_code: 股票代码
            
        Returns:
            实时行情数据
        """
        # 检查本地缓存
        cache_key = f"monitor_quote_{stock_code}"
        if cache_key in self.cache:
            cache_time, data = self.cache[cache_key]
            if (datetime.now() - cache_time).total_seconds() < self.monitor_cache_ttl:
                return data
        
        try:
            # 优先使用东方财富 API（异步 HTTP，速度快）
            quote = await self.primary_source.get_realtime_quote(stock_code)
            if quote and quote.get("price", 0) > 0:
                self._set_cache(cache_key, quote)
                return quote
            
            # 东方财富失败，尝试 AkShare 个股接口
            logger.info(f"东方财富API失败，尝试AkShare个股接口: {stock_code}")
            quote = await self.backup_source.get_realtime_quote_individual(stock_code)
            if quote and quote.get("price", 0) > 0:
                self._set_cache(cache_key, quote)
                return quote
            
            # 最后尝试 AkShare 全市场接口
            logger.info(f"AkShare个股接口失败，尝试全市场接口: {stock_code}")
            quote = await self.backup_source.get_realtime_quote(stock_code)
            if quote:
                self._set_cache(cache_key, quote)
                return quote
            
            logger.warning(f"所有数据源都无法获取监测行情: {stock_code}")
            return None
            
        except Exception as e:
            logger.error(f"获取监测行情异常: {stock_code}, 错误: {str(e)}")
            return None
    
    async def get_kline_data(
        self,
        stock_code: str,
        period: str = "daily",
        start_date: Optional[str] = None,
        end_date: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据 - 多数据源容错
        
        Args:
            stock_code: 股票代码
            period: 周期
            start_date: 开始日期
            end_date: 结束日期
            limit: 数据条数
            
        Returns:
            K线数据列表
        """
        cache_key = f"kline_{stock_code}_{period}_{start_date}_{end_date}_{limit}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 主数据源
            klines = await self.primary_source.get_kline_data(
                stock_code, period, start_date, end_date, limit
            )
            if klines:
                self._set_cache(cache_key, klines)
                return klines
            
            # 备用数据源 - 需要转换参数格式
            logger.info(f"主数据源失败，使用备用数据源获取K线: {stock_code}")
            
            # 转换周期格式
            period_map = {
                "1min": "1", "5min": "5", "15min": "15",
                "30min": "30", "60min": "60",
                "daily": "daily", "weekly": "weekly", "monthly": "monthly"
            }
            ak_period = period_map.get(period, "daily")
            
            # 转换日期格式
            ak_start = start_date.replace("-", "") if start_date else None
            ak_end = end_date.replace("-", "") if end_date else None
            
            klines = await self.backup_source.get_kline_data(
                stock_code, ak_period, ak_start, ak_end, limit=limit
            )
            if klines:
                self._set_cache(cache_key, klines)
                return klines
            
            logger.warning(f"所有数据源都无法获取K线数据: {stock_code}")
            return []
            
        except Exception as e:
            logger.error(f"获取K线数据异常: {stock_code}, 错误: {str(e)}")
            return []
    
    async def get_batch_quotes(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取实时行情
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            股票代码到行情数据的映射
        """
        try:
            # 检查缓存
            results = {}
            uncached_codes = []
            
            for code in stock_codes:
                cache_key = f"quote_{code}"
                cached_data = self._get_cache(cache_key)
                if cached_data:
                    results[code] = cached_data
                else:
                    uncached_codes.append(code)
            
            if not uncached_codes:
                return results
            
            # 主数据源批量获取
            quotes = await self.primary_source.get_batch_quotes(uncached_codes)
            
            # 缓存成功获取的数据
            for code, quote in quotes.items():
                cache_key = f"quote_{code}"
                self._set_cache(cache_key, quote)
                results[code] = quote
            
            # 对于失败的股票，尝试备用数据源单独获取
            failed_codes = [code for code in uncached_codes if code not in quotes]
            if failed_codes:
                logger.info(f"部分股票主数据源失败，使用备用数据源: {failed_codes}")
                
                # 限制并发数，避免过多请求
                semaphore = asyncio.Semaphore(5)
                
                async def fetch_one(code: str):
                    async with semaphore:
                        try:
                            quote = await self.backup_source.get_realtime_quote(code)
                            if quote:
                                cache_key = f"quote_{code}"
                                self._set_cache(cache_key, quote)
                                results[code] = quote
                        except Exception as e:
                            logger.warning(f"备用数据源获取失败: {code}, 错误: {str(e)}")
                
                await asyncio.gather(*[fetch_one(code) for code in failed_codes])
            
            return results
            
        except Exception as e:
            logger.error(f"批量获取行情异常: {str(e)}")
            return {}
    
    async def search_stock(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        搜索股票 - 多数据源支持
        
        Args:
            keyword: 搜索关键词
            limit: 返回结果数量限制
            
        Returns:
            匹配的股票列表
        """
        try:
            # 主数据源搜索
            results = await self.primary_source.search_stock(keyword, limit)
            if results:
                return results
            
            # 备用数据源搜索
            logger.info(f"主数据源搜索失败，使用备用数据源: {keyword}")
            results = await self.backup_source.search_stock(keyword, limit)
            return results or []
            
        except Exception as e:
            logger.error(f"搜索股票异常: {keyword}, 错误: {str(e)}")
            return []
    
    async def get_fund_flow(self, stock_code: str, days: int = 10) -> List[Dict[str, Any]]:
        """
        获取资金流向数据
        
        Args:
            stock_code: 股票代码
            days: 获取天数
            
        Returns:
            资金流向数据列表
        """
        cache_key = f"fund_flow_{stock_code}_{days}"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 主数据源
            flow_data = await self.primary_source.get_fund_flow(stock_code, days)
            if flow_data:
                self._set_cache(cache_key, flow_data)
                return flow_data
            
            # 备用数据源 - AkShare有不同的资金流向接口
            logger.info(f"主数据源失败，使用备用数据源获取资金流向: {stock_code}")
            # 注意：这里需要根据AkShare的实际接口调整
            # flow_data = await self.backup_source.get_fund_flow(stock_code)
            # if flow_data:
            #     self._set_cache(cache_key, flow_data)
            #     return flow_data
            
            logger.warning(f"无法获取资金流向数据: {stock_code}")
            return []
            
        except Exception as e:
            logger.error(f"获取资金流向异常: {stock_code}, 错误: {str(e)}")
            return []
    
    async def get_market_overview(self) -> Dict[str, Any]:
        """
        获取市场概览数据
        
        Returns:
            市场概览数据
        """
        cache_key = "market_overview"
        cached_data = self._get_cache(cache_key)
        if cached_data:
            return cached_data
        
        try:
            # 获取主要指数行情
            indices = ["000001", "399001", "399006"]  # 上证指数、深证成指、创业板指
            index_quotes = await self.get_batch_quotes(indices)
            
            overview = {
                "update_time": datetime.now().isoformat(),
                "indices": index_quotes,
                "market_status": "trading" if self._is_trading_time() else "closed"
            }
            
            self._set_cache(cache_key, overview)
            return overview
            
        except Exception as e:
            logger.error(f"获取市场概览异常: {str(e)}")
            return {}
    
    def _is_trading_time(self) -> bool:
        """判断是否在交易时间内"""
        now = datetime.now()
        weekday = now.weekday()
        
        # 周末不交易
        if weekday >= 5:
            return False
        
        # 交易时间：9:30-11:30, 13:00-15:00
        time_now = now.time()
        morning_start = datetime.strptime("09:30", "%H:%M").time()
        morning_end = datetime.strptime("11:30", "%H:%M").time()
        afternoon_start = datetime.strptime("13:00", "%H:%M").time()
        afternoon_end = datetime.strptime("15:00", "%H:%M").time()
        
        return (morning_start <= time_now <= morning_end) or \
               (afternoon_start <= time_now <= afternoon_end)
    
    async def close(self):
        """关闭数据获取服务"""
        try:
            await self.primary_source.close()
        except Exception as e:
            logger.error(f"关闭主数据源失败: {str(e)}")


# 创建全局数据获取服务实例
data_fetcher = DataFetcher()