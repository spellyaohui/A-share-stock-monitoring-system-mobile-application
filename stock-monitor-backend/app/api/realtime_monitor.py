"""
实时监测 API - 专门用于监测股票的实时数据获取
特点：
1. 只获取用户监测的股票，数据量小
2. 使用更短的缓存时间（10秒）
3. 直接调用 AkShare 获取最新数据
4. 支持触发预警检查
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Dict, Any, Optional
from datetime import datetime, time
import asyncio
from concurrent.futures import ThreadPoolExecutor
import akshare as ak

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.monitor import Monitor
from app.models.stock import Stock
from app.core.logging import get_logger

logger = get_logger(__name__)
router = APIRouter(prefix="/api/realtime", tags=["实时监测"])

# 线程池用于执行同步的 AkShare 调用
executor = ThreadPoolExecutor(max_workers=2)

# 监测专用缓存（更短的 TTL）
_monitor_cache: Dict[str, Any] = {}
_monitor_cache_time: Optional[datetime] = None
_MONITOR_CACHE_TTL = 10  # 监测缓存只有 10 秒


def is_trading_time() -> bool:
    """判断是否在交易时间"""
    now = datetime.now()
    if now.weekday() >= 5:
        return False
    
    current_time = now.time()
    morning_start = time(9, 25)
    morning_end = time(11, 30)
    afternoon_start = time(13, 0)
    afternoon_end = time(15, 0)
    
    return (morning_start <= current_time <= morning_end or 
            afternoon_start <= current_time <= afternoon_end)


def is_monitor_cache_valid() -> bool:
    """检查监测缓存是否有效"""
    global _monitor_cache_time
    if not _monitor_cache_time or not _monitor_cache:
        return False
    
    elapsed = (datetime.now() - _monitor_cache_time).total_seconds()
    
    # 交易时间内使用短缓存，非交易时间使用长缓存
    if is_trading_time():
        return elapsed <= _MONITOR_CACHE_TTL
    else:
        return elapsed <= 300  # 非交易时间 5 分钟缓存


async def fetch_realtime_quotes(stock_codes: List[str]) -> Dict[str, Dict]:
    """
    获取指定股票的实时行情
    使用 stock_bid_ask_em 个股接口，10秒缓存，避免频繁调用全市场接口
    """
    global _monitor_cache, _monitor_cache_time
    
    if not stock_codes:
        return {}
    
    def safe_float(val, default=0):
        """安全转换为浮点数，处理 '-' 和 NaN"""
        if val is None or val == '-' or val == '':
            return default
        try:
            result = float(val)
            import math
            if math.isnan(result) or math.isinf(result):
                return default
            return result
        except (ValueError, TypeError):
            return default
    
    # 检查缓存
    if is_monitor_cache_valid():
        result = {}
        missing_codes = []
        for code in stock_codes:
            if code in _monitor_cache:
                result[code] = _monitor_cache[code]
            else:
                missing_codes.append(code)
        
        if not missing_codes:
            return result
    else:
        missing_codes = stock_codes
        result = {}
    
    # 使用 stock_bid_ask_em 个股接口获取数据
    try:
        loop = asyncio.get_event_loop()
        
        for code in missing_codes:
            try:
                # 使用个股盘口接口
                df = await loop.run_in_executor(executor, lambda c=code: ak.stock_bid_ask_em(symbol=c))
                if df is not None and not df.empty:
                    data = dict(zip(df["item"], df["value"]))
                    
                    price = safe_float(data.get("最新"))
                    pre_close = safe_float(data.get("昨收"))
                    
                    # 非交易时间：如果最新价为0但昨收有值，使用昨收
                    if price == 0 and pre_close > 0:
                        price = pre_close
                    
                    # 计算涨跌额
                    change = round(price - pre_close, 2) if pre_close > 0 else 0
                    
                    quote = {
                        'code': code,
                        'name': str(data.get("名称", "")),
                        'price': price,
                        'change': change,
                        'change_percent': safe_float(data.get("涨幅")),
                        'open': safe_float(data.get("今开")),
                        'high': safe_float(data.get("最高")),
                        'low': safe_float(data.get("最低")),
                        'pre_close': pre_close,
                        'volume': int(safe_float(data.get("总手", 0)) * 100),
                        'amount': safe_float(data.get("金额")),
                        'volume_ratio': safe_float(data.get("量比")),
                        'turnover_rate': safe_float(data.get("换手")),
                        'limit_up': safe_float(data.get("涨停")),
                        'limit_down': safe_float(data.get("跌停")),
                        'update_time': datetime.now().isoformat()
                    }
                    result[code] = quote
                    _monitor_cache[code] = quote
            except Exception as e:
                logger.warning(f"获取股票 {code} 行情失败: {e}")
        
        _monitor_cache_time = datetime.now()
        return result
        
    except Exception as e:
        logger.error(f"获取实时行情失败: {e}")
        return result


def check_alerts(monitor: Monitor, quote: Dict) -> List[Dict]:
    """
    检查监测预警条件
    返回触发的预警列表
    """
    alerts = []
    price = quote.get('price', 0)
    change_percent = quote.get('change_percent', 0)
    
    if not price:
        return alerts
    
    # 检查最高价预警（price_max）
    if monitor.price_max and price >= float(monitor.price_max):
        alerts.append({
            'type': 'price_max',
            'message': f'股价 {price:.2f} 已达到或超过预警价 {float(monitor.price_max):.2f}',
            'level': 'warning'
        })
    
    # 检查最低价预警（price_min）
    if monitor.price_min and price <= float(monitor.price_min):
        alerts.append({
            'type': 'price_min',
            'message': f'股价 {price:.2f} 已达到或低于预警价 {float(monitor.price_min):.2f}',
            'level': 'warning'
        })
    
    # 检查涨幅预警（rise_threshold）
    if monitor.rise_threshold and change_percent >= float(monitor.rise_threshold):
        alerts.append({
            'type': 'rise',
            'message': f'涨幅 {change_percent:.2f}% 已达到或超过预警值 {float(monitor.rise_threshold):.2f}%',
            'level': 'info'
        })
    
    # 检查跌幅预警（fall_threshold）
    if monitor.fall_threshold and change_percent <= -float(monitor.fall_threshold):
        alerts.append({
            'type': 'fall',
            'message': f'跌幅 {abs(change_percent):.2f}% 已达到或超过预警值 {float(monitor.fall_threshold):.2f}%',
            'level': 'danger'
        })
    
    return alerts


@router.get("/monitors")
async def get_realtime_monitors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    获取用户监测的股票实时数据
    - 只获取用户监测的股票
    - 使用 10 秒短缓存
    - 返回实时价格和预警状态
    """
    try:
        # 1. 获取用户的监测列表
        result = await db.execute(
            select(Monitor, Stock)
            .join(Stock, Monitor.stock_id == Stock.id)
            .where(Monitor.user_id == current_user.id)
        )
        monitors_with_stocks = result.all()
        
        if not monitors_with_stocks:
            return {
                "monitors": [],
                "is_trading": is_trading_time(),
                "cache_ttl": _MONITOR_CACHE_TTL if is_trading_time() else 300,
                "update_time": datetime.now().isoformat()
            }
        
        # 2. 提取股票代码
        stock_codes = [stock.code for _, stock in monitors_with_stocks]
        
        # 3. 获取实时行情
        quotes = await fetch_realtime_quotes(stock_codes)
        
        # 4. 组装返回数据
        monitor_list = []
        for monitor, stock in monitors_with_stocks:
            quote = quotes.get(stock.code, {})
            alerts = check_alerts(monitor, quote) if quote else []
            
            monitor_list.append({
                "id": monitor.id,
                "stock_id": stock.id,
                "stock_code": stock.code,
                "stock_name": stock.name,
                "is_active": monitor.is_active,
                # 监测条件（兼容新旧字段名）
                "price_min": float(monitor.price_min) if monitor.price_min else None,
                "price_max": float(monitor.price_max) if monitor.price_max else None,
                "rise_threshold": float(monitor.rise_threshold) if monitor.rise_threshold else None,
                "fall_threshold": float(monitor.fall_threshold) if monitor.fall_threshold else None,
                # 新版字段名（兼容移动端）
                "price_lower": float(monitor.price_min) if monitor.price_min else None,
                "price_upper": float(monitor.price_max) if monitor.price_max else None,
                "change_upper": float(monitor.rise_threshold) if monitor.rise_threshold else None,
                "change_lower": float(monitor.fall_threshold) if monitor.fall_threshold else None,
                # 实时数据
                "price": quote.get('price', 0),
                "current_price": quote.get('price', 0),
                "change": quote.get('change', 0),
                "change_percent": quote.get('change_percent', 0),
                "open": quote.get('open', 0),
                "high": quote.get('high', 0),
                "low": quote.get('low', 0),
                "pre_close": quote.get('pre_close', 0),
                "volume": quote.get('volume', 0),
                "amount": quote.get('amount', 0),
                # 预警状态
                "alerts": alerts,
                "has_alert": len(alerts) > 0
            })
        
        return {
            "monitors": monitor_list,
            "is_trading": is_trading_time(),
            "cache_ttl": _MONITOR_CACHE_TTL if is_trading_time() else 300,
            "update_time": datetime.now().isoformat()
        }
        
    except Exception as e:
        logger.error(f"获取实时监测数据失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取实时监测数据失败: {str(e)}")


@router.get("/quote/{stock_code}")
async def get_single_quote(
    stock_code: str,
    current_user: User = Depends(get_current_user)
):
    """
    获取单只股票的实时行情
    用于股票详情页的实时刷新
    """
    try:
        quotes = await fetch_realtime_quotes([stock_code])
        quote = quotes.get(stock_code)
        
        if not quote:
            raise HTTPException(status_code=404, detail=f"未找到股票 {stock_code} 的行情数据")
        
        return {
            "quote": quote,
            "is_trading": is_trading_time(),
            "update_time": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票 {stock_code} 实时行情失败: {e}")
        raise HTTPException(status_code=500, detail=f"获取实时行情失败: {str(e)}")


@router.get("/status")
async def get_realtime_status():
    """
    获取实时监测服务状态
    """
    return {
        "is_trading": is_trading_time(),
        "cache_valid": is_monitor_cache_valid(),
        "cache_size": len(_monitor_cache),
        "cache_ttl": _MONITOR_CACHE_TTL if is_trading_time() else 300,
        "cache_time": _monitor_cache_time.isoformat() if _monitor_cache_time else None,
        "server_time": datetime.now().isoformat()
    }
