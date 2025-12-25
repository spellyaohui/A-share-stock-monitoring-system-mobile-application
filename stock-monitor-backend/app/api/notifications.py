from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.models.monitor import Notification, NotificationConfig
from app.schemas.notification import NotificationConfigUpdate

router = APIRouter()

@router.get("/config")
async def get_config(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()
    if not config:
        return {
            "api_url": None,
            "api_method": "POST",
            "is_enabled": False
        }
    return {
        "id": config.id,
        "api_url": config.api_url,
        "api_method": config.api_method,
        "api_headers": config.api_headers,
        "is_enabled": config.is_enabled
    }

@router.put("/config")
async def update_config(
    config_update: NotificationConfigUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    result = await db.execute(
        select(NotificationConfig).where(NotificationConfig.user_id == current_user.id)
    )
    config = result.scalar_one_or_none()

    update_data = config_update.model_dump(exclude_unset=True)

    if not config:
        config = NotificationConfig(user_id=current_user.id, **update_data)
        db.add(config)
    else:
        for key, value in update_data.items():
            setattr(config, key, value)

    await db.commit()
    return {"message": "配置更新成功"}

@router.get("/history")
async def get_history(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    limit: int = 50
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(Notification.created_at.desc())
        .limit(limit)
    )
    notifications = result.scalars().all()
    return [
        {
            "id": n.id,
            "type": n.type,
            "content": n.content,
            "is_sent": n.is_sent,
            "created_at": n.created_at
        }
        for n in notifications
    ]
