#!/usr/bin/env python3
import akshare as ak
import pandas as pd

def test_alternative_financial_apis():
    print("=== 测试替代财务数据接口 ===")
    
    stock_code = "000679"
    
    # 1. 测试股票基本信息
    try:
        print("1. 测试股票基本信息...")
        data = ak.stock_individual_info_em(symbol=stock_code)
        print(f"基本信息数据形状: {data.shape}")
        print("基本信息:")
        print(data)
        print()
    except Exception as e:
        print(f"基本信息接口失败: {e}")
        print()
    
    # 2. 测试股票历史数据（包含一些财务指标）
    try:
        print("2. 测试历史数据...")
        data = ak.stock_zh_a_hist(symbol=stock_code, period="daily", start_date="20241201", end_date="20241225", adjust="")
        print(f"历史数据形状: {data.shape}")
        print("历史数据列:")
        print(list(data.columns))
        print("最新数据:")
        print(data.tail(1))
        print()
    except Exception as e:
        print(f"历史数据接口失败: {e}")
        print()
    
    # 3. 测试东方财富个股信息
    try:
        print("3. 测试东方财富个股信息...")
        data = ak.stock_individual_info_em(symbol=stock_code)
        print(f"个股信息数据: {type(data)}")
        print("个股信息:")
        print(data)
        print()
    except Exception as e:
        print(f"个股信息接口失败: {e}")
        print()
    
    # 4. 测试股票实时数据（包含一些财务比率）
    try:
        print("4. 测试实时数据中的财务信息...")
        data = ak.stock_zh_a_spot_em()
        stock_data = data[data['代码'] == stock_code]
        if not stock_data.empty:
            print("实时数据中的财务相关字段:")
            relevant_cols = ['代码', '名称', '最新价', '市盈率-动态', '市净率', '总市值', '流通市值', '换手率']
            print(stock_data[relevant_cols].iloc[0])
        print()
    except Exception as e:
        print(f"实时数据接口失败: {e}")
        print()
    
    # 5. 测试概念板块（可能包含行业信息）
    try:
        print("5. 测试概念板块信息...")
        # 获取股票所属概念
        data = ak.stock_board_concept_cons_em(symbol="商业百货")
        if stock_code in data['代码'].values:
            print(f"{stock_code} 属于商业百货概念")
        print()
    except Exception as e:
        print(f"概念板块接口失败: {e}")
        print()

if __name__ == "__main__":
    test_alternative_financial_apis()