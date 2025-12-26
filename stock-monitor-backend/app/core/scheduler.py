from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime

scheduler = AsyncIOScheduler()
memory_cache = {}


async def refresh_market_cache():
    """刷新全市场数据缓存"""
    print(f"[{datetime.now()}] 开始刷新市场数据缓存...")
    from app.services.market_cache import market_cache
    success = await market_cache.refresh_market_data()
    if success:
        print(f"[{datetime.now()}] 市场数据缓存刷新完成")
    else:
        print(f"[{datetime.now()}] 市场数据缓存刷新失败")


async def update_stock_data():
    """更新股票数据（已废弃，使用 refresh_market_cache 代替）"""
    print(f"[{datetime.now()}] 开始更新股票数据...")
    from app.database import AsyncSessionLocal
    from app.services.data_fetcher import update_all_stock_data
    async with AsyncSessionLocal() as db:
        await update_all_stock_data(db)
    print(f"[{datetime.now()}] 股票数据更新完成")


async def check_monitor_conditions():
    """检查监测条件"""
    print(f"[{datetime.now()}] 开始检查监测条件...")
    from app.database import AsyncSessionLocal
    from app.services.monitor_service import check_and_notify
    async with AsyncSessionLocal() as db:
        await check_and_notify(db)
    print(f"[{datetime.now()}] 监测条件检查完成")


def start_scheduler():
    # 1. 市场数据缓存刷新任务
    # 开盘前刷新一次（9:00）
    scheduler.add_job(
        refresh_market_cache,
        CronTrigger(hour=9, minute=0, day_of_week='mon-fri'),
        id='refresh_market_morning',
        replace_existing=True
    )
    
    # 盘中每 10 分钟刷新一次（由于监测个股有专门的高效 API，市场数据刷新间隔调长）
    scheduler.add_job(
        refresh_market_cache,
        IntervalTrigger(minutes=10),
        id='refresh_market_interval',
        replace_existing=True
    )
    
    # 收盘后刷新一次（15:30）
    scheduler.add_job(
        refresh_market_cache,
        CronTrigger(hour=15, minute=30, day_of_week='mon-fri'),
        id='refresh_market_close',
        replace_existing=True
    )
    
    # 2. 监测条件检查任务（每2分钟，由于监测个股有专门的高效 API，间隔可以调长）
    scheduler.add_job(
        check_monitor_conditions,
        IntervalTrigger(minutes=2),
        id='check_monitors',
        replace_existing=True
    )
    
    # 3. 股票数据更新任务（每 5 分钟，已被市场缓存替代，保留用于兼容）
    # scheduler.add_job(
    #     update_stock_data,
    #     IntervalTrigger(minutes=5),
    #     id='update_stocks',
    #     replace_existing=True
    # )
    
    scheduler.start()
    print("定时任务调度器已启动")
    
    # 启动时立即刷新一次市场数据
    import asyncio
    asyncio.create_task(refresh_market_cache())


def shutdown_scheduler():
    scheduler.shutdown()
    print("定时任务调度器已关闭")
