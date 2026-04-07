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
                        email VARCHAR(255),
                        hashed_password VARCHAR(255),
                        auth_provider VARCHAR(50) NOT NULL DEFAULT 'local',
                        google_sub VARCHAR(255),
                        is_active BOOLEAN DEFAULT TRUE
                    );
                """)
                await cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS email VARCHAR(255);")
                await cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS auth_provider VARCHAR(50) NOT NULL DEFAULT 'local';")
                await cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS google_sub VARCHAR(255);")
                await cur.execute("ALTER TABLE users ALTER COLUMN hashed_password DROP NOT NULL;")
                await cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS users_email_unique_idx
                    ON users (email)
                    WHERE email IS NOT NULL;
                """)
                await cur.execute("""
                    CREATE UNIQUE INDEX IF NOT EXISTS users_google_sub_unique_idx
                    ON users (google_sub)
                    WHERE google_sub IS NOT NULL;
                """)
        logger.info("Database tables verified/created successfully.")
    except Exception as e:
        logger.error(f"Error during database initialization: {e}", exc_info=True)
        raise
