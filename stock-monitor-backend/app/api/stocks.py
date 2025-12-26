from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
from app.services.stock_service import search_stocks, get_stock_detail
from app.services.data_fetcher import data_fetcher
from app.services.akshare_api import akshare_service
from app.database import get_db
from app.core.logging import get_logger
from app.utils.indicators import calculate_ma, calculate_rsi, calculate_macd

logger = get_logger(__name__)
router = APIRouter()


@router.get("/search")
async def search_stock(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    type: Optional[str] = Query(None, description="搜索类型: code/name"),
    limit: int = Query(10, le=50, description="返回结果数量限制"),
    db: AsyncSession = Depends(get_db)
):
    """搜索股票 - 支持代码和名称搜索"""
    try:
        results = await search_stocks(db, q, type, limit)
        
        # 转换为前端期望的格式
        formatted_results = []
        for stock in results:
            stock_id = stock.id if stock.id != 0 else int(stock.code)
            formatted_results.append({
                "id": stock_id,
                "code": stock.code,
                "name": stock.name,
                "market": "SH" if stock.code.startswith(('6', '9')) else "SZ",
                "full_code": f"{stock.code}.{'SH' if stock.code.startswith(('6', '9')) else 'SZ'}"
            })
        
        return formatted_results
        
    except Exception as e:
        logger.error(f"搜索股票失败: {q}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="搜索失败")


@router.get("/{stock_id}")
async def get_stock_detail_api(
    stock_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取股票详情"""
    try:
        stock = await get_stock_detail(db, stock_id)
        if not stock:
            # 尝试按代码查找
            stock_code = str(stock_id).zfill(6)
            # 这里可以从在线API获取股票信息并创建记录
            raise HTTPException(status_code=404, detail="股票不存在")
        
        return {
            "id": stock.id,
            "code": stock.code,
            "name": stock.name,
            "market": stock.market,
            "full_code": stock.full_code
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取股票详情失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取股票详情失败")


@router.get("/{stock_id}/realtime")
async def get_stock_realtime(
    stock_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取股票实时行情"""
    try:
        # 获取股票信息
        stock = await get_stock_detail(db, stock_id)
        stock_code = None
        
        if stock:
            stock_code = stock.code
        else:
            # 如果数据库中没有，尝试直接用stock_id作为代码
            stock_code = str(stock_id).zfill(6)
        
        # 获取实时行情
        quote = await data_fetcher.get_realtime_quote(stock_code)
        if not quote:
            # 返回基本信息，标记数据不可用
            return {
                "code": stock_code,
                "name": stock.name if stock else "",
                "price": 0,
                "change": 0,
                "change_percent": 0,
                "open": 0,
                "high": 0,
                "low": 0,
                "pre_close": 0,
                "volume": 0,
                "amount": 0,
                "data_unavailable": True,
                "message": "该股票暂无实时行情数据（可能是北交所、退市股或停牌股票）"
            }
        
        return quote
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取实时行情失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取实时行情失败: {str(e)}")


@router.get("/{stock_id}/daily")
async def get_stock_daily(
    stock_id: int,
    start: Optional[str] = Query(None, description="开始日期 YYYY-MM-DD"),
    end: Optional[str] = Query(None, description="结束日期 YYYY-MM-DD"),
    db: AsyncSession = Depends(get_db)
):
    """获取股票日线数据"""
    try:
        # 获取股票代码
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        # 获取日线数据
        klines = await data_fetcher.get_kline_data(
            stock_code, "daily", start, end, limit=250
        )
        
        return klines
    except Exception as e:
        logger.error(f"获取日线数据失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取日线数据失败")


@router.get("/{stock_id}/kline")
async def get_stock_kline(
    stock_id: int,
    type: str = Query("day", description="K线类型: day/week/month"),
    limit: int = Query(200, le=500, description="数据条数"),
    db: AsyncSession = Depends(get_db)
):
    """获取K线数据"""
    try:
        # 获取股票代码
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        # 转换周期格式
        period_map = {
            "day": "daily",
            "week": "weekly", 
            "month": "monthly"
        }
        period = period_map.get(type, "daily")
        
        # 获取K线数据
        klines = await data_fetcher.get_kline_data(
            stock_code, period, limit=limit
        )
        
        return {
            "klines": klines,
            "period": type,
            "total": len(klines)
        }
    except Exception as e:
        logger.error(f"获取K线数据失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取K线数据失败")


@router.get("/{stock_id}/indicators")
async def get_stock_indicators(
    stock_id: int,
    indicator: str = Query("ma", description="技术指标: ma,macd,kdj"),
    db: AsyncSession = Depends(get_db)
):
    """获取技术指标"""
    try:
        # 获取股票代码
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        # 获取K线数据用于计算指标
        klines = await data_fetcher.get_kline_data(
            stock_code, "daily", limit=250
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail="无法获取K线数据")
        
        # 计算技术指标
        indicators_data = {}
        if "ma" in indicator:
            ma5 = calculate_ma(klines, 5)
            ma10 = calculate_ma(klines, 10)
            ma20 = calculate_ma(klines, 20)
            indicators_data = {
                "ma5": ma5,
                "ma10": ma10,
                "ma20": ma20
            }
        
        return indicators_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技术指标失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取技术指标失败")


# ==================== 新增接口 ====================

@router.get("/{stock_id}/bid-ask")
async def get_stock_bid_ask(
    stock_id: int,
    db: AsyncSession = Depends(get_db)
):
    """获取股票五档盘口数据"""
    try:
        # 获取股票代码
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        # 获取五档盘口
        bid_ask = await akshare_service.get_bid_ask(stock_code)
        if not bid_ask:
            raise HTTPException(status_code=404, detail="无法获取盘口数据")
        
        return bid_ask
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取五档盘口失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取盘口数据失败")


@router.get("/{stock_id}/kline-minute")
async def get_stock_minute_kline(
    stock_id: int,
    period: str = Query("5", description="分钟周期: 1/5/15/30/60"),
    limit: int = Query(100, le=500, description="数据条数"),
    db: AsyncSession = Depends(get_db)
):
    """获取分钟级K线数据"""
    try:
        # 验证周期参数
        valid_periods = ["1", "5", "15", "30", "60"]
        if period not in valid_periods:
            raise HTTPException(status_code=400, detail=f"无效的周期参数，支持: {valid_periods}")
        
        # 获取股票代码
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        # 获取分钟K线
        klines = await akshare_service.get_minute_kline(stock_code, period, limit=limit)
        
        return {
            "klines": klines,
            "period": f"{period}min",
            "total": len(klines)
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取分钟K线失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取分钟K线失败")


@router.get("/market/hot-rank")
async def get_hot_rank(
    limit: int = Query(50, le=100, description="返回数量")
):
    """获取热门股票排名"""
    try:
        hot_list = await akshare_service.get_hot_rank(limit)
        if not hot_list:
            return {"list": [], "total": 0}
        
        return {
            "list": hot_list,
            "total": len(hot_list)
        }
    except Exception as e:
        logger.error(f"获取热门股票排名失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取热门排名失败")


@router.get("/market/hot-keywords")
async def get_hot_keywords():
    """获取热门关键词/概念"""
    try:
        keywords = await akshare_service.get_hot_keywords()
        if not keywords:
            return {"list": [], "total": 0}
        
        return {
            "list": keywords,
            "total": len(keywords)
        }
    except Exception as e:
        logger.error(f"获取热门关键词失败: {str(e)}")
        raise HTTPException(status_code=500, detail="获取热门关键词失败")