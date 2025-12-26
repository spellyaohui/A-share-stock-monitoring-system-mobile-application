from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_
from typing import Optional, List, Dict, Any
from app.models.stock import Stock
from app.schemas.stock import StockSearch
from app.services.stock_api import stock_api_service
from app.services.akshare_api import akshare_service
from app.core.logging import get_logger

logger = get_logger(__name__)

async def search_stocks(db: AsyncSession, query: str, search_type: Optional[str] = None, limit: int = 10) -> List[StockSearch]:
    """
    搜索股票 - 优先从数据库搜索，如果没有结果则使用在线API
    
    Args:
        db: 数据库会话
        query: 搜索关键词
        search_type: 搜索类型 ("code" 或 None)
        limit: 返回结果数量限制
    
    Returns:
        股票搜索结果列表
    """
    query = query.strip()

    # 首先从数据库搜索
    if search_type == "code":
        # 代码搜索 - 支持6位数字代码
        padded_query = query.zfill(6) if query.isdigit() else query
        result = await db.execute(
            select(Stock).where(
                or_(
                    Stock.code.like(f"{query}%"),
                    Stock.code.like(f"{padded_query}%"),
                    Stock.full_code.like(f"{query}%")
                )
            ).limit(limit)
        )
    else:
        # 名称或混合搜索
        padded_query = query.zfill(6) if query.isdigit() else query
        result = await db.execute(
            select(Stock).where(
                or_(
                    Stock.name.like(f"%{query}%"),
                    Stock.code.like(f"{query}%"),
                    Stock.code.like(f"{padded_query}%")
                )
            ).limit(limit)
        )

    stocks = result.scalars().all()
    db_results = [StockSearch(id=s.id, code=s.code, name=s.name) for s in stocks]
    
    # 如果数据库结果不足，尝试在线搜索
    if len(db_results) < limit:
        try:
            # 首先尝试东方财富API
            online_results = await stock_api_service.search_stock(query, limit - len(db_results))
            
            # 如果东方财富API没有结果，尝试AkShare
            if not online_results:
                online_results = await akshare_service.search_stock(query, limit - len(db_results))
            
            # 转换在线结果格式并去重
            existing_codes = {s.code for s in db_results}
            for result in online_results:
                if result["code"] not in existing_codes:
                    # 使用股票代码作为临时ID
                    temp_id = int(result["code"]) if result["code"].isdigit() else 0
                    db_results.append(StockSearch(
                        id=temp_id,
                        code=result["code"],
                        name=result["name"]
                    ))
                    if len(db_results) >= limit:
                        break
        except Exception as e:
            logger.warning(f"在线搜索股票失败: {query}, 错误: {str(e)}")
    
    return db_results[:limit]

async def get_stock_detail(db: AsyncSession, stock_id: int) -> Optional[Stock]:
    """获取股票详情"""
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    return result.scalar_one_or_none()


async def get_realtime_quote(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取股票实时行情 - 多数据源支持
    
    Args:
        stock_code: 股票代码
    
    Returns:
        实时行情数据
    """
    try:
        # 首先尝试东方财富API（主数据源）
        quote = await stock_api_service.get_realtime_quote(stock_code)
        if quote:
            return quote
        
        # 如果主数据源失败，尝试AkShare
        logger.info(f"主数据源失败，尝试AkShare获取行情: {stock_code}")
        quote = await akshare_service.get_realtime_quote(stock_code)
        if quote:
            return quote
        
        logger.warning(f"所有数据源都无法获取行情: {stock_code}")
        return None
        
    except Exception as e:
        logger.error(f"获取实时行情异常: {stock_code}, 错误: {str(e)}")
        return None


async def get_realtime_quote_for_monitor(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取监测个股的实时行情 - 使用高效的个股专用接口
    
    此方法专为监测少量个股设计，使用雪球数据源的个股接口，
    避免获取全市场数据后筛选，大幅提升效率并减少对数据源的压力。
    
    Args:
        stock_code: 股票代码
    
    Returns:
        实时行情数据（包含更多指标：量比、委比、52周高低等）
    """
    try:
        # 优先使用 AkShare 的个股专用接口（雪球数据源）
        quote = await akshare_service.get_realtime_quote_individual(stock_code)
        if quote:
            return quote
        
        # 如果个股接口失败，回退到东方财富API
        logger.info(f"个股接口失败，回退到东方财富API: {stock_code}")
        quote = await stock_api_service.get_realtime_quote(stock_code)
        if quote:
            return quote
        
        # 最后尝试 AkShare 全市场接口
        logger.info(f"东方财富API失败，尝试AkShare全市场接口: {stock_code}")
        quote = await akshare_service.get_realtime_quote(stock_code)
        if quote:
            return quote
        
        logger.warning(f"所有数据源都无法获取监测行情: {stock_code}")
        return None
        
    except Exception as e:
        logger.error(f"获取监测行情异常: {stock_code}, 错误: {str(e)}")
        return None


async def get_kline_data(
    stock_code: str,
    period: str = "daily",
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    获取K线数据 - 多数据源支持
    
    Args:
        stock_code: 股票代码
        period: 周期
        start_date: 开始日期
        end_date: 结束日期
        limit: 数据条数
    
    Returns:
        K线数据列表
    """
    try:
        # 首先尝试东方财富API
        klines = await stock_api_service.get_kline_data(
            stock_code, period, start_date, end_date, limit
        )
        if klines:
            return klines
        
        # 如果主数据源失败，尝试AkShare
        logger.info(f"主数据源失败，尝试AkShare获取K线: {stock_code}")
        
        # 转换周期格式
        period_map = {
            "1min": "1",
            "5min": "5", 
            "15min": "15",
            "30min": "30",
            "60min": "60",
            "daily": "daily",
            "weekly": "weekly", 
            "monthly": "monthly"
        }
        ak_period = period_map.get(period, "daily")
        
        # 转换日期格式 (YYYY-MM-DD -> YYYYMMDD)
        ak_start = start_date.replace("-", "") if start_date else None
        ak_end = end_date.replace("-", "") if end_date else None
        
        klines = await akshare_service.get_kline_data(
            stock_code, ak_period, ak_start, ak_end, limit=limit
        )
        if klines:
            return klines
        
        logger.warning(f"所有数据源都无法获取K线数据: {stock_code}")
        return []
        
    except Exception as e:
        logger.error(f"获取K线数据异常: {stock_code}, 错误: {str(e)}")
        return []


async def get_batch_quotes(stock_codes: List[str]) -> Dict[str, Dict[str, Any]]:
    """
    批量获取股票实时行情
    
    Args:
        stock_codes: 股票代码列表
    
    Returns:
        股票代码到行情数据的映射
    """
    try:
        # 首先尝试东方财富API批量获取
        quotes = await stock_api_service.get_batch_quotes(stock_codes)
        
        # 对于获取失败的股票，尝试用AkShare单独获取
        failed_codes = [code for code in stock_codes if code not in quotes]
        if failed_codes:
            logger.info(f"部分股票主数据源失败，尝试AkShare: {failed_codes}")
            for code in failed_codes:
                try:
                    quote = await akshare_service.get_realtime_quote(code)
                    if quote:
                        quotes[code] = quote
                except Exception as e:
                    logger.warning(f"AkShare获取行情失败: {code}, 错误: {str(e)}")
        
        return quotes
        
    except Exception as e:
        logger.error(f"批量获取行情异常: {str(e)}")
        return {}


async def get_minute_kline(
    stock_code: str,
    period: str = "5",
    limit: int = 100
) -> List[Dict[str, Any]]:
    """
    获取分钟级K线数据
    
    Args:
        stock_code: 股票代码
        period: 分钟周期 (1/5/15/30/60)
        limit: 数据条数
    
    Returns:
        分钟K线数据列表
    """
    try:
        # 使用AkShare获取分钟K线
        klines = await akshare_service.get_minute_kline(stock_code, period, limit=limit)
        return klines
    except Exception as e:
        logger.error(f"获取分钟K线异常: {stock_code}, 错误: {str(e)}")
        return []


async def get_bid_ask(stock_code: str) -> Optional[Dict[str, Any]]:
    """
    获取五档盘口数据
    
    Args:
        stock_code: 股票代码
    
    Returns:
        五档盘口数据
    """
    try:
        bid_ask = await akshare_service.get_bid_ask(stock_code)
        return bid_ask
    except Exception as e:
        logger.error(f"获取五档盘口异常: {stock_code}, 错误: {str(e)}")
        return None


async def get_hot_stocks(limit: int = 50) -> List[Dict[str, Any]]:
    """
    获取热门股票排名
    
    Args:
        limit: 返回数量
    
    Returns:
        热门股票列表
    """
    try:
        hot_list = await akshare_service.get_hot_rank(limit)
        return hot_list or []
    except Exception as e:
        logger.error(f"获取热门股票异常: {str(e)}")
        return []
