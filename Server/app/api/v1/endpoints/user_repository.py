from psycopg_pool import AsyncConnectionPool

class UserRepository:
    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool

    @staticmethod
    def _serialize_user(row) -> dict | None:
        if not row:
            return None

        return {
            "id": row[0],
            "username": row[1],
            "email": row[2],
            "hashed_password": row[3],
            "auth_provider": row[4],
            "google_sub": row[5],
            "is_active": row[6],
        }

    async def get_by_username(self, username: str) -> dict | None:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, username, email, hashed_password, auth_provider, google_sub, is_active
                    FROM users
                    WHERE username = %s
                    """,
                    (username,)
                )
                return self._serialize_user(await cur.fetchone())

    async def get_by_email(self, email: str) -> dict | None:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, username, email, hashed_password, auth_provider, google_sub, is_active
                    FROM users
                    WHERE email = %s
                    """,
                    (email,)
                )
                return self._serialize_user(await cur.fetchone())

    async def get_by_google_sub(self, google_sub: str) -> dict | None:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    SELECT id, username, email, hashed_password, auth_provider, google_sub, is_active
                    FROM users
                    WHERE google_sub = %s
                    """,
                    (google_sub,)
                )
                return self._serialize_user(await cur.fetchone())

    async def create(
        self,
        username: str,
        hashed_password: str | None,
        email: str | None = None,
        auth_provider: str = "local",
        google_sub: str | None = None,
    ) -> dict:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    INSERT INTO users (username, email, hashed_password, auth_provider, google_sub)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, username, email, hashed_password, auth_provider, google_sub, is_active
                    """,
                    (username, email, hashed_password, auth_provider, google_sub)
                )
                return self._serialize_user(await cur.fetchone())

    async def create_google_user(self, email: str, google_sub: str) -> dict:
        return await self.create(
            username=email,
            hashed_password=None,
            email=email,
            auth_provider="google",
            google_sub=google_sub,
        )

    async def update_google_identity(self, user_id: int, email: str, google_sub: str) -> dict:
        async with self.pool.connection() as conn:
            async with conn.cursor() as cur:
                await cur.execute(
                    """
                    UPDATE users
                    SET email = %s,
                        google_sub = %s,
                        auth_provider = 'google'
                    WHERE id = %s
                    RETURNING id, username, email, hashed_password, auth_provider, google_sub, is_active
                    """,
                    (email, google_sub, user_id)
                )
                return self._serialize_user(await cur.fetchone())
