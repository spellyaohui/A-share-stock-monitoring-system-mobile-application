"""
使用 Playwright 测试市场概况页面的标签页和龙虎榜
"""
import asyncio
from playwright.async_api import async_playwright
import time

async def test_market_overview():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # 显示浏览器
        page = await browser.new_page()
        
        print("=" * 60)
        print("开始测试市场概况页面")
        print("=" * 60)
        
        # 1. 先登录
        print("\n[1] 登录系统...")
        await page.goto("http://localhost:3003/login")
        await page.wait_for_timeout(2000)
        
        # 使用更精确的选择器
        await page.locator('input').first.fill('admin')
        await page.locator('input[type="password"]').fill('admin')
        await page.locator('button.el-button--primary').click()
        await page.wait_for_timeout(2000)
        
        print("✓ 登录成功")
        
        # 2. 进入市场概况页面
        print("\n[2] 进入市场概况页面...")
        await page.goto("http://localhost:3003/market")
        await page.wait_for_timeout(3000)
        
        # 截图当前页面
        await page.screenshot(path="test_screenshots/market_overview_initial.png")
        print("✓ 已截图: market_overview_initial.png")
        
        # 3. 测试标签页切换 - 热门股票
        print("\n[3] 测试标签页 - 热门股票...")
        hot_tab = page.locator('.el-tabs__item:has-text("热门股票")')
        await hot_tab.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="test_screenshots/tab_hot_stocks.png")
        print("✓ 已截图: tab_hot_stocks.png")
        
        # 检查标签页位置
        hot_tab_box = await hot_tab.bounding_box()
        print(f"  热门股票标签位置: x={hot_tab_box['x']}, y={hot_tab_box['y']}, width={hot_tab_box['width']}")
        
        # 4. 测试标签页切换 - 行业板块
        print("\n[4] 测试标签页 - 行业板块...")
        sector_tab = page.locator('.el-tabs__item:has-text("行业板块")')
        await sector_tab.click()
        await page.wait_for_timeout(1000)
        await page.screenshot(path="test_screenshots/tab_sectors.png")
        print("✓ 已截图: tab_sectors.png")
        
        sector_tab_box = await sector_tab.bounding_box()
        print(f"  行业板块标签位置: x={sector_tab_box['x']}, y={sector_tab_box['y']}, width={sector_tab_box['width']}")
        
        # 5. 测试标签页切换 - 龙虎榜
        print("\n[5] 测试标签页 - 龙虎榜...")
        lhb_tab = page.locator('.el-tabs__item:has-text("龙虎榜")')
        await lhb_tab.click()
        await page.wait_for_timeout(3000)  # 等待数据加载
        await page.screenshot(path="test_screenshots/tab_lhb.png")
        print("✓ 已截图: tab_lhb.png")
        
        lhb_tab_box = await lhb_tab.bounding_box()
        print(f"  龙虎榜标签位置: x={lhb_tab_box['x']}, y={lhb_tab_box['y']}, width={lhb_tab_box['width']}")
        
        # 6. 检查龙虎榜数据
        print("\n[6] 检查龙虎榜数据...")
        
        # 检查是否有表格数据
        table_rows = page.locator('.lhb-card .el-table__body-wrapper tr')
        row_count = await table_rows.count()
        print(f"  龙虎榜表格行数: {row_count}")
        
        if row_count > 0:
            # 获取第一行数据
            first_row = table_rows.first
            cells = first_row.locator('td')
            cell_count = await cells.count()
            print(f"  第一行列数: {cell_count}")
            
            # 打印前几行数据
            print("\n  龙虎榜数据预览:")
            for i in range(min(5, row_count)):
                row = table_rows.nth(i)
                row_text = await row.inner_text()
                print(f"    行{i+1}: {row_text[:100]}...")
        else:
            # 检查是否有空状态
            empty = page.locator('.el-empty')
            if await empty.count() > 0:
                print("  ⚠ 龙虎榜显示空状态")
            else:
                print("  ⚠ 龙虎榜无数据且无空状态提示")
        
        # 7. 测试标签页动画 - 快速切换
        print("\n[7] 测试标签页快速切换动画...")
        for i in range(3):
            await page.locator('.el-tabs__item:has-text("热门股票")').click()
            await page.wait_for_timeout(300)
            await page.locator('.el-tabs__item:has-text("行业板块")').click()
            await page.wait_for_timeout(300)
            await page.locator('.el-tabs__item:has-text("龙虎榜")').click()
            await page.wait_for_timeout(300)
        
        await page.screenshot(path="test_screenshots/tab_animation_test.png")
        print("✓ 已截图: tab_animation_test.png")
        
        # 8. 检查活动标签的样式
        print("\n[8] 检查活动标签样式...")
        active_tab = page.locator('.el-tabs__item.is-active')
        active_tab_text = await active_tab.inner_text()
        print(f"  当前活动标签: {active_tab_text}")
        
        # 获取活动标签的计算样式
        active_styles = await active_tab.evaluate('''el => {
            const styles = window.getComputedStyle(el);
            return {
                background: styles.background,
                color: styles.color,
                borderRadius: styles.borderRadius,
                padding: styles.padding
            };
        }''')
        print(f"  活动标签样式: {active_styles}")
        
        # 9. 检查是否有下划线动画条
        print("\n[9] 检查下划线动画条...")
        active_bar = page.locator('.el-tabs__active-bar')
        if await active_bar.count() > 0:
            bar_styles = await active_bar.evaluate('''el => {
                const styles = window.getComputedStyle(el);
                return {
                    display: styles.display,
                    width: styles.width,
                    transform: styles.transform
                };
            }''')
            print(f"  下划线动画条样式: {bar_styles}")
        else:
            print("  ✓ 下划线动画条已隐藏")
        
        print("\n" + "=" * 60)
        print("测试完成！请查看 test_screenshots 目录下的截图")
        print("=" * 60)
        
        # 保持浏览器打开一会儿以便观察
        await page.wait_for_timeout(5000)
        
        await browser.close()

if __name__ == "__main__":
    import os
    os.makedirs("test_screenshots", exist_ok=True)
    asyncio.run(test_market_overview())
