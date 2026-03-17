from psycopg_pool import AsyncConnectionPool
from psycopg.rows import dict_row
from typing import Optional
from app.models.user import UserCreate
from app.core.security import get_password_hash

async def get_user_by_username(pool: AsyncConnectionPool, username: str) -> Optional[dict]:
    async with pool.connection() as conn:
        async with conn.cursor(row_factory=dict_row) as cur:
            await cur.execute(
                "SELECT id, username, hashed_password, is_active FROM users WHERE username = %s;", 
                (username,)
            )
            row = await cur.fetchone()
            if row:
                return row
        return None

async def create_user(pool: AsyncConnectionPool, user: UserCreate) -> dict:
    hashed_password = get_password_hash(user.password)
    async with pool.connection() as conn:
        async with conn.transaction():
            async with conn.cursor(row_factory=dict_row) as cur:
                await cur.execute(
                    "INSERT INTO users (username, hashed_password) VALUES (%s, %s) RETURNING id;",
                    (user.username, hashed_password)
                )
                res = await cur.fetchone()
                user_id = res['id']
                
        return {
            "id": user_id,
            "username": user.username,
            "is_active": True
        }
