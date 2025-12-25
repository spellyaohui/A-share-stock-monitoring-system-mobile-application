#!/usr/bin/env python3
"""
调试监测创建问题
"""
import asyncio
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.data_fetcher import data_fetcher
from app.services.akshare_api import akshare_service


async def test_stock_data():
    """测试股票数据获取"""
    stock_code = "000672"
    
    print(f"=== 测试股票 {stock_code} 数据获取 ===")
    
    # 测试实时行情
    print("\n1. 测试实时行情获取")
    try:
        quote = await data_fetcher.get_realtime_quote(stock_code)
        print(f"实时行情结果: {quote}")
        if quote:
            print(f"  - 股票名称: {quote.get('name', 'N/A')}")
            print(f"  - 当前价格: {quote.get('price', 'N/A')}")
        else:
            print("  - 获取失败")
    except Exception as e:
        print(f"  - 错误: {e}")
    
    # 测试AkShare搜索
    print("\n2. 测试AkShare搜索")
    try:
        results = await akshare_service.search_stock(stock_code, limit=1)
        print(f"AkShare搜索结果: {results}")
        if results:
            result = results[0]
            print(f"  - 股票代码: {result.get('code', 'N/A')}")
            print(f"  - 股票名称: {result.get('name', 'N/A')}")
            print(f"  - 市场: {result.get('market', 'N/A')}")
        else:
            print("  - 搜索无结果")
    except Exception as e:
        print(f"  - 错误: {e}")
    
    # 测试AkShare实时行情
    print("\n3. 测试AkShare实时行情")
    try:
        quote = await akshare_service.get_realtime_quote(stock_code)
        print(f"AkShare实时行情结果: {quote}")
        if quote:
            print(f"  - 股票名称: {quote.get('name', 'N/A')}")
            print(f"  - 当前价格: {quote.get('price', 'N/A')}")
        else:
            print("  - 获取失败")
    except Exception as e:
        print(f"  - 错误: {e}")


async def main():
    """主函数"""
    try:
        await test_stock_data()
    except Exception as e:
        print(f"测试过程中发生错误: {e}")
    finally:
        # 清理资源
        try:
            await data_fetcher.close()
        except:
            pass


if __name__ == "__main__":
    asyncio.run(main())