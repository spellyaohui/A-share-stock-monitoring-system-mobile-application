#!/usr/bin/env python3
import asyncio
from app.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash
from sqlalchemy import select

async def reset_admin_password():
    async with AsyncSessionLocal() as db:
        # 查找admin用户
        result = await db.execute(select(User).where(User.username == "admin"))
        admin_user = result.scalar_one_or_none()
        
        if admin_user:
            # 重新设置密码
            new_password_hash = get_password_hash("admin")
            admin_user.password_hash = new_password_hash
            await db.commit()
            print("admin用户密码已重置为: admin")
        else:
            print("未找到admin用户")

if __name__ == "__main__":
    asyncio.run(reset_admin_password())