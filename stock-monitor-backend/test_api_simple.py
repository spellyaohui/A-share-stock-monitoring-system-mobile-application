#!/usr/bin/env python3
"""
简单API测试 - 使用 requests 同步测试
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_apis():
    print("=== 后端API测试 ===\n")
    
    # 1. 测试财务数据API
    print("1. 测试财务数据API (000679)...")
    try:
        resp = requests.get(f"{BASE_URL}/api/enhanced/stocks/000679/financial", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   基本信息: {data.get('basic_info', {})}")
            print(f"   财务比率: {data.get('financial_ratios', {})}")
            print(f"   同行业对比数量: {len(data.get('industry_comparison', []))}")
            if data.get('error'):
                print(f"   ⚠️ 错误: {data.get('error')}")
        else:
            print(f"   响应: {resp.text[:500]}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 2. 测试技术指标API
    print("\n2. 测试技术指标API (000679)...")
    try:
        resp = requests.get(f"{BASE_URL}/api/enhanced/stocks/000679/technical", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   技术指标: {data.get('technical', {})}")
            if data.get('error'):
                print(f"   ⚠️ 错误: {data.get('error')}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 3. 测试K线数据API
    print("\n3. 测试K线数据API...")
    try:
        resp = requests.get(f"{BASE_URL}/api/charts/1/kline?period=day", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            if 'klines' in data:
                print(f"   K线数据条数: {len(data.get('klines', []))}")
                if data.get('klines'):
                    print(f"   最新K线: {data['klines'][-1]}")
            else:
                print(f"   响应: {data}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 4. 测试新闻API
    print("\n4. 测试新闻API (000679)...")
    try:
        resp = requests.get(f"{BASE_URL}/api/enhanced/stocks/000679/news", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   新闻数量: {len(data.get('news', []))}")
            if data.get('news'):
                print(f"   最新新闻: {data['news'][0].get('新闻标题', '')[:50]}...")
            if data.get('error'):
                print(f"   ⚠️ 错误: {data.get('error')}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 5. 测试资金流向API
    print("\n5. 测试资金流向API (000679)...")
    try:
        resp = requests.get(f"{BASE_URL}/api/enhanced/stocks/000679/fund_flow", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   资金流向数据条数: {len(data.get('fund_flow', []))}")
            if data.get('error'):
                print(f"   ⚠️ 错误: {data.get('error')}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")
    
    # 6. 测试市场概况API
    print("\n6. 测试市场概况API...")
    try:
        resp = requests.get(f"{BASE_URL}/api/enhanced/market/overview", timeout=60)
        print(f"   状态码: {resp.status_code}")
        if resp.status_code == 200:
            data = resp.json()
            print(f"   市场统计: {data.get('market_stats', {})}")
    except Exception as e:
        print(f"   ❌ 请求失败: {e}")

    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    test_apis()