"""
图表API路由
注意：此模块的功能与 stocks.py 中的 kline/indicators 接口重复
为保持向后兼容，这里转发到 stocks 模块的实现
"""
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.services.data_fetcher import data_fetcher
from app.services.stock_service import get_stock_detail
from app.core.logging import get_logger
from app.utils.indicators import calculate_ma, calculate_macd, calculate_rsi

logger = get_logger(__name__)
router = APIRouter()


@router.get("/kline/{stock_id}")
async def get_kline_chart(
    stock_id: int,
    period: str = Query("daily", description="周期: daily/weekly/monthly"),
    limit: int = Query(200, le=500, description="数据条数"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取K线图表数据
    
    注意：建议使用 /api/stocks/{id}/kline 接口，此接口保留用于向后兼容
    """
    try:
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        klines = await data_fetcher.get_kline_data(
            stock_code, period, limit=limit
        )
        
        return {
            "stock": {
                "id": stock.id if stock else stock_id,
                "code": stock.code if stock else stock_code,
                "name": stock.name if stock else ""
            },
            "klines": klines,
            "period": period,
            "total": len(klines)
        }
    except Exception as e:
        logger.error(f"获取K线图表失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取K线数据失败")


@router.get("/indicators/{stock_id}")
async def get_technical_indicators(
    stock_id: int,
    indicator: str = Query("ma", description="技术指标: ma/macd/rsi"),
    period: str = Query("daily", description="周期"),
    db: AsyncSession = Depends(get_db)
):
    """
    获取技术指标数据
    
    注意：建议使用 /api/stocks/{id}/indicators 接口，此接口保留用于向后兼容
    """
    try:
        stock = await get_stock_detail(db, stock_id)
        stock_code = stock.code if stock else str(stock_id).zfill(6)
        
        klines = await data_fetcher.get_kline_data(
            stock_code, period, limit=250
        )
        
        if not klines:
            raise HTTPException(status_code=404, detail="无法获取K线数据")
        
        # 计算技术指标
        indicators_data = {}
        
        if "ma" in indicator:
            indicators_data["ma"] = {
                "ma5": calculate_ma(klines, 5),
                "ma10": calculate_ma(klines, 10),
                "ma20": calculate_ma(klines, 20),
                "ma60": calculate_ma(klines, 60)
            }
        
        if "macd" in indicator:
            indicators_data["macd"] = calculate_macd(klines)
        
        if "rsi" in indicator:
            indicators_data["rsi"] = calculate_rsi(klines)
        
        return {
            "stock": {
                "id": stock.id if stock else stock_id,
                "code": stock.code if stock else stock_code,
                "name": stock.name if stock else ""
            },
            "indicators": indicators_data,
            "period": period
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"获取技术指标失败: {stock_id}, 错误: {str(e)}")
        raise HTTPException(status_code=500, detail="获取技术指标失败")


# 为了向后兼容，保留 /kline/{stock_id} 路由
# 但建议前端统一使用 /api/stocks/{id}/kline
