#!/usr/bin/env python3
"""
全面测试财务数据相关接口
"""
import akshare as ak
import pandas as pd

def test_comprehensive_financial_data():
    print("=== 全面财务数据测试 ===")
    
    stock_code = "000679"  # 大连友谊
    
    # 1. 个股基本信息（包含一些财务指标）
    print("1. 个股基本信息")
    try:
        basic_info = ak.stock_individual_info_em(symbol=stock_code)
        print("基本信息:")
        for _, row in basic_info.iterrows():
            print(f"  {row['item']}: {row['value']}")
        print()
    except Exception as e:
        print(f"获取基本信息失败: {e}\n")
    
    # 2. 实时行情中的财务比率
    print("2. 实时行情中的财务比率")
    try:
        realtime_data = ak.stock_zh_a_spot_em()
        stock_data = realtime_data[realtime_data['代码'] == stock_code]
        if not stock_data.empty:
            stock_info = stock_data.iloc[0]
            print("财务比率:")
            print(f"  市盈率(动态): {stock_info['市盈率-动态']}")
            print(f"  市净率: {stock_info['市净率']}")
            print(f"  总市值: {stock_info['总市值']:,.0f}")
            print(f"  流通市值: {stock_info['流通市值']:,.0f}")
            print(f"  换手率: {stock_info['换手率']}%")
        print()
    except Exception as e:
        print(f"获取实时财务比率失败: {e}\n")
    
    # 3. 测试可能的财务报表接口
    print("3. 测试财务报表接口")
    
    # 尝试不同的财务报表接口
    financial_apis = [
        ("资产负债表", lambda: ak.stock_balance_sheet_by_report_em(symbol=stock_code)),
        ("利润表", lambda: ak.stock_profit_sheet_by_report_em(symbol=stock_code)),
        ("现金流量表", lambda: ak.stock_cash_flow_sheet_by_report_em(symbol=stock_code)),
        ("主要财务指标", lambda: ak.stock_financial_abstract_em(symbol=stock_code)),
        ("财务分析", lambda: ak.stock_financial_analysis_indicator(symbol=stock_code)),
    ]
    
    for name, api_func in financial_apis:
        try:
            print(f"测试 {name}...")
            data = api_func()
            if not data.empty:
                print(f"  数据形状: {data.shape}")
                print(f"  列名: {list(data.columns)}")
                print(f"  最新数据:")
                print(data.head(1))
            else:
                print(f"  {name} 数据为空")
            print()
        except Exception as e:
            print(f"  {name} 接口失败: {e}\n")
    
    # 4. 测试行业财务对比
    print("4. 行业财务对比")
    try:
        # 获取行业板块信息
        industry_data = ak.stock_board_industry_name_em()
        print(f"行业板块数量: {len(industry_data)}")
        
        # 尝试获取商业百货行业的股票
        retail_stocks = ak.stock_board_industry_cons_em(symbol="商业百货")
        print(f"商业百货行业股票数量: {len(retail_stocks)}")
        print("同行业股票前5只:")
        print(retail_stocks[['代码', '名称', '最新价', '涨跌幅', '市盈率-动态', '市净率']].head())
        print()
    except Exception as e:
        print(f"获取行业对比失败: {e}\n")
    
    # 5. 测试股东信息
    print("5. 股东信息")
    try:
        # 十大股东
        shareholders = ak.stock_zh_a_gdhs(symbol=stock_code)
        print("十大股东信息:")
        print(shareholders.head())
        print()
    except Exception as e:
        print(f"获取股东信息失败: {e}\n")
    
    # 6. 测试分红配股信息
    print("6. 分红配股信息")
    try:
        dividend_data = ak.stock_zh_a_fhpg(symbol=stock_code)
        print("分红配股信息:")
        print(dividend_data.head())
        print()
    except Exception as e:
        print(f"获取分红配股信息失败: {e}\n")

if __name__ == "__main__":
    test_comprehensive_financial_data()