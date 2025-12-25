"""
股票数据API服务
提供实时行情、历史数据、资金流向等数据获取功能
"""
import aiohttp
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import json
import re
from app.core.logging import get_logger

logger = get_logger(__name__)


class StockAPIService:
    """股票数据API服务类"""
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        # 东方财富API基础URL
        self.eastmoney_quote_url = "https://push2.eastmoney.com/api/qt/stock/get"
        self.eastmoney_kline_url = "https://push2his.eastmoney.com/api/qt/stock/kline/get"
        self.eastmoney_fund_flow_url = "https://push2.eastmoney.com/api/qt/stock/fflow/kline/get"
        # 新浪财经API（备用）
        self.sina_realtime_url = "https://hq.sinajs.cn/list="
        
    async def _get_session(self) -> aiohttp.ClientSession:
        """获取或创建HTTP会话"""
        if self.session is None or self.session.closed:
            timeout = aiohttp.ClientTimeout(total=30)
            self.session = aiohttp.ClientSession(timeout=timeout)
        return self.session
    
    async def close(self):
        """关闭HTTP会话"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    def _get_market_code(self, stock_code: str) -> str:
        """
        根据股票代码获取市场代码
        上海: 1, 深圳: 0
        """
        if stock_code.startswith(('6', '9', '5')):
            return '1'  # 上海
        else:
            return '0'  # 深圳
    
    def _get_secid(self, stock_code: str) -> str:
        """获取东方财富格式的证券ID"""
        market = self._get_market_code(stock_code)
        return f"{market}.{stock_code}"
    
    async def get_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取股票实时行情
        
        Args:
            stock_code: 股票代码，如 "000001"
            
        Returns:
            包含实时行情数据的字典
        """
        try:
            session = await self._get_session()
            secid = self._get_secid(stock_code)
            
            params = {
                "secid": secid,
                "fields": "f43,f44,f45,f46,f47,f48,f50,f51,f52,f55,f57,f58,f60,f116,f117,f168,f169,f170",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            
            async with session.get(self.eastmoney_quote_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data"):
                        raw = data["data"]
                        return {
                            "code": stock_code,
                            "name": raw.get("f58", ""),
                            "price": raw.get("f43", 0) / 100,  # 当前价
                            "change": raw.get("f169", 0) / 100,  # 涨跌额
                            "change_percent": raw.get("f170", 0) / 100,  # 涨跌幅
                            "open": raw.get("f46", 0) / 100,  # 开盘价
                            "high": raw.get("f44", 0) / 100,  # 最高价
                            "low": raw.get("f45", 0) / 100,  # 最低价
                            "pre_close": raw.get("f60", 0) / 100,  # 昨收
                            "volume": raw.get("f47", 0),  # 成交量（手）
                            "amount": raw.get("f48", 0),  # 成交额
                            "turnover_rate": raw.get("f168", 0) / 100,  # 换手率
                            "pe_ratio": raw.get("f55", 0) / 100,  # 市盈率
                            "market_cap": raw.get("f116", 0),  # 总市值
                            "float_market_cap": raw.get("f117", 0),  # 流通市值
                            "timestamp": datetime.now().isoformat()
                        }
            
            # 如果东方财富API失败，尝试新浪API
            return await self._get_sina_realtime(stock_code)
            
        except Exception as e:
            logger.error(f"获取实时行情失败: {stock_code}, 错误: {str(e)}")
            return None
    
    async def _get_sina_realtime(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """从新浪财经获取实时行情（备用）"""
        try:
            session = await self._get_session()
            market = "sh" if stock_code.startswith(('6', '9', '5')) else "sz"
            url = f"{self.sina_realtime_url}{market}{stock_code}"
            
            headers = {"Referer": "https://finance.sina.com.cn"}
            
            async with session.get(url, headers=headers) as response:
                if response.status == 200:
                    text = await response.text(encoding='gbk')
                    # 解析新浪数据格式
                    match = re.search(r'"(.+)"', text)
                    if match:
                        parts = match.group(1).split(',')
                        if len(parts) >= 32:
                            return {
                                "code": stock_code,
                                "name": parts[0],
                                "price": float(parts[3]) if parts[3] else 0,
                                "change": float(parts[3]) - float(parts[2]) if parts[3] and parts[2] else 0,
                                "change_percent": ((float(parts[3]) - float(parts[2])) / float(parts[2]) * 100) if parts[3] and parts[2] and float(parts[2]) != 0 else 0,
                                "open": float(parts[1]) if parts[1] else 0,
                                "high": float(parts[4]) if parts[4] else 0,
                                "low": float(parts[5]) if parts[5] else 0,
                                "pre_close": float(parts[2]) if parts[2] else 0,
                                "volume": int(float(parts[8])) if parts[8] else 0,
                                "amount": float(parts[9]) if parts[9] else 0,
                                "timestamp": datetime.now().isoformat()
                            }
        except Exception as e:
            logger.error(f"新浪API获取失败: {stock_code}, 错误: {str(e)}")
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
        获取K线数据
        
        Args:
            stock_code: 股票代码
            period: 周期 - daily(日线), weekly(周线), monthly(月线), 
                    1min, 5min, 15min, 30min, 60min
            start_date: 开始日期 YYYY-MM-DD
            end_date: 结束日期 YYYY-MM-DD
            limit: 返回数据条数
            
        Returns:
            K线数据列表
        """
        try:
            session = await self._get_session()
            secid = self._get_secid(stock_code)
            
            # 周期映射
            klt_map = {
                "1min": "1", "5min": "5", "15min": "15", 
                "30min": "30", "60min": "60",
                "daily": "101", "weekly": "102", "monthly": "103"
            }
            klt = klt_map.get(period, "101")
            
            params = {
                "secid": secid,
                "klt": klt,
                "fqt": "1",  # 前复权
                "lmt": limit,
                "end": "20500101",
                "fields1": "f1,f2,f3,f4,f5,f6",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            
            async with session.get(self.eastmoney_kline_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and data["data"].get("klines"):
                        klines = []
                        for line in data["data"]["klines"]:
                            parts = line.split(',')
                            if len(parts) >= 11:
                                kline = {
                                    "date": parts[0],
                                    "open": float(parts[1]),
                                    "close": float(parts[2]),
                                    "high": float(parts[3]),
                                    "low": float(parts[4]),
                                    "volume": int(parts[5]),
                                    "amount": float(parts[6]),
                                    "amplitude": float(parts[7]),  # 振幅
                                    "change_percent": float(parts[8]),  # 涨跌幅
                                    "change": float(parts[9]),  # 涨跌额
                                    "turnover_rate": float(parts[10])  # 换手率
                                }
                                
                                # 日期过滤
                                if start_date and kline["date"] < start_date:
                                    continue
                                if end_date and kline["date"] > end_date:
                                    continue
                                    
                                klines.append(kline)
                        
                        return klines
            
            return []
            
        except Exception as e:
            logger.error(f"获取K线数据失败: {stock_code}, 错误: {str(e)}")
            return []
    
    async def get_fund_flow(self, stock_code: str, days: int = 10) -> List[Dict[str, Any]]:
        """
        获取个股资金流向数据
        
        Args:
            stock_code: 股票代码
            days: 获取天数
            
        Returns:
            资金流向数据列表
        """
        try:
            session = await self._get_session()
            secid = self._get_secid(stock_code)
            
            params = {
                "secid": secid,
                "klt": "101",
                "lmt": days,
                "fields1": "f1,f2,f3,f7",
                "fields2": "f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61,f62,f63,f64,f65",
                "ut": "fa5fd1943c7b386f172d6893dbfba10b"
            }
            
            async with session.get(self.eastmoney_fund_flow_url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("data") and data["data"].get("klines"):
                        flows = []
                        for line in data["data"]["klines"]:
                            parts = line.split(',')
                            if len(parts) >= 13:
                                flows.append({
                                    "date": parts[0],
                                    "main_net_inflow": float(parts[1]),  # 主力净流入
                                    "small_net_inflow": float(parts[5]),  # 小单净流入
                                    "medium_net_inflow": float(parts[3]),  # 中单净流入
                                    "large_net_inflow": float(parts[7]),  # 大单净流入
                                    "super_large_net_inflow": float(parts[9]),  # 超大单净流入
                                    "main_net_inflow_percent": float(parts[2]),  # 主力净流入占比
                                    "close": float(parts[11]),  # 收盘价
                                    "change_percent": float(parts[12])  # 涨跌幅
                                })
                        return flows
            
            return []
            
        except Exception as e:
            logger.error(f"获取资金流向失败: {stock_code}, 错误: {str(e)}")
            return []
    
    async def get_batch_quotes(self, stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
        """
        批量获取股票实时行情
        
        Args:
            stock_codes: 股票代码列表
            
        Returns:
            股票代码到行情数据的映射
        """
        results = {}
        
        # 并发获取，但限制并发数
        semaphore = asyncio.Semaphore(10)
        
        async def fetch_one(code: str):
            async with semaphore:
                quote = await self.get_realtime_quote(code)
                if quote:
                    results[code] = quote
        
        await asyncio.gather(*[fetch_one(code) for code in stock_codes])
        
        return results
    
    async def search_stock(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        搜索股票
        
        Args:
            keyword: 搜索关键词（代码或名称）
            limit: 返回结果数量限制
            
        Returns:
            匹配的股票列表
        """
        try:
            session = await self._get_session()
            url = "https://searchapi.eastmoney.com/api/suggest/get"
            
            params = {
                "input": keyword,
                "type": "14",
                "token": "D43BF722C8E33BDC906FB84D85E326E8",
                "count": limit
            }
            
            async with session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    if data.get("QuotationCodeTable") and data["QuotationCodeTable"].get("Data"):
                        results = []
                        for item in data["QuotationCodeTable"]["Data"]:
                            # 只返回A股
                            if item.get("SecurityTypeName") in ["沪A", "深A"]:
                                results.append({
                                    "code": item.get("Code", ""),
                                    "name": item.get("Name", ""),
                                    "market": "SH" if item.get("SecurityTypeName") == "沪A" else "SZ"
                                })
                        return results
            
            return []
            
        except Exception as e:
            logger.error(f"搜索股票失败: {keyword}, 错误: {str(e)}")
            return []


# 创建全局服务实例
stock_api_service = StockAPIService()