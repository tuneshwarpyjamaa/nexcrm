import asyncio
import asyncpg
import os
from dotenv import load_dotenv

load_dotenv()

async def check_schema():
    conn = await asyncpg.connect(os.getenv('DATABASE_URL'))
    rows = await conn.fetch('SELECT column_name FROM information_schema.columns WHERE table_name = \'emails\' ORDER BY ordinal_position')
    print([row['column_name'] for row in rows])
    await conn.close()

if __name__ == "__main__":
    asyncio.run(check_schema())
