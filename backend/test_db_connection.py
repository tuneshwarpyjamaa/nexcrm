import asyncpg
import asyncio
import os

async def test_db():
    try:
        conn = await asyncpg.connect(os.environ['DATABASE_URL'])
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        print('Database connection test passed')
    except Exception as e:
        print(f'Database connection test failed: {e}')
        raise

asyncio.run(test_db())
