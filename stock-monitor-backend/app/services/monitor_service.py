from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlalchemy.orm import selectinload
from typing import List, Optional
from datetime import datetime
from app.models.monitor import Monitor, Notification
from app.models.stock import Stock
from app.schemas.stock import MonitorCreate, MonitorUpdate
from app.services.data_fetcher import data_fetcher
from app.core.logging import get_logger

logger = get_logger(__name__)

async def get_user_monitors(db: AsyncSession, user_id: int) -> List[Monitor]:
    result = await db.execute(
        select(Monitor)
        .options(selectinload(Monitor.stock))
        .where(Monitor.user_id == user_id)
        .order_by(Monitor.created_at.desc())
    )
    return result.scalars().all()

async def get_user_monitors_with_realtime(db: AsyncSession, user_id: int) -> List[dict]:
    """
    获取用户监测列表及实时行情（并发优化版本）
    
    优化策略：
    1. 并发获取所有股票的实时行情，而非串行
    2. 使用 asyncio.gather 并发执行，大幅提升响应速度
    3. 限制并发数避免过载
    """
    import asyncio
    
    monitors = await get_user_monitors(db, user_id)
    
    if not monitors:
        return []
    
    # 收集所有需要获取行情的股票代码
    stock_codes = [m.stock.code for m in monitors if m.stock]
    
    # 并发获取所有股票的实时行情（限制并发数为10）
    semaphore = asyncio.Semaphore(10)
    
    async def fetch_quote(code: str):
        async with semaphore:
            try:
                return code, await data_fetcher.get_realtime_quote_for_monitor(code)
            except Exception as e:
                logger.warning(f"获取行情失败: {code}, 错误: {e}")
                return code, {}
    
    # 并发执行所有请求
    quote_results = await asyncio.gather(*[fetch_quote(code) for code in stock_codes])
    
    # 构建代码到行情的映射
    quotes_map = {code: quote for code, quote in quote_results}
    
    # 组装结果
    result = []
    for monitor in monitors:
        realtime = quotes_map.get(monitor.stock.code, {}) if monitor.stock else {}
        monitor_dict = {
            "id": monitor.id,
            "stock_id": monitor.stock_id,
            "price_min": float(monitor.price_min) if monitor.price_min else None,
            "price_max": float(monitor.price_max) if monitor.price_max else None,
            "rise_threshold": float(monitor.rise_threshold) if monitor.rise_threshold else None,
            "fall_threshold": float(monitor.fall_threshold) if monitor.fall_threshold else None,
            "is_active": monitor.is_active,
            "created_at": monitor.created_at,
            "stock": {
                "id": monitor.stock.id,
                "code": monitor.stock.code,
                "name": monitor.stock.name
            } if monitor.stock else None,
            # 实时行情数据
            "current_price": realtime.get("price"),
            "price": realtime.get("price"),
            "change": realtime.get("change"),
            "change_percent": realtime.get("change_percent"),
            "open": realtime.get("open"),
            "high": realtime.get("high"),
            "low": realtime.get("low"),
            "pre_close": realtime.get("pre_close"),
            "volume": realtime.get("volume"),
            "amount": realtime.get("amount"),
            "turnover_rate": realtime.get("turnover_rate"),
            "volume_ratio": realtime.get("volume_ratio"),
            "limit_up": realtime.get("limit_up"),
            "limit_down": realtime.get("limit_down"),
        }
        result.append(monitor_dict)
    return result

async def create_monitor(db: AsyncSession, user_id: int, data: MonitorCreate) -> Monitor:
    """创建股票监测"""
    stock_id = data.stock_id
    stock_code = str(stock_id).zfill(6)  # 将ID转换为6位股票代码
    
    logger.info(f"创建监测: 用户ID={user_id}, 股票ID={stock_id}, 股票代码={stock_code}")
    
    # 首先尝试按ID查找股票
    result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = result.scalar_one_or_none()
    
    # 如果按ID找不到，尝试按代码查找
    if not stock:
        result = await db.execute(select(Stock).where(Stock.code == stock_code))
        stock = result.scalar_one_or_none()
    
    # 如果数据库中没有，尝试从在线数据源获取并创建
    if not stock:
        logger.info(f"数据库中未找到股票 {stock_code}，尝试从在线数据源获取")
        try:
            # 使用统一数据获取服务获取实时行情验证股票是否存在
            quote = await data_fetcher.get_realtime_quote(stock_code)
            logger.info(f"在线获取股票 {stock_code} 行情结果: {quote is not None}")
            
            if quote and quote.get('name'):
                # 股票存在，创建股票记录
                market = 'SH' if stock_code.startswith(('6', '9')) else 'SZ'
                
                stock = Stock(
                    id=stock_id,
                    code=stock_code,
                    name=quote.get('name', ''),
                    market=market,
                    full_code=f"{stock_code}.{market}"
                )
                db.add(stock)
                await db.flush()
                logger.info(f"成功创建股票记录: {stock_code} - {quote.get('name')}")
            else:
                logger.error(f"无法获取股票 {stock_code} 的行情数据")
                raise ValueError(f"股票代码 {stock_code} 不存在，请检查代码是否正确")
                    
        except ValueError:
            raise  # 重新抛出ValueError
        except Exception as e:
            logger.error(f"获取股票信息失败: {stock_code}, 错误: {str(e)}")
            raise ValueError(f"获取股票信息失败: {str(e)}")

    # 检查是否已存在监测
    exist = await db.execute(
        select(Monitor).where(
            and_(Monitor.user_id == user_id, Monitor.stock_id == stock_id)
        )
    )
    if exist.scalar_one_or_none():
        raise ValueError("该股票已在监测列表中")

    monitor = Monitor(**data.model_dump(), user_id=user_id)
    db.add(monitor)
    await db.commit()
    await db.refresh(monitor)
    logger.info(f"成功创建监测: 股票={stock_code}, 监测ID={monitor.id}")
    return monitor

async def update_monitor(db: AsyncSession, user_id: int, monitor_id: int, data: MonitorUpdate) -> Monitor:
    result = await db.execute(
        select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == user_id)
        )
    )
    monitor = result.scalar_one_or_none()

    if not monitor:
        raise ValueError("监测配置不存在")

    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(monitor, key, value)

    await db.commit()
    await db.refresh(monitor)
    return monitor

async def delete_monitor(db: AsyncSession, user_id: int, monitor_id: int) -> None:
    result = await db.execute(
        select(Monitor).where(
            and_(Monitor.id == monitor_id, Monitor.user_id == user_id)
        )
    )
    monitor = result.scalar_one_or_none()

    if not monitor:
        raise ValueError("监测配置不存在")

    await db.delete(monitor)
    await db.commit()

async def create_and_send_notification(
    db: AsyncSession,
    user_id: int,
    stock_id: int,
    monitor_id: int,
    notify_type: str,
    notify_value: float,
    current_data: dict
):
    stock_result = await db.execute(select(Stock).where(Stock.id == stock_id))
    stock = stock_result.scalar_one_or_none()

    type_names = {
        'price_min': '价格下限',
        'price_max': '价格上限',
        'rise': '涨幅',
        'fall': '跌幅'
    }

    content = f"""股票预警通知
股票: {stock.name} ({stock.code})
类型: {type_names.get(notify_type, notify_type)}
当前价格: {current_data.get('price', 0):.2f}
"""
    if notify_type in ['rise', 'fall']:
        content += f"涨跌幅: {notify_value:.2f}%\n"
    else:
        content += f"触发值: {notify_value:.2f}\n"

    notification = Notification(
        user_id=user_id,
        stock_id=stock_id,
        monitor_id=monitor_id,
        type=notify_type,
        content=content
    )
    db.add(notification)
    await db.commit()

    await send_notification(db, user_id, content)

async def send_notification(db: AsyncSession, user_id: int, content: str):
    from app.models.monitor import NotificationConfig
    import httpx

    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == user_id)
    )
    config = result.scalar_one_or_none()

    if not config or not config.is_enabled or not config.api_url:
        return

    try:
        headers = config.api_headers or {}
        async with httpx.AsyncClient() as client:
            await client.request(
                method=config.api_method or "POST",
                url=config.api_url,
                json={"content": content},
                headers=headers,
                timeout=10.0
            )

        notification_update = await db.execute(
            select(Notification).order_by(Notification.id.desc()).limit(1)
        )
        notif = notification_update.scalar_one_or_none()
        if notif:
            notif.is_sent = True
            notif.sent_at = datetime.now()
            await db.commit()
    except Exception as e:
        print(f"发送通知失败: {e}")

async def check_and_notify(db: AsyncSession) -> None:
    """
    检查所有活跃监测并发送通知（并发优化版本）
    """
    import asyncio
    
    result = await db.execute(
        select(Monitor)
        .options(selectinload(Monitor.stock))
        .where(Monitor.is_active == True)
    )
    monitors = result.scalars().all()
    
    if not monitors:
        return
    
    # 收集所有股票代码
    stock_codes = list(set(m.stock.code for m in monitors if m.stock))
    
    # 并发获取所有行情
    semaphore = asyncio.Semaphore(10)
    
    async def fetch_quote(code: str):
        async with semaphore:
            try:
                return code, await data_fetcher.get_realtime_quote_for_monitor(code)
            except Exception as e:
                logger.warning(f"获取行情失败: {code}, 错误: {e}")
                return code, {}
    
    quote_results = await asyncio.gather(*[fetch_quote(code) for code in stock_codes])
    quotes_map = {code: quote for code, quote in quote_results}
    
    # 检查每个监测条件
    for monitor in monitors:
        if not monitor.stock:
            continue
            
        realtime = quotes_map.get(monitor.stock.code, {})
        if not realtime or 'price' not in realtime:
            continue

        current_price = realtime['price']
        pre_close = realtime.get('pre_close', current_price)
        change_pct = ((current_price - pre_close) / pre_close * 100) if pre_close > 0 else 0

        should_notify = False
        notify_type = None
        notify_value = None

        if monitor.price_min and current_price <= monitor.price_min:
            should_notify = True
            notify_type = 'price_min'
            notify_value = current_price
        elif monitor.price_max and current_price >= monitor.price_max:
            should_notify = True
            notify_type = 'price_max'
            notify_value = current_price
        elif monitor.rise_threshold and change_pct >= monitor.rise_threshold:
            should_notify = True
            notify_type = 'rise'
            notify_value = change_pct
        elif monitor.fall_threshold and change_pct <= -monitor.fall_threshold:
            should_notify = True
            notify_type = 'fall'
            notify_value = change_pct

        if should_notify:
            await create_and_send_notification(
                db=db,
                user_id=monitor.user_id,
                stock_id=monitor.stock_id,
                monitor_id=monitor.id,
                notify_type=notify_type,
                notify_value=notify_value,
                current_data=realtime
            )
