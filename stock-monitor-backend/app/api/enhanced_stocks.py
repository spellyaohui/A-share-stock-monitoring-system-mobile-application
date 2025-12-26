"""
增强版股票API - 提供更丰富的数据和功能
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, List
import akshare as ak
import pandas as pd
from datetime import datetime, timedelta
import asyncio
from concurrent.futures import ThreadPoolExecutor

from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/api/enhanced", tags=["增强功能"])

# 创建线程池用于执行同步的akshare调用
executor = ThreadPoolExecutor(max_workers=4)

async def run_in_executor(func, *args):
    """在线程池中运行同步函数"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(executor, func, *args)


@router.get("/market/overview")
async def get_market_overview():
    """
    获取市场概况
    优先使用缓存数据，避免频繁调用 AkShare API
    """
    import math
    import numpy as np
    
    def clean_nan(data):
        """递归清理数据中的 NaN 和 Inf 值"""
        if isinstance(data, list):
            return [clean_nan(item) for item in data]
        elif isinstance(data, dict):
            return {k: clean_nan(v) for k, v in data.items()}
        elif isinstance(data, float):
            if math.isnan(data) or math.isinf(data):
                return 0
            return data
        elif isinstance(data, (np.floating, np.integer)):
            val = float(data)
            if math.isnan(val) or math.isinf(val):
                return 0
            return val
        return data
    
    try:
        from app.services.market_cache import market_cache
        
        # 检查缓存是否有效
        if market_cache.is_cache_valid():
            # 使用缓存数据
            market_stats = market_cache.get_market_stats()
            top_volume = market_cache.get_top_stocks('amount', 10)
            top_gainers = market_cache.get_top_stocks('change', 10)
            top_losers = market_cache.get_top_stocks('change_down', 10)
            
            return clean_nan({
                "market_stats": market_stats,
                "top_volume": top_volume,
                "top_gainers": top_gainers,
                "top_losers": top_losers,
                "from_cache": True,
                "timestamp": datetime.now().isoformat()
            })
        
        # 缓存无效，刷新数据
        success = await market_cache.refresh_market_data()
        
        if not success:
            # 刷新失败，返回空数据
            return {
                "market_stats": {},
                "top_volume": [],
                "top_gainers": [],
                "top_losers": [],
                "from_cache": False,
                "error": "市场数据刷新失败",
                "timestamp": datetime.now().isoformat()
            }
        
        market_stats = market_cache.get_market_stats()
        top_volume = market_cache.get_top_stocks('amount', 10)
        top_gainers = market_cache.get_top_stocks('change', 10)
        top_losers = market_cache.get_top_stocks('change_down', 10)
        
        return clean_nan({
            "market_stats": market_stats,
            "top_volume": top_volume,
            "top_gainers": top_gainers,
            "top_losers": top_losers,
            "from_cache": False,
            "timestamp": datetime.now().isoformat()
        })
    except Exception as e:
        logger.error(f"获取市场概况失败: {e}")
        # 返回空数据而不是抛出异常
        return {
            "market_stats": {},
            "top_volume": [],
            "top_gainers": [],
            "top_losers": [],
            "from_cache": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }


@router.get("/market/cache-status")
async def get_cache_status():
    """获取市场数据缓存状态"""
    try:
        from app.services.market_cache import market_cache
        return market_cache.get_cache_info()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取缓存状态失败: {str(e)}")


@router.post("/market/refresh-cache")
async def refresh_market_cache():
    """手动刷新市场数据缓存"""
    try:
        from app.services.market_cache import market_cache
        success = await market_cache.refresh_market_data()
        if success:
            return {"message": "缓存刷新成功", "cache_info": market_cache.get_cache_info()}
        else:
            raise HTTPException(status_code=500, detail="缓存刷新失败")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"刷新缓存失败: {str(e)}")


@router.get("/stocks/{stock_code}/financial")
async def get_stock_financial(stock_code: str):
    """获取股票财务数据"""
    try:
        # 获取个股基本信息（这个接口很快）
        basic_info = {}
        try:
            individual_info = await run_in_executor(ak.stock_individual_info_em, stock_code)
            if not individual_info.empty:
                info_dict = dict(zip(individual_info['item'], individual_info['value']))
                basic_info = {
                    "股票代码": info_dict.get('股票代码', stock_code),
                    "股票名称": info_dict.get('股票简称', ''),
                    "最新价": info_dict.get('最新', 0),
                    "总股本": info_dict.get('总股本', 0),
                    "流通股": info_dict.get('流通股', 0),
                    "总市值": info_dict.get('总市值', 0),
                    "流通市值": info_dict.get('流通市值', 0),
                    "行业": info_dict.get('行业', ''),
                    "上市时间": info_dict.get('上市时间', '')
                }
        except Exception as e:
            print(f"获取个股基本信息失败: {e}")
        
        # 获取财务比率 - 优先使用市场缓存
        financial_ratios = {}
        try:
            # 1. 优先从市场缓存获取（最快，不会触发全市场请求）
            from app.services.market_cache import market_cache
            quote = market_cache.get_stock_realtime(stock_code)
            
            # 2. 如果缓存没有，使用 data_fetcher（会自动处理缓存）
            if not quote:
                from app.services.data_fetcher import data_fetcher
                quote = await data_fetcher.get_realtime_quote(stock_code)
            
            if quote:
                financial_ratios = {
                    "市盈率_动态": quote.get('pe_ratio', 0) or 0,
                    "市净率": quote.get('pb_ratio', 0) or 0,
                    "换手率": quote.get('turnover_rate', 0) or 0,
                    "成交量": quote.get('volume', 0) or 0,
                    "成交额": quote.get('amount', 0) or 0,
                    "振幅": quote.get('amplitude', 0) or 0,
                    "量比": quote.get('volume_ratio', 0) or 0,
                    "涨速": 0,
                    "60日涨跌幅": 0,
                    "年初至今涨跌幅": 0
                }
                print(f"财务数据获取成功: 市盈率={financial_ratios['市盈率_动态']}, 市净率={financial_ratios['市净率']}")
        except Exception as e:
            print(f"获取财务比率失败: {e}")
        
        # 获取同行业对比数据（可选，可能较慢）
        industry_comparison = []
        try:
            if basic_info.get('行业'):
                industry_stocks = await run_in_executor(ak.stock_board_industry_cons_em, basic_info['行业'])
                if not industry_stocks.empty:
                    industry_comparison = industry_stocks.head(10)[
                        ['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率', '总市值']
                    ].to_dict('records')
        except Exception as e:
            print(f"获取行业对比失败: {e}")
        
        # 股东信息暂时跳过，因为接口返回的是全市场数据
        shareholders_info = []
        
        # 构建财务报表数据（基于可用信息）
        balance_sheet = []
        income_statement = []
        cash_flow = []
        
        if basic_info:
            balance_sheet = [{
                "报告期": "最新数据",
                "总股本": basic_info.get('总股本', 0),
                "流通股": basic_info.get('流通股', 0),
                "总市值": basic_info.get('总市值', 0),
                "流通市值": basic_info.get('流通市值', 0),
                "市净率": financial_ratios.get('市净率', 0),
                "说明": "基于实时数据计算"
            }]
            
            # 利润表相关数据
            income_statement = [{
                "报告期": "最新数据",
                "市盈率_动态": financial_ratios.get('市盈率_动态', 0),
                "最新价": basic_info.get('最新价', 0),
                "年初至今涨跌幅": financial_ratios.get('年初至今涨跌幅', 0),
                "60日涨跌幅": financial_ratios.get('60日涨跌幅', 0),
                "说明": "基于实时数据计算"
            }]
            
            # 现金流量表相关数据
            cash_flow = [{
                "报告期": "最新数据",
                "成交量": financial_ratios.get('成交量', 0),
                "成交额": financial_ratios.get('成交额', 0),
                "换手率": financial_ratios.get('换手率', 0),
                "量比": financial_ratios.get('量比', 0),
                "说明": "基于实时交易数据"
            }]
        
        return {
            "basic_info": basic_info,
            "financial_ratios": financial_ratios,
            "balance_sheet": balance_sheet,
            "income_statement": income_statement,
            "cash_flow": cash_flow,
            "industry_comparison": industry_comparison,
            "shareholders_info": shareholders_info,
            "note": "基于AkShare可用接口提供的实时财务数据",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "basic_info": {},
            "financial_ratios": {},
            "balance_sheet": [],
            "income_statement": [],
            "cash_flow": [],
            "industry_comparison": [],
            "shareholders_info": [],
            "error": f"获取数据失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stocks/{stock_code}/news")
async def get_stock_news(stock_code: str, limit: int = Query(10, le=50)):
    """获取股票新闻"""
    try:
        news_data = await run_in_executor(ak.stock_news_em, stock_code)
        
        if news_data.empty:
            return {"news": [], "timestamp": datetime.now().isoformat()}
        
        # 限制返回数量
        news_list = news_data.head(limit).to_dict('records')
        
        return {
            "news": news_list,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "news": [],
            "error": f"获取新闻失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stocks/{stock_code}/fund_flow")
async def get_stock_fund_flow(stock_code: str):
    """获取股票资金流向"""
    try:
        # 确定市场
        market = "sz" if stock_code.startswith(('000', '002', '300')) else "sh"
        
        fund_flow = await run_in_executor(ak.stock_individual_fund_flow, stock_code, market)
        
        if fund_flow.empty:
            return {"fund_flow": [], "timestamp": datetime.now().isoformat()}
        
        return {
            "fund_flow": fund_flow.head(30).to_dict('records'),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "fund_flow": [],
            "error": f"获取资金流向失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/market/sectors")
async def get_market_sectors():
    """获取行业板块数据（带缓存）"""
    try:
        from app.services.market_cache import market_cache
        import math
        import numpy as np
        
        def clean_nan(data):
            """递归清理数据中的 NaN 和 Inf 值"""
            if isinstance(data, list):
                return [clean_nan(item) for item in data]
            elif isinstance(data, dict):
                return {k: clean_nan(v) for k, v in data.items()}
            elif isinstance(data, float):
                if math.isnan(data) or math.isinf(data):
                    return 0
                return data
            elif isinstance(data, (np.floating, np.integer)):
                val = float(data)
                if math.isnan(val) or math.isinf(val):
                    return 0
                return val
            return data
        
        def clean_dataframe(df):
            """清理 DataFrame 中的所有非法值"""
            # 替换所有 NaN 和 Inf 为 0
            df = df.replace([np.inf, -np.inf], 0)
            df = df.fillna(0)
            # 对于字符串列，将 '-' 替换为空字符串
            for col in df.select_dtypes(include=['object']).columns:
                df[col] = df[col].replace('-', '')
            return df
        
        # 检查缓存
        cached_data = market_cache.get_sectors_cache()
        if cached_data:
            return {
                **clean_nan(cached_data),
                "from_cache": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # 缓存无效，获取新数据
        result = {"industries": [], "concepts": []}
        
        # 获取行业板块
        try:
            industry_data = await run_in_executor(ak.stock_board_industry_name_em)
            if industry_data is not None and not industry_data.empty:
                # 清理数据
                industry_data = clean_dataframe(industry_data)
                records = industry_data.to_dict('records')
                result["industries"] = clean_nan(records)
        except Exception as e:
            logger.warning(f"获取行业板块失败: {e}")
        
        # 获取概念板块
        try:
            concept_data = await run_in_executor(ak.stock_board_concept_name_em)
            if concept_data is not None and not concept_data.empty:
                # 清理数据
                concept_data = clean_dataframe(concept_data)
                records = concept_data.head(50).to_dict('records')  # 概念板块太多，限制50个
                result["concepts"] = clean_nan(records)
        except Exception as e:
            logger.warning(f"获取概念板块失败: {e}")
        
        # 存入缓存（即使部分数据为空也缓存）
        if result["industries"] or result["concepts"]:
            market_cache.set_sectors_cache(result)
        
        return {
            **clean_nan(result),
            "from_cache": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"获取板块数据失败: {e}")
        # 返回空数据而不是抛出异常
        return {
            "industries": [],
            "concepts": [],
            "from_cache": False,
            "error": str(e),
            "timestamp": datetime.now().isoformat()
        }

@router.get("/market/lhb")
async def get_dragon_tiger_list():
    """获取龙虎榜数据（带缓存）"""
    try:
        from app.services.market_cache import market_cache
        import math
        import numpy as np
        
        def clean_nan(data):
            """递归清理数据中的 NaN 和 Inf 值"""
            if isinstance(data, list):
                return [clean_nan(item) for item in data]
            elif isinstance(data, dict):
                return {k: clean_nan(v) for k, v in data.items()}
            elif isinstance(data, float):
                if math.isnan(data) or math.isinf(data):
                    return 0
                return data
            elif isinstance(data, (np.floating, np.integer)):
                val = float(data)
                if math.isnan(val) or math.isinf(val):
                    return 0
                return val
            return data
        
        # 检查缓存
        cached_data = market_cache.get_lhb_cache()
        if cached_data:
            return {
                "lhb_data": clean_nan(cached_data),
                "from_cache": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # 缓存无效，获取新数据
        # 使用股票龙虎榜统计接口
        lhb_data = await run_in_executor(ak.stock_lhb_stock_statistic_em, "近一月")
        
        if lhb_data is None or lhb_data.empty:
            return {"lhb_data": [], "from_cache": False, "timestamp": datetime.now().isoformat()}
        
        # 清理数据
        lhb_data = lhb_data.replace([np.inf, -np.inf], 0)
        lhb_data = lhb_data.fillna(0)
        result = clean_nan(lhb_data.head(50).to_dict('records'))
        
        # 存入缓存
        market_cache.set_lhb_cache(result)
        
        return {
            "lhb_data": result,
            "from_cache": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "lhb_data": [],
            "from_cache": False,
            "error": f"获取龙虎榜数据失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/stocks/{stock_code}/technical")
async def get_stock_technical(stock_code: str):
    """获取股票技术指标"""
    try:
        # 获取历史数据用于计算技术指标
        end_date = datetime.now().strftime("%Y%m%d")
        start_date = (datetime.now() - timedelta(days=365)).strftime("%Y%m%d")
        
        hist_data = await run_in_executor(
            ak.stock_zh_a_hist, 
            stock_code, 
            "daily", 
            start_date, 
            end_date, 
            ""
        )
        
        if hist_data.empty:
            return {"technical": {}, "timestamp": datetime.now().isoformat()}
        
        # 计算简单技术指标
        latest = hist_data.iloc[-1]
        recent_20 = hist_data.tail(20)
        recent_60 = hist_data.tail(60)
        
        ma5 = recent_20.tail(5)['收盘'].mean() if len(recent_20) >= 5 else None
        ma10 = recent_20.tail(10)['收盘'].mean() if len(recent_20) >= 10 else None
        ma20 = recent_20['收盘'].mean() if len(recent_20) >= 20 else None
        ma60 = recent_60['收盘'].mean() if len(recent_60) >= 60 else None
        
        # 计算RSI (简化版)
        price_changes = hist_data['收盘'].diff().dropna()
        gains = price_changes.where(price_changes > 0, 0)
        losses = -price_changes.where(price_changes < 0, 0)
        
        if len(gains) >= 14:
            avg_gain = gains.rolling(14).mean().iloc[-1]
            avg_loss = losses.rolling(14).mean().iloc[-1]
            rs = avg_gain / avg_loss if avg_loss != 0 else 0
            rsi = 100 - (100 / (1 + rs))
        else:
            rsi = None
        
        return {
            "technical": {
                "ma5": round(ma5, 2) if ma5 else None,
                "ma10": round(ma10, 2) if ma10 else None,
                "ma20": round(ma20, 2) if ma20 else None,
                "ma60": round(ma60, 2) if ma60 else None,
                "rsi": round(rsi, 2) if rsi else None,
                "current_price": float(latest['收盘']),
                "volume_ratio": float(latest['成交量']) / recent_20['成交量'].mean() if len(recent_20) > 0 else None
            },
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "technical": {},
            "error": f"获取技术指标失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }

@router.get("/market/hot_stocks")
async def get_hot_stocks():
    """获取热门股票（使用市场缓存数据）"""
    try:
        from app.services.market_cache import market_cache
        
        # 优先使用缓存数据
        if market_cache.is_cache_valid():
            hot_by_volume = market_cache.get_top_stocks('amount', 20)
            hot_by_gain = market_cache.get_top_stocks('change', 20)
            hot_by_turnover = market_cache.get_top_stocks('turnover', 20)
            
            return {
                "hot_by_volume": hot_by_volume,
                "hot_by_gain": hot_by_gain,
                "hot_by_turnover": hot_by_turnover,
                "from_cache": True,
                "timestamp": datetime.now().isoformat()
            }
        
        # 缓存无效，刷新数据
        await market_cache.refresh_market_data()
        
        hot_by_volume = market_cache.get_top_stocks('amount', 20)
        hot_by_gain = market_cache.get_top_stocks('change', 20)
        hot_by_turnover = market_cache.get_top_stocks('turnover', 20)
        
        return {
            "hot_by_volume": hot_by_volume,
            "hot_by_gain": hot_by_gain,
            "hot_by_turnover": hot_by_turnover,
            "from_cache": False,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"获取热门股票失败: {str(e)}")

@router.get("/stocks/{stock_code}/peers")
async def get_stock_peers(stock_code: str):
    """获取同行业股票对比"""
    try:
        # 这里简化处理，实际应该根据行业分类获取同行业股票
        # 获取实时数据
        realtime_data = await run_in_executor(ak.stock_zh_a_spot_em)
        
        # 随机选择一些股票作为对比（实际应该根据行业筛选）
        peers = realtime_data.sample(10)[
            ['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率']
        ].to_dict('records')
        
        return {
            "peers": peers,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        return {
            "peers": [],
            "error": f"获取同行业股票失败: {str(e)}",
            "timestamp": datetime.now().isoformat()
        }