#!/usr/bin/env python3
"""
AkShare 集成测试脚本
用于验证 AkShare 数据获取功能
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.akshare_api import akshare_service
from app.services.data_fetcher import data_fetcher


async def test_akshare_basic():
    """测试 AkShare 基本功能"""
    print("=== 测试 AkShare 基本功能 ===")
    
    # 测试股票搜索
    print("\n1. 测试股票搜索")
    try:
        results = await akshare_service.search_stock("平安", limit=5)
        print(f"搜索 '平安' 结果: {len(results)} 条")
        for stock in results[:3]:
            print(f"  - {stock['code']} {stock['name']}")
    except Exception as e:
        print(f"搜索失败: {e}")
    
    # 测试实时行情
    print("\n2. 测试实时行情")
    try:
        quote = await akshare_service.get_realtime_quote("000001")
        if quote:
            print(f"平安银行 (000001) 实时行情:")
            print(f"  - 当前价: {quote.get('price', 'N/A')}")
            print(f"  - 涨跌幅: {quote.get('change_percent', 'N/A')}%")
            print(f"  - 成交量: {quote.get('volume', 'N/A')}")
        else:
            print("获取实时行情失败")
    except Exception as e:
        print(f"获取实时行情失败: {e}")
    
    # 测试K线数据
    print("\n3. 测试K线数据")
    try:
        klines = await akshare_service.get_kline_data("000001", "daily", limit=5)
        print(f"平安银行 (000001) 最近5日K线:")
        for kline in klines[-3:]:  # 显示最近3天
            print(f"  - {kline['date']}: 开盘{kline['open']}, 收盘{kline['close']}, 涨跌幅{kline['change_percent']}%")
    except Exception as e:
        print(f"获取K线数据失败: {e}")


async def test_data_fetcher():
    """测试统一数据获取服务"""
    print("\n=== 测试统一数据获取服务 ===")
    
    # 测试实时行情
    print("\n1. 测试实时行情获取")
    try:
        quote = await data_fetcher.get_realtime_quote("000001")
        if quote:
            print(f"平安银行 (000001) 行情:")
            print(f"  - 当前价: {quote.get('price', 'N/A')}")
            print(f"  - 涨跌幅: {quote.get('change_percent', 'N/A')}%")
        else:
            print("获取行情失败")
    except Exception as e:
        print(f"获取行情失败: {e}")
    
    # 测试批量行情
    print("\n2. 测试批量行情获取")
    try:
        codes = ["000001", "000002", "600000"]
        quotes = await data_fetcher.get_batch_quotes(codes)
        print(f"批量获取 {len(codes)} 只股票行情，成功 {len(quotes)} 只:")
        for code, quote in quotes.items():
            print(f"  - {code} {quote.get('name', 'N/A')}: {quote.get('price', 'N/A')}")
    except Exception as e:
        print(f"批量获取行情失败: {e}")
    
    # 测试搜索功能
    print("\n3. 测试股票搜索")
    try:
        results = await data_fetcher.search_stock("银行", limit=5)
        print(f"搜索 '银行' 结果: {len(results)} 条")
        for stock in results[:3]:
            print(f"  - {stock['code']} {stock['name']}")
    except Exception as e:
        print(f"搜索失败: {e}")


async def test_market_overview():
    """测试市场概览"""
    print("\n=== 测试市场概览 ===")
    try:
        overview = await data_fetcher.get_market_overview()
        print(f"市场状态: {overview.get('market_status', 'N/A')}")
        print(f"更新时间: {overview.get('update_time', 'N/A')}")
        
        indices = overview.get('indices', {})
        print(f"主要指数行情 ({len(indices)} 个):")
        for code, quote in indices.items():
            name = quote.get('name', code)
            price = quote.get('price', 'N/A')
            change_pct = quote.get('change_percent', 'N/A')
            print(f"  - {name} ({code}): {price} ({change_pct}%)")
    except Exception as e:
        print(f"获取市场概览失败: {e}")


async def main():
    """主测试函数"""
    print("开始 AkShare 集成测试...")
    
    try:
        # 测试 AkShare 基本功能
        await test_akshare_basic()
        
        # 测试统一数据获取服务
        await test_data_fetcher()
        
        # 测试市场概览
        await test_market_overview()
        
        print("\n=== 测试完成 ===")
        
    except KeyboardInterrupt:
        print("\n测试被用户中断")
    except Exception as e:
        print(f"\n测试过程中发生错误: {e}")
    finally:
        # 清理资源
        try:
            await data_fetcher.close()
        except:
            pass


if __name__ == "__main__":
    # 运行测试
    asyncio.run(main())