import asyncio
import aiomysql
from app.config import get_settings

settings = get_settings()

async def update_password():
    conn = await aiomysql.connect(
        host=settings.MYSQL_HOST,
        port=settings.MYSQL_PORT,
        user=settings.MYSQL_USER,
        password=settings.MYSQL_PASSWORD,
        db=settings.MYSQL_DB,
        charset='utf8mb4'
    )

    new_hash = '$2b$12$x.xeAf8xQvzerCbsejiwvupRe9UutT/iG/ypyCfvMivSNlnvwmr5.'

    async with conn.cursor() as cursor:
        await cursor.execute(
            "UPDATE users SET password_hash = %s WHERE username = 'admin'",
            (new_hash,)
        )
        await conn.commit()
        print(f"Updated {cursor.rowcount} rows")

    await conn.ensure_closed()
    print("Password updated successfully!")

if __name__ == "__main__":
    asyncio.run(update_password())
