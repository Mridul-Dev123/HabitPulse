from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from app.models.user import UserCreate
from app.core import security
from app.core.config import settings
from app.api.v1.endpoints.user_repository import UserRepository

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    def get_google_client_id(self) -> str | None:
        return settings.GOOGLE_CLIENT_ID

    async def register_user(self, user_in: UserCreate) -> dict:
        existing_user = await self.repository.get_by_username(user_in.username)
        if existing_user:
            raise ValueError("Username already registered")
        
        hashed_password = security.get_password_hash(user_in.password)
        new_user = await self.repository.create(user_in.username, hashed_password)
        return new_user

    async def authenticate_user(self, username: str, password: str) -> str | None:
        user = await self.repository.get_by_username(username)
        if not user or not user["hashed_password"] or not security.verify_password(password, user["hashed_password"]):
            return None
        
        access_token = security.create_access_token(data={"sub": user["username"]})
        return access_token

    async def authenticate_google_user(self, credential: str) -> str:
        if not settings.GOOGLE_CLIENT_ID:
            raise ValueError("Google authentication is not configured on the server")

        try:
            token_info = id_token.verify_oauth2_token(
                credential,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID,
            )
        except ValueError as exc:
            raise ValueError("Invalid Google credential") from exc

        email = (token_info.get("email") or "").strip().lower()
        google_sub = token_info.get("sub")
        email_verified = token_info.get("email_verified")

        if not email or not google_sub or not email_verified:
            raise ValueError("Google account email is not verified")

        user = await self.repository.get_by_google_sub(google_sub)

        if user and (
            user["email"] != email
            or user["google_sub"] != google_sub
            or user["auth_provider"] != "google"
        ):
            user = await self.repository.update_google_identity(user["id"], email, google_sub)

        if not user:
            user = await self.repository.get_by_email(email)

        if not user:
            user = await self.repository.get_by_username(email)

        if user and (user["email"] != email or user["google_sub"] != google_sub or user["auth_provider"] != "google"):
            user = await self.repository.update_google_identity(user["id"], email, google_sub)

        if not user:
            user = await self.repository.create_google_user(email, google_sub)

        access_token = security.create_access_token(
            data={
                "sub": user["username"],
                "email": email,
                "auth_provider": "google",
            }
        )
        return access_token
