from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.schemas.stock import MonitorCreate, MonitorUpdate, MonitorResponse
from app.services.monitor_service import (
    get_user_monitors, get_user_monitors_with_realtime,
    create_monitor, update_monitor, delete_monitor
)
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User

router = APIRouter()

@router.get("")
@router.get("/")
async def list_monitors(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    return await get_user_monitors_with_realtime(db, current_user.id)

@router.post("")
@router.post("/")
async def create(
    monitor: MonitorCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """创建监测"""
    from app.core.logging import get_logger
    logger = get_logger(__name__)
    
    logger.info(f"收到创建监测请求: 用户={current_user.username}, 数据={monitor.model_dump()}")
    
    try:
        result = await create_monitor(db, current_user.id, monitor)
        logger.info(f"监测创建成功: ID={result.id}")
        return result
    except ValueError as e:
        logger.error(f"监测创建失败 (ValueError): {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"监测创建失败 (Exception): {str(e)}")
        raise HTTPException(status_code=500, detail=f"创建监测失败: {str(e)}")

@router.put("/{monitor_id}")
async def update(
    monitor_id: int,
    monitor: MonitorUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        return await update_monitor(db, current_user.id, monitor_id, monitor)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{monitor_id}")
async def delete(
    monitor_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    try:
        await delete_monitor(db, current_user.id, monitor_id)
        return {"message": "删除成功"}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
