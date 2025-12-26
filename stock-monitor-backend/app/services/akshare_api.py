"""
AkShare 数据服务
提供基于 AkShare 库的股票数据获取功能
作为东方财富和新浪API的补充数据源
"""
import asyncio
from typing import Dict, List, Optional, Any
from datetime import datetime
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from app.core.logging import get_logger

logger = get_logger(__name__)

# 线程池用于运行同步的 akshare 调用
_executor = ThreadPoolExecutor(max_workers=4)


def _run_sync(func, *args, **kwargs):
    """在线程池中运行同步函数"""
    return func(*args, **kwargs)


def _safe_float(value, default: float = 0.0) -> float:
    """安全转换为浮点数，处理 '-'、None、空字符串等异常值"""
    if value is None or value == '' or value == '-':
        return default
    try:
        return float(value)
    except (ValueError, TypeError):
        return default


def _safe_int(value, default: int = 0) -> int:
    """安全转换为整数，处理 '-'、None、空字符串等异常值"""
    if value is None or value == '' or value == '-':
        return default
    try:
        return int(float(value))
    except (ValueError, TypeError):
        return default


class AkShareService:
    """AkShare 数据服务类"""
    
    def __init__(self):
        self._ak = None
        self._cache = {}
        self._cache_time = {}
        # 分级缓存TTL配置（秒）
        # 由于监测个股有专门的高效 API，其他数据缓存时间可以调长
        self._cache_ttl_config = {
            "realtime": 10,       # 实时行情缓存10秒（监测个股用专门接口）
            "bid_ask": 5,         # 五档盘口缓存5秒
            "kline_min": 30,      # 分钟K线缓存30秒
            "kline_daily": 600,   # 日K线缓存10分钟
            "hot_rank": 300,      # 热门排名缓存5分钟
            "fund_flow": 300,     # 资金流向缓存5分钟
            "stock_list": 7200,   # 股票列表缓存2小时
            "board": 600,         # 板块数据缓存10分钟
            "news": 600,          # 新闻缓存10分钟
            "financial": 7200,    # 财务数据缓存2小时
            "default": 120        # 默认缓存2分钟
        }
        self._cache_ttl = 120  # 默认缓存2分钟（兼容旧代码）
    
    @property
    def ak(self):
        """延迟导入 akshare"""
        if self._ak is None:
            try:
                import akshare as ak
                self._ak = ak
            except ImportError:
                logger.error("akshare 未安装，请运行: pip install akshare")
                raise
        return self._ak
    
    async def _run_in_executor(self, func, *args, **kwargs):
        """在线程池中异步运行同步函数"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(_executor, partial(func, *args, **kwargs))

    def _get_market(self, stock_code: str) -> str:
        """根据股票代码判断市场"""
        code = stock_code.strip()
        if code.startswith(("6", "9")):
            return "sh"
        elif code.startswith(("0", "2", "3")):
            return "sz"
        else:
            return "sh"

    def _is_cache_valid(self, key: str, cache_type: str = "default") -> bool:
        """
        检查缓存是否有效
        
        Args:
            key: 缓存键
            cache_type: 缓存类型，用于获取对应的TTL
        """
        if key not in self._cache_time:
            return False
        elapsed = (datetime.now() - self._cache_time[key]).total_seconds()
        ttl = self._cache_ttl_config.get(cache_type, self._cache_ttl_config["default"])
        return elapsed < ttl
    
    def _set_cache(self, key: str, value: Any) -> None:
        """设置缓存"""
        self._cache[key] = value
        self._cache_time[key] = datetime.now()
    
    def _get_cache(self, key: str, cache_type: str = "default") -> Optional[Any]:
        """获取缓存，如果有效则返回，否则返回None"""
        if self._is_cache_valid(key, cache_type):
            return self._cache.get(key)
        return None
    
    def _clear_expired_cache(self) -> None:
        """清理过期缓存（定期调用以释放内存）"""
        now = datetime.now()
        expired_keys = []
        for key, cache_time in self._cache_time.items():
            # 超过最大TTL（1小时）的缓存都清理
            if (now - cache_time).total_seconds() > 3600:
                expired_keys.append(key)
        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_time.pop(key, None)

    # ==================== 实时行情 ====================

    async def get_realtime_quote(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取个股实时行情

        Args:
            stock_code: 股票代码 (如 "000001")

        Returns:
            行情数据字典
        """
        # 检查缓存
        cache_key = f"realtime_{stock_code}"
        cached = self._get_cache(cache_key, "realtime")
        if cached:
            return cached
        
        try:
            def _get_quote():
                df = self.ak.stock_zh_a_spot_em()
                row = df[df["代码"] == stock_code]
                if row.empty:
                    return None

                r = row.iloc[0]
                return {
                    "code": r.get("代码", ""),
                    "name": r.get("名称", ""),
                    "price": float(r.get("最新价", 0) or 0),
                    "change": float(r.get("涨跌额", 0) or 0),
                    "change_percent": float(r.get("涨跌幅", 0) or 0),
                    "open": float(r.get("今开", 0) or 0),
                    "high": float(r.get("最高", 0) or 0),
                    "low": float(r.get("最低", 0) or 0),
                    "pre_close": float(r.get("昨收", 0) or 0),
                    "volume": int(r.get("成交量", 0) or 0),
                    "amount": float(r.get("成交额", 0) or 0),
                    "turnover_rate": float(r.get("换手率", 0) or 0),
                    "pe_ratio": float(r.get("市盈率-动态", 0) or 0),
                    "pb_ratio": float(r.get("市净率", 0) or 0),
                    "market_cap": float(r.get("总市值", 0) or 0),
                    "float_market_cap": float(r.get("流通市值", 0) or 0),
                    "timestamp": datetime.now().isoformat(),
                }
            
            result = await self._run_in_executor(_get_quote)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取实时行情失败: {stock_code}, 错误: {str(e)}")
            return None

    async def get_realtime_quote_individual(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取个股实时行情（使用东方财富个股接口，高效）
        
        使用 stock_bid_ask_em 接口，针对单只股票查询，效率高，
        避免获取全市场数据后筛选。包含五档盘口、实时价格、涨跌幅等。

        Args:
            stock_code: 股票代码 (如 "000672")

        Returns:
            行情数据字典
        """
        # 检查缓存（实时行情缓存时间短）
        cache_key = f"realtime_individual_{stock_code}"
        cached = self._get_cache(cache_key, "realtime")
        if cached:
            return cached
        
        try:
            def _get_quote():
                try:
                    # 使用东方财富个股行情接口
                    df = self.ak.stock_bid_ask_em(symbol=stock_code)
                    if df is None or df.empty:
                        return None
                    
                    # 将 DataFrame 转换为字典
                    data = dict(zip(df["item"], df["value"]))
                    
                    # 使用安全转换函数处理可能的 '-' 值
                    price = _safe_float(data.get("最新"))
                    pre_close = _safe_float(data.get("昨收"))
                    change = round(price - pre_close, 2) if pre_close > 0 else 0
                    
                    return {
                        "code": stock_code,
                        "name": "",  # 名称由调用方提供，避免额外 API 调用
                        "price": price,
                        "change": change,
                        "change_percent": _safe_float(data.get("涨幅")),
                        "open": _safe_float(data.get("今开")),
                        "high": _safe_float(data.get("最高")),
                        "low": _safe_float(data.get("最低")),
                        "pre_close": pre_close,
                        "volume": _safe_int(_safe_float(data.get("总手")) * 100),  # 总手转换为股数
                        "amount": _safe_float(data.get("金额")),
                        "turnover_rate": _safe_float(data.get("换手")),
                        "volume_ratio": _safe_float(data.get("量比")),
                        "avg_price": _safe_float(data.get("均价")),
                        "limit_up": _safe_float(data.get("涨停")),
                        "limit_down": _safe_float(data.get("跌停")),
                        "outer_vol": _safe_int(data.get("外盘")),
                        "inner_vol": _safe_int(data.get("内盘")),
                        # 五档盘口
                        "bid_ask": {
                            "sell_5": {"price": _safe_float(data.get("sell_5")), "vol": _safe_int(data.get("sell_5_vol"))},
                            "sell_4": {"price": _safe_float(data.get("sell_4")), "vol": _safe_int(data.get("sell_4_vol"))},
                            "sell_3": {"price": _safe_float(data.get("sell_3")), "vol": _safe_int(data.get("sell_3_vol"))},
                            "sell_2": {"price": _safe_float(data.get("sell_2")), "vol": _safe_int(data.get("sell_2_vol"))},
                            "sell_1": {"price": _safe_float(data.get("sell_1")), "vol": _safe_int(data.get("sell_1_vol"))},
                            "buy_1": {"price": _safe_float(data.get("buy_1")), "vol": _safe_int(data.get("buy_1_vol"))},
                            "buy_2": {"price": _safe_float(data.get("buy_2")), "vol": _safe_int(data.get("buy_2_vol"))},
                            "buy_3": {"price": _safe_float(data.get("buy_3")), "vol": _safe_int(data.get("buy_3_vol"))},
                            "buy_4": {"price": _safe_float(data.get("buy_4")), "vol": _safe_int(data.get("buy_4_vol"))},
                            "buy_5": {"price": _safe_float(data.get("buy_5")), "vol": _safe_int(data.get("buy_5_vol"))},
                        },
                        "timestamp": datetime.now().isoformat(),
                    }
                except Exception as inner_e:
                    logger.warning(f"stock_bid_ask_em 接口失败: {stock_code}, 错误: {str(inner_e)}")
                    return None
            
            result = await self._run_in_executor(_get_quote)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取个股实时行情失败: {stock_code}, 错误: {str(e)}")
            return None

    # ==================== K线数据 ====================

    async def get_kline_data(
        self,
        stock_code: str,
        period: str = "daily",
        start_date: str = None,
        end_date: str = None,
        adjust: str = "qfq",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            stock_code: 股票代码
            period: 周期 (daily/weekly/monthly)
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)
            adjust: 复权类型 (qfq前复权/hfq后复权/空不复权)
            limit: 返回数据条数

        Returns:
            K线数据列表
        """
        # 检查缓存
        cache_key = f"kline_{stock_code}_{period}_{start_date}_{end_date}_{limit}"
        cache_type = "kline_daily" if period in ["daily", "weekly", "monthly"] else "kline_min"
        cached = self._get_cache(cache_key, cache_type)
        if cached:
            return cached
        
        try:
            def _get_kline():
                df = self.ak.stock_zh_a_hist(
                    symbol=stock_code,
                    period=period,
                    start_date=start_date,
                    end_date=end_date,
                    adjust=adjust,
                )
                if df.empty:
                    return []

                klines = []
                for _, row in df.tail(limit).iterrows():
                    klines.append({
                        "date": str(row.get("日期", "")),
                        "open": float(row.get("开盘", 0)),
                        "close": float(row.get("收盘", 0)),
                        "high": float(row.get("最高", 0)),
                        "low": float(row.get("最低", 0)),
                        "volume": int(row.get("成交量", 0)),
                        "amount": float(row.get("成交额", 0)),
                        "amplitude": float(row.get("振幅", 0) or 0),
                        "change_percent": float(row.get("涨跌幅", 0) or 0),
                        "change": float(row.get("涨跌额", 0) or 0),
                        "turnover_rate": float(row.get("换手率", 0) or 0),
                    })
                return klines
            
            result = await self._run_in_executor(_get_kline)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取K线数据失败: {stock_code}, 错误: {str(e)}")
            return []

    # ==================== 分钟K线数据 ====================

    async def get_minute_kline(
        self,
        stock_code: str,
        period: str = "5",
        adjust: str = "qfq",
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        获取分钟级K线数据

        Args:
            stock_code: 股票代码
            period: 周期 (1/5/15/30/60 分钟)
            adjust: 复权类型 (qfq前复权/hfq后复权/空不复权)
            limit: 返回数据条数

        Returns:
            分钟K线数据列表
        """
        # 检查缓存
        cache_key = f"kline_min_{stock_code}_{period}_{limit}"
        cached = self._get_cache(cache_key, "kline_min")
        if cached:
            return cached
        
        try:
            def _get_minute_kline():
                df = self.ak.stock_zh_a_hist_min_em(
                    symbol=stock_code,
                    period=period,
                    adjust=adjust,
                )
                if df.empty:
                    return []

                klines = []
                for _, row in df.tail(limit).iterrows():
                    klines.append({
                        "time": str(row.get("时间", "")),
                        "open": float(row.get("开盘", 0)),
                        "close": float(row.get("收盘", 0)),
                        "high": float(row.get("最高", 0)),
                        "low": float(row.get("最低", 0)),
                        "volume": int(row.get("成交量", 0)),
                        "amount": float(row.get("成交额", 0)),
                        "latest_price": float(row.get("最新价", 0) or 0),
                    })
                return klines
            
            result = await self._run_in_executor(_get_minute_kline)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取分钟K线失败: {stock_code}, 错误: {str(e)}")
            return []

    # ==================== 五档盘口 ====================

    async def get_bid_ask(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取五档盘口数据

        Args:
            stock_code: 股票代码

        Returns:
            五档盘口数据
        """
        # 检查缓存
        cache_key = f"bid_ask_{stock_code}"
        cached = self._get_cache(cache_key, "bid_ask")
        if cached:
            return cached
        
        try:
            def _get_bid_ask():
                # 使用东方财富实时行情接口获取盘口数据
                df = self.ak.stock_bid_ask_em(symbol=stock_code)
                if df.empty:
                    return None
                
                # 解析五档数据
                result = {
                    "code": stock_code,
                    "timestamp": datetime.now().isoformat(),
                    "bids": [],  # 买盘
                    "asks": [],  # 卖盘
                }
                
                # 解析买卖盘数据
                for _, row in df.iterrows():
                    item_name = str(row.get("item", ""))
                    item_value = row.get("value", 0)
                    
                    # 买盘价格和数量
                    if "买" in item_name and "价" in item_name:
                        level = int(''.join(filter(str.isdigit, item_name)) or 0)
                        if level > 0 and level <= 5:
                            while len(result["bids"]) < level:
                                result["bids"].append({"price": 0, "volume": 0})
                            result["bids"][level-1]["price"] = float(item_value or 0)
                    elif "买" in item_name and "量" in item_name:
                        level = int(''.join(filter(str.isdigit, item_name)) or 0)
                        if level > 0 and level <= 5:
                            while len(result["bids"]) < level:
                                result["bids"].append({"price": 0, "volume": 0})
                            result["bids"][level-1]["volume"] = int(item_value or 0)
                    # 卖盘价格和数量
                    elif "卖" in item_name and "价" in item_name:
                        level = int(''.join(filter(str.isdigit, item_name)) or 0)
                        if level > 0 and level <= 5:
                            while len(result["asks"]) < level:
                                result["asks"].append({"price": 0, "volume": 0})
                            result["asks"][level-1]["price"] = float(item_value or 0)
                    elif "卖" in item_name and "量" in item_name:
                        level = int(''.join(filter(str.isdigit, item_name)) or 0)
                        if level > 0 and level <= 5:
                            while len(result["asks"]) < level:
                                result["asks"].append({"price": 0, "volume": 0})
                            result["asks"][level-1]["volume"] = int(item_value or 0)
                
                return result
            
            result = await self._run_in_executor(_get_bid_ask)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取五档盘口失败: {stock_code}, 错误: {str(e)}")
            return None

    # ==================== 热门股票排名 ====================

    async def get_hot_rank(self, limit: int = 50) -> Optional[List[Dict[str, Any]]]:
        """
        获取热门股票排名

        Args:
            limit: 返回数量限制

        Returns:
            热门股票列表
        """
        # 检查缓存
        cache_key = f"hot_rank_{limit}"
        cached = self._get_cache(cache_key, "hot_rank")
        if cached:
            return cached
        
        try:
            def _get_hot_rank():
                df = self.ak.stock_hot_rank_em()
                if df.empty:
                    return None
                
                result = []
                for _, row in df.head(limit).iterrows():
                    result.append({
                        "rank": int(row.get("当前排名", 0) or 0),
                        "code": str(row.get("代码", "")),
                        "name": str(row.get("股票名称", "")),
                        "price": float(row.get("最新价", 0) or 0),
                        "change_percent": float(row.get("涨跌幅", 0) or 0),
                        "rank_change": int(row.get("排名较昨日变化", 0) or 0),
                    })
                return result
            
            result = await self._run_in_executor(_get_hot_rank)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取热门股票排名失败: {str(e)}")
            return None

    # ==================== 热门关键词 ====================

    async def get_hot_keywords(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取热门关键词/概念

        Returns:
            热门关键词列表
        """
        # 检查缓存
        cache_key = "hot_keywords"
        cached = self._get_cache(cache_key, "hot_rank")
        if cached:
            return cached
        
        try:
            def _get_hot_keywords():
                df = self.ak.stock_hot_keyword_em()
                if df.empty:
                    return None
                
                result = []
                for _, row in df.head(20).iterrows():
                    result.append({
                        "keyword": str(row.get("关键词", "")),
                        "heat": int(row.get("热度", 0) or 0),
                        "related_stocks": str(row.get("相关股票", "")),
                    })
                return result
            
            result = await self._run_in_executor(_get_hot_keywords)
            if result:
                self._set_cache(cache_key, result)
            return result
        except Exception as e:
            logger.error(f"AkShare 获取热门关键词失败: {str(e)}")
            return None


    # ==================== 资金流向 ====================

    def get_fund_flow(self, stock_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取个股资金流向

        Args:
            stock_code: 股票代码

        Returns:
            资金流向数据列表
        """
        try:
            market = self._get_market(stock_code)
            df = self.ak.stock_individual_fund_flow(stock=stock_code, market=market)
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "date": str(row.get("日期", "")),
                    "close_price": float(row.get("收盘价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "main_net_inflow": float(row.get("主力净流入-净额", 0) or 0),
                    "main_net_inflow_pct": float(row.get("主力净流入-净占比", 0) or 0),
                    "super_large_net_inflow": float(row.get("超大单净流入-净额", 0) or 0),
                    "large_net_inflow": float(row.get("大单净流入-净额", 0) or 0),
                    "medium_net_inflow": float(row.get("中单净流入-净额", 0) or 0),
                    "small_net_inflow": float(row.get("小单净流入-净额", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取资金流向失败: {e}")
            return None

    def get_fund_flow_rank(self, indicator: str = "今日") -> Optional[List[Dict[str, Any]]]:
        """
        获取资金流向排名

        Args:
            indicator: 时间范围 (今日/3日/5日/10日)

        Returns:
            资金流向排名列表
        """
        try:
            df = self.ak.stock_individual_fund_flow_rank(indicator=indicator)
            if df.empty:
                return None

            result = []
            for _, row in df.head(50).iterrows():  # 只取前50
                result.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "main_net_inflow": float(row.get("主力净流入-净额", 0) or 0),
                    "main_net_inflow_pct": float(row.get("主力净流入-净占比", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取资金流向排名失败: {e}")
            return None

    # ==================== 涨跌停数据 ====================

    def get_zt_pool(self, date: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        获取涨停股票池

        Args:
            date: 日期 (YYYYMMDD)，默认今天

        Returns:
            涨停股票列表
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            df = self.ak.stock_zt_pool_em(date=date)
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "zt_price": float(row.get("涨停价", 0) or 0),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "turnover_rate": float(row.get("换手率", 0) or 0),
                    "amount": float(row.get("成交额", 0) or 0),
                    "float_market_cap": float(row.get("流通市值", 0) or 0),
                    "zt_reason": str(row.get("涨停原因", "")),
                    "continuous_zt": int(row.get("连板数", 0) or 0),
                    "first_zt_time": str(row.get("首次涨停时间", "")),
                    "last_zt_time": str(row.get("最后涨停时间", "")),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取涨停股票池失败: {e}")
            return None

    def get_dt_pool(self, date: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        获取跌停股票池

        Args:
            date: 日期 (YYYYMMDD)

        Returns:
            跌停股票列表
        """
        try:
            if date is None:
                date = datetime.now().strftime("%Y%m%d")
            df = self.ak.stock_zt_pool_dtgc_em(date=date)
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "dt_price": float(row.get("跌停价", 0) or 0),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "turnover_rate": float(row.get("换手率", 0) or 0),
                    "amount": float(row.get("成交额", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取跌停股票池失败: {e}")
            return None


    # ==================== 板块数据 ====================

    def get_industry_boards(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取行业板块列表

        Returns:
            行业板块列表
        """
        try:
            df = self.ak.stock_board_industry_name_em()
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "name": str(row.get("板块名称", "")),
                    "code": str(row.get("板块代码", "")),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "change_amount": float(row.get("涨跌额", 0) or 0),
                    "total_market_cap": float(row.get("总市值", 0) or 0),
                    "turnover_rate": float(row.get("换手率", 0) or 0),
                    "rise_count": int(row.get("上涨家数", 0) or 0),
                    "fall_count": int(row.get("下跌家数", 0) or 0),
                    "leading_stock": str(row.get("领涨股票", "")),
                    "leading_change_pct": float(row.get("领涨股票-涨跌幅", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取行业板块失败: {e}")
            return None

    def get_concept_boards(self) -> Optional[List[Dict[str, Any]]]:
        """
        获取概念板块列表

        Returns:
            概念板块列表
        """
        try:
            df = self.ak.stock_board_concept_name_em()
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "name": str(row.get("板块名称", "")),
                    "code": str(row.get("板块代码", "")),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "total_market_cap": float(row.get("总市值", 0) or 0),
                    "turnover_rate": float(row.get("换手率", 0) or 0),
                    "rise_count": int(row.get("上涨家数", 0) or 0),
                    "fall_count": int(row.get("下跌家数", 0) or 0),
                    "leading_stock": str(row.get("领涨股票", "")),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取概念板块失败: {e}")
            return None

    def get_board_stocks(self, board_name: str, board_type: str = "industry") -> Optional[List[Dict[str, Any]]]:
        """
        获取板块成分股

        Args:
            board_name: 板块名称
            board_type: 板块类型 (industry/concept)

        Returns:
            成分股列表
        """
        try:
            if board_type == "industry":
                df = self.ak.stock_board_industry_cons_em(symbol=board_name)
            else:
                df = self.ak.stock_board_concept_cons_em(symbol=board_name)

            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "current_price": float(row.get("最新价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取板块成分股失败: {e}")
            return None

    # ==================== 龙虎榜数据 ====================

    def get_lhb_detail(self, start_date: str, end_date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取龙虎榜详情

        Args:
            start_date: 开始日期 (YYYYMMDD)
            end_date: 结束日期 (YYYYMMDD)

        Returns:
            龙虎榜数据列表
        """
        try:
            df = self.ak.stock_lhb_detail_em(start_date=start_date, end_date=end_date)
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": str(row.get("代码", "")),
                    "name": str(row.get("名称", "")),
                    "date": str(row.get("上榜日", "")),
                    "reason": str(row.get("解读", "")),
                    "close_price": float(row.get("收盘价", 0) or 0),
                    "change_percent": float(row.get("涨跌幅", 0) or 0),
                    "buy_amount": float(row.get("龙虎榜净买额", 0) or 0),
                    "turnover_rate": float(row.get("换手率", 0) or 0),
                    "float_market_cap": float(row.get("流通市值", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取龙虎榜详情失败: {e}")
            return None

    # ==================== 财务数据 ====================

    def get_financial_indicator(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取财务指标

        Args:
            stock_code: 股票代码

        Returns:
            财务指标数据
        """
        try:
            df = self.ak.stock_financial_analysis_indicator(symbol=stock_code)
            if df.empty:
                return None

            # 取最新一期数据
            row = df.iloc[0]
            return {
                "report_date": str(row.get("日期", "")),
                "eps": float(row.get("摊薄每股收益(元)", 0) or 0),
                "roe": float(row.get("净资产收益率(%)", 0) or 0),
                "gross_margin": float(row.get("销售毛利率(%)", 0) or 0),
                "net_margin": float(row.get("销售净利率(%)", 0) or 0),
                "debt_ratio": float(row.get("资产负债率(%)", 0) or 0),
                "current_ratio": float(row.get("流动比率", 0) or 0),
            }
        except Exception as e:
            logger.error(f"AkShare 获取财务指标失败: {e}")
            return None

    # ==================== 业绩预告 ====================

    def get_performance_forecast(self, date: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取业绩预告

        Args:
            date: 报告期 (如 "20240331")

        Returns:
            业绩预告列表
        """
        try:
            df = self.ak.stock_yjyg_em(date=date)
            if df.empty:
                return None

            result = []
            for _, row in df.head(100).iterrows():
                result.append({
                    "code": str(row.get("股票代码", "")),
                    "name": str(row.get("股票简称", "")),
                    "forecast_type": str(row.get("预告类型", "")),
                    "forecast_content": str(row.get("业绩预告内容", "")),
                    "forecast_net_profit_min": float(row.get("预告净利润下限", 0) or 0),
                    "forecast_net_profit_max": float(row.get("预告净利润上限", 0) or 0),
                    "change_reason": str(row.get("业绩变动原因", "")),
                    "report_date": str(row.get("预告日期", "")),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取业绩预告失败: {e}")
            return None


    # ==================== 新闻资讯 ====================

    def get_stock_news(self, stock_code: str) -> Optional[List[Dict[str, Any]]]:
        """
        获取个股新闻

        Args:
            stock_code: 股票代码

        Returns:
            新闻列表
        """
        try:
            df = self.ak.stock_news_em(symbol=stock_code)
            if df.empty:
                return None

            result = []
            for _, row in df.head(20).iterrows():
                result.append({
                    "title": str(row.get("新闻标题", "")),
                    "content": str(row.get("新闻内容", "")),
                    "publish_time": str(row.get("发布时间", "")),
                    "source": str(row.get("文章来源", "")),
                    "url": str(row.get("新闻链接", "")),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取个股新闻失败: {e}")
            return None

    # ==================== 股票列表 ====================

    def get_stock_list(self) -> Optional[List[Dict[str, str]]]:
        """
        获取A股股票列表

        Returns:
            股票列表
        """
        cache_key = "stock_list"
        if self._is_cache_valid(cache_key, "stock_list"):
            return self._cache[cache_key]

        try:
            df = self.ak.stock_info_a_code_name()
            if df.empty:
                return None

            result = []
            for _, row in df.iterrows():
                result.append({
                    "code": str(row.get("code", "")),
                    "name": str(row.get("name", "")),
                })

            # 缓存结果
            self._cache[cache_key] = result
            self._cache_time[cache_key] = datetime.now()
            return result
        except Exception as e:
            logger.error(f"AkShare 获取股票列表失败: {e}")
            return None

    async def search_stock(self, keyword: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        搜索股票

        Args:
            keyword: 搜索关键词 (代码或名称)
            limit: 返回结果数量限制

        Returns:
            匹配的股票列表
        """
        try:
            def _search():
                # 如果是纯数字，直接按代码搜索
                if keyword.isdigit():
                    df = self.ak.stock_zh_a_spot_em()
                    matches = df[df["代码"].str.contains(keyword, na=False)]
                    results = []
                    for _, row in matches.head(limit).iterrows():
                        results.append({
                            "code": str(row.get("代码", "")),
                            "name": str(row.get("名称", "")),
                            "market": "SH" if str(row.get("代码", "")).startswith(('6', '9')) else "SZ"
                        })
                    return results
                
                # 按名称模糊搜索
                df = self.ak.stock_zh_a_spot_em()
                matches = df[df["名称"].str.contains(keyword, na=False)]
                results = []
                for _, row in matches.head(limit).iterrows():
                    results.append({
                        "code": str(row.get("代码", "")),
                        "name": str(row.get("名称", "")),
                        "market": "SH" if str(row.get("代码", "")).startswith(('6', '9')) else "SZ"
                    })
                return results
            
            return await self._run_in_executor(_search)
        except Exception as e:
            logger.error(f"AkShare 搜索股票失败: {keyword}, 错误: {str(e)}")
            return []

    # ==================== 融资融券 ====================

    def get_margin_data(self, stock_code: str) -> Optional[Dict[str, Any]]:
        """
        获取个股融资融券数据

        Args:
            stock_code: 股票代码

        Returns:
            融资融券数据
        """
        try:
            # 获取深市融资融券数据
            df = self.ak.stock_margin_detail_szse(date=datetime.now().strftime("%Y%m%d"))
            if df.empty:
                return None

            row = df[df["证券代码"] == stock_code]
            if row.empty:
                return None

            r = row.iloc[0]
            return {
                "code": stock_code,
                "margin_balance": float(r.get("融资余额", 0) or 0),
                "margin_buy": float(r.get("融资买入额", 0) or 0),
                "short_balance": float(r.get("融券余额", 0) or 0),
                "short_sell": float(r.get("融券卖出量", 0) or 0),
            }
        except Exception as e:
            logger.error(f"AkShare 获取融资融券数据失败: {e}")
            return None

    # ==================== 大宗交易 ====================

    def get_block_trade(self, date: str = None) -> Optional[List[Dict[str, Any]]]:
        """
        获取大宗交易数据

        Args:
            date: 日期 (YYYYMMDD)

        Returns:
            大宗交易列表
        """
        try:
            df = self.ak.stock_dzjy_sctj()
            if df.empty:
                return None

            result = []
            for _, row in df.head(50).iterrows():
                result.append({
                    "code": str(row.get("证券代码", "")),
                    "name": str(row.get("证券简称", "")),
                    "trade_date": str(row.get("交易日期", "")),
                    "price": float(row.get("成交价", 0) or 0),
                    "volume": int(row.get("成交量", 0) or 0),
                    "amount": float(row.get("成交额", 0) or 0),
                    "premium_rate": float(row.get("折溢率", 0) or 0),
                })
            return result
        except Exception as e:
            logger.error(f"AkShare 获取大宗交易数据失败: {e}")
            return None


# 创建全局服务实例
akshare_service = AkShareService()
