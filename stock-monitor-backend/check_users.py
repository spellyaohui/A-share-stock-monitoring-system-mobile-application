#!/usr/bin/env python3
import asyncio
from app.database import AsyncSessionLocal
from sqlalchemy import text

async def check_users():
    async with AsyncSessionLocal() as db:
        result = await db.execute(text("SELECT id, username, email FROM users"))
        users = result.fetchall()
        print("用户数据:")
        for user in users:
            print(f"ID: {user.id}, 用户名: {user.username}, 邮箱: {user.email}")

if __name__ == "__main__":
    asyncio.run(check_users())