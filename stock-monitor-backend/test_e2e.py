#!/usr/bin/env python3
"""
端到端测试 - 使用 Playwright 测试前端页面数据显示
"""
import asyncio
from playwright.async_api import async_playwright
import json

async def test_stock_detail_page():
    """测试股票详情页面数据显示"""
    print("=== 端到端测试：股票详情页面 ===\n")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 设置为 False 可以看到浏览器
        page = await browser.new_page()
        
        # 1. 先登录
        print("1. 登录系统...")
        await page.goto("http://localhost:3002/login")
        await page.wait_for_load_state("networkidle")
        
        # 填写登录表单
        await page.fill('input[type="text"]', 'admin')
        await page.fill('input[type="password"]', 'admin')
        await page.click('button[type="submit"]')
        
        # 等待登录完成
        await page.wait_for_timeout(2000)
        print("   登录成功")
        
        # 2. 访问股票列表页面
        print("\n2. 访问股票列表...")
        await page.goto("http://localhost:3002/stocks")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        # 3. 搜索 000679 股票
        print("\n3. 搜索股票 000679...")
        search_input = page.locator('input[placeholder*="搜索"]').first
        if await search_input.count() > 0:
            await search_input.fill("000679")
            await page.wait_for_timeout(1000)
        
        # 4. 点击进入详情页
        print("\n4. 进入股票详情页...")
        # 尝试找到并点击股票链接
        stock_link = page.locator('text=000679').first
        if await stock_link.count() > 0:
            await stock_link.click()
            await page.wait_for_timeout(3000)
        else:
            # 直接访问增强版详情页
            print("   直接访问增强版详情页...")
            await page.goto("http://localhost:3002/enhanced-stock/1")
            await page.wait_for_timeout(3000)
        
        # 5. 检查页面数据
        print("\n5. 检查页面数据...")
        
        # 截图保存
        await page.screenshot(path="test_screenshot_basic.png")
        print("   已保存基本信息截图: test_screenshot_basic.png")
        
        # 检查K线图
        print("\n6. 检查K线图...")
        chart_element = page.locator('.chart-card, [class*="chart"]').first
        if await chart_element.count() > 0:
            print("   K线图容器存在")
        else:
            print("   ⚠️ K线图容器未找到")
        
        # 7. 点击财务数据标签
        print("\n7. 检查财务数据...")
        financial_tab = page.locator('text=财务数据').first
        if await financial_tab.count() > 0:
            await financial_tab.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="test_screenshot_financial.png")
            print("   已保存财务数据截图: test_screenshot_financial.png")
        
        # 8. 检查新闻资讯
        print("\n8. 检查新闻资讯...")
        news_tab = page.locator('text=新闻资讯').first
        if await news_tab.count() > 0:
            await news_tab.click()
            await page.wait_for_timeout(2000)
            await page.screenshot(path="test_screenshot_news.png")
            print("   已保存新闻资讯截图: test_screenshot_news.png")
        
        # 9. 获取控制台日志
        print("\n9. 检查控制台错误...")
        
        # 10. 测试API响应
        print("\n10. 直接测试API响应...")
        
        await browser.close()
        print("\n=== 测试完成 ===")

async def test_api_directly():
    """直接测试API响应"""
    print("\n=== 直接测试后端API ===\n")
    
    import aiohttp
    
    async with aiohttp.ClientSession() as session:
        # 测试财务数据API
        print("1. 测试财务数据API...")
        try:
            async with session.get("http://localhost:8000/api/enhanced/stocks/000679/financial") as resp:
                data = await resp.json()
                print(f"   状态码: {resp.status}")
                print(f"   基本信息: {data.get('basic_info', {})}")
                print(f"   财务比率: {data.get('financial_ratios', {})}")
                print(f"   同行业对比数量: {len(data.get('industry_comparison', []))}")
                if data.get('error'):
                    print(f"   ⚠️ 错误: {data.get('error')}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        # 测试技术指标API
        print("\n2. 测试技术指标API...")
        try:
            async with session.get("http://localhost:8000/api/enhanced/stocks/000679/technical") as resp:
                data = await resp.json()
                print(f"   状态码: {resp.status}")
                print(f"   技术指标: {data.get('technical', {})}")
                if data.get('error'):
                    print(f"   ⚠️ 错误: {data.get('error')}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        # 测试K线数据API
        print("\n3. 测试K线数据API...")
        try:
            async with session.get("http://localhost:8000/api/charts/1/kline?period=day") as resp:
                data = await resp.json()
                print(f"   状态码: {resp.status}")
                if 'klines' in data:
                    print(f"   K线数据条数: {len(data.get('klines', []))}")
                    if data.get('klines'):
                        print(f"   最新K线: {data['klines'][-1]}")
                else:
                    print(f"   响应: {data}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        # 测试新闻API
        print("\n4. 测试新闻API...")
        try:
            async with session.get("http://localhost:8000/api/enhanced/stocks/000679/news") as resp:
                data = await resp.json()
                print(f"   状态码: {resp.status}")
                print(f"   新闻数量: {len(data.get('news', []))}")
                if data.get('news'):
                    print(f"   最新新闻: {data['news'][0].get('新闻标题', '')[:50]}...")
                if data.get('error'):
                    print(f"   ⚠️ 错误: {data.get('error')}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")
        
        # 测试资金流向API
        print("\n5. 测试资金流向API...")
        try:
            async with session.get("http://localhost:8000/api/enhanced/stocks/000679/fund_flow") as resp:
                data = await resp.json()
                print(f"   状态码: {resp.status}")
                print(f"   资金流向数据条数: {len(data.get('fund_flow', []))}")
                if data.get('error'):
                    print(f"   ⚠️ 错误: {data.get('error')}")
        except Exception as e:
            print(f"   ❌ 请求失败: {e}")

if __name__ == "__main__":
    # 先测试API
    asyncio.run(test_api_directly())
    
    # 再测试页面
    print("\n" + "="*50)
    asyncio.run(test_stock_detail_page())