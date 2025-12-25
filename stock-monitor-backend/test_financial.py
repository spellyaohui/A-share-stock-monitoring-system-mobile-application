#!/usr/bin/env python3
import akshare as ak
import pandas as pd

def test_financial_apis():
    print("=== 测试财务数据接口 ===")
    
    # 测试不同的财务数据接口
    stock_code = "000001"
    
    # 1. 测试财务摘要
    try:
        print("1. 测试财务摘要接口...")
        data = ak.stock_financial_abstract(stock=stock_code)
        print(f"财务摘要数据形状: {data.shape}")
        print("财务摘要数据:")
        print(data.head())
        print()
    except Exception as e:
        print(f"财务摘要接口失败: {e}")
        print()
    
    # 2. 测试财务指标
    try:
        print("2. 测试财务指标接口...")
        data = ak.stock_financial_analysis_indicator(stock=stock_code)
        print(f"财务指标数据形状: {data.shape}")
        print("财务指标数据:")
        print(data.head())
        print()
    except Exception as e:
        print(f"财务指标接口失败: {e}")
        print()
    
    # 3. 测试业绩预告
    try:
        print("3. 测试业绩预告接口...")
        data = ak.stock_yjbb_em(date="2024-12-31")
        filtered_data = data[data['股票代码'] == stock_code]
        print(f"业绩预告数据: {len(filtered_data)} 条")
        if len(filtered_data) > 0:
            print(filtered_data.head())
        print()
    except Exception as e:
        print(f"业绩预告接口失败: {e}")
        print()
    
    # 4. 测试主要财务指标
    try:
        print("4. 测试主要财务指标...")
        data = ak.stock_zh_a_hist_min_em(symbol=stock_code, start_date="2024-12-25 09:30:00", end_date="2024-12-25 15:00:00", period="1", adjust="")
        print(f"分钟数据形状: {data.shape}")
        print("分钟数据:")
        print(data.tail(3))
        print()
    except Exception as e:
        print(f"分钟数据接口失败: {e}")
        print()

if __name__ == "__main__":
    test_financial_apis()