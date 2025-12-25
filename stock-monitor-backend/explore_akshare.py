#!/usr/bin/env python3
"""
探索AkShare提供的丰富数据接口
"""
import akshare as ak
import pandas as pd

def explore_stock_data():
    print("=== AkShare 股票数据探索 ===\n")
    
    # 1. 基础股票信息
    print("1. 股票基础信息")
    try:
        stock_info = ak.stock_info_a_code_name()
        print(f"A股股票总数: {len(stock_info)}")
        print("前5只股票:")
        print(stock_info.head())
        print()
    except Exception as e:
        print(f"获取股票基础信息失败: {e}\n")
    
    # 2. 实时行情数据
    print("2. 实时行情数据")
    try:
        realtime_data = ak.stock_zh_a_spot_em()
        print(f"实时行情数据字段: {list(realtime_data.columns)}")
        print("前3只股票实时数据:")
        print(realtime_data.head(3))
        print()
    except Exception as e:
        print(f"获取实时行情失败: {e}\n")
    
    # 3. 历史K线数据
    print("3. 历史K线数据")
    try:
        kline_data = ak.stock_zh_a_hist(symbol="000001", period="daily", start_date="20241201", end_date="20241225", adjust="")
        print(f"K线数据字段: {list(kline_data.columns)}")
        print("平安银行最近5天K线:")
        print(kline_data.tail())
        print()
    except Exception as e:
        print(f"获取K线数据失败: {e}\n")
    
    # 4. 财务数据
    print("4. 财务数据")
    try:
        # 资产负债表
        balance_sheet = ak.stock_balance_sheet_by_report_em(symbol="000001")
        print(f"资产负债表字段: {list(balance_sheet.columns)}")
        print("平安银行资产负债表(最新):")
        print(balance_sheet.head(2))
        print()
    except Exception as e:
        print(f"获取财务数据失败: {e}\n")
    
    # 5. 技术指标
    print("5. 技术指标")
    try:
        # MACD指标
        macd_data = ak.stock_zh_a_hist_pre_min_em(symbol="000001", start_date="2024-12-20 09:30:00", end_date="2024-12-25 15:00:00")
        print(f"分钟级数据字段: {list(macd_data.columns)}")
        print("平安银行分钟级数据样例:")
        print(macd_data.tail(3))
        print()
    except Exception as e:
        print(f"获取技术指标失败: {e}\n")
    
    # 6. 市场概况
    print("6. 市场概况")
    try:
        # 涨跌停统计
        limit_up_down = ak.stock_zh_a_st_em()
        print(f"涨跌停数据字段: {list(limit_up_down.columns)}")
        print("涨跌停统计:")
        print(limit_up_down.head())
        print()
    except Exception as e:
        print(f"获取市场概况失败: {e}\n")
    
    # 7. 资金流向
    print("7. 资金流向")
    try:
        money_flow = ak.stock_individual_fund_flow(stock="000001", market="sz")
        print(f"资金流向字段: {list(money_flow.columns)}")
        print("平安银行资金流向:")
        print(money_flow.head())
        print()
    except Exception as e:
        print(f"获取资金流向失败: {e}\n")
    
    # 8. 龙虎榜数据
    print("8. 龙虎榜数据")
    try:
        lhb_data = ak.stock_lhb_detail_em(start_date="20241220", end_date="20241225")
        print(f"龙虎榜字段: {list(lhb_data.columns)}")
        print("最近龙虎榜数据:")
        print(lhb_data.head(3))
        print()
    except Exception as e:
        print(f"获取龙虎榜数据失败: {e}\n")
    
    # 9. 新闻资讯
    print("9. 新闻资讯")
    try:
        news_data = ak.stock_news_em(symbol="000001")
        print(f"新闻数据字段: {list(news_data.columns)}")
        print("平安银行最新新闻:")
        print(news_data.head(3))
        print()
    except Exception as e:
        print(f"获取新闻资讯失败: {e}\n")
    
    # 10. 行业板块
    print("10. 行业板块")
    try:
        industry_data = ak.stock_board_industry_name_em()
        print(f"行业板块数量: {len(industry_data)}")
        print("行业板块列表(前10个):")
        print(industry_data.head(10))
        print()
    except Exception as e:
        print(f"获取行业板块失败: {e}\n")

if __name__ == "__main__":
    explore_stock_data()