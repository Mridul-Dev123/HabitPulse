import logging
from psycopg_pool import AsyncConnectionPool
from app.core.config import settings

logger = logging.getLogger(__name__)

# Global pool reference
pool = None

async def get_db_pool():
    global pool
    url = settings.DB_URL.strip("'").strip('"')
    
    try:
        logger.info(f"Attempting to connect to database at {url.split('@')[-1] if '@' in url else 'database'}")
        pool = AsyncConnectionPool(url, open=False)
        await pool.open()
        logger.info("Successfully connected to the database.")
        return pool
    except Exception as e:
        logger.error(f"Failed to connect to the database: {e}", exc_info=True)
        raise

async def init_db(pool: AsyncConnectionPool):
    try:
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
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        raise
