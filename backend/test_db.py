import asyncio
from db import get_pool
from subscriptions.schemas import SubscriptionAction

async def test_sub():
    pool = await get_pool()
    async with pool.acquire() as conn:
        print("Checking users table:")
        users = await conn.fetch("SELECT * FROM users")
        for u in users:
            print(dict(u))

asyncio.run(test_sub())
