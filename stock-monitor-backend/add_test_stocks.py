import asyncio
import aiomysql
from app.config import get_settings

settings = get_settings()

async def add_test_stocks():
    """添加一些测试股票数据"""
    conn = await aiomysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        charset='utf8mb4'
    )

    stocks = [
        ('000001', '平安银行', 'SZ'),
        ('000002', '万科A', 'SZ'),
        ('000858', '五粮液', 'SZ'),
        ('600000', '浦发银行', 'SH'),
        ('600036', '招商银行', 'SH'),
        ('600519', '贵州茅台', 'SH'),
        ('600887', '伊利股份', 'SH'),
        ('000725', '京东方A', 'SZ'),
        ('002415', '海康威视', 'SZ'),
        ('300059', '东方财富', 'SZ'),
        ('601318', '中国平安', 'SH'),
        ('601857', '中国石油', 'SH'),
        ('601988', '中国银行', 'SH'),
        ('000333', '美的集团', 'SZ'),
        ('002594', '比亚迪', 'SZ'),
    ]

    async with conn.cursor() as cursor:
        for code, name, market in stocks:
            # 检查是否已存在
            await cursor.execute(
                "SELECT id FROM stocks WHERE code = %s",
                (code,)
            )
            if await cursor.fetchone():
                print(f"股票 {code} {name} 已存在，跳过")
                continue

            # 插入新股票
            await cursor.execute(
                "INSERT INTO stocks (code, name, market, full_code) VALUES (%s, %s, %s, %s)",
                (code, name, market, f"{code}.{market}")
            )
            print(f"添加股票: {code} {name}")

        await conn.commit()
        print(f"\n共添加 {len(stocks)} 只股票")

    await conn.ensure_closed()
    print("测试股票数据添加完成!")

if __name__ == "__main__":
    asyncio.run(add_test_stocks())
