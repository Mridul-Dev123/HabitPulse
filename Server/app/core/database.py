from psycopg_pool import AsyncConnectionPool
from app.core.config import settings

# Global pool reference
pool = None

async def get_db_pool():
    global pool
    url = settings.DB_URL.strip("'").strip('"')
    
    pool = AsyncConnectionPool(url, open=False)
    await pool.open()
    return pool

async def init_db(pool: AsyncConnectionPool):
    async with pool.connection() as conn:
        async with conn.cursor() as cur:
            await cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(255) UNIQUE NOT NULL,
                    hashed_password VARCHAR(255) NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE
                );
            """)
