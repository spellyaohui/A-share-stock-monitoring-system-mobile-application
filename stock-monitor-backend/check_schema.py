import asyncio
import aiomysql
from app.config import get_settings

settings = get_settings()

async def check_schema():
    conn = await aiomysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        charset='utf8mb4'
    )

    async with conn.cursor() as cursor:
        await cursor.execute("DESCRIBE users")
        result = await cursor.fetchall()
        print("Users table schema:")
        for row in result:
            print(f"  {row[0]} - {row[1]}")

    await conn.ensure_closed()

if __name__ == "__main__":
    asyncio.run(check_schema())
