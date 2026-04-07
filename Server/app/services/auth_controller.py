import logging
from fastapi import HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate
from app.services.auth_service import AuthService

logger = logging.getLogger(__name__)

class AuthController:
    def __init__(self, auth_service: AuthService):
        self.auth_service = auth_service

    async def signup(self, user: UserCreate):
        logger.info(f"Signup attempt for username: {user.username}")
        try:
            new_user = await self.auth_service.register_user(user)
            logger.info(f"User created successfully: {new_user['username']}")
            return {
                "message": "User created successfully", 
                "user_id": new_user["id"], 
                "username": new_user["username"]
            }
        except ValueError as e:
            logger.warning(f"Signup failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Error creating user {user.username}: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")

    async def login(self, form_data: OAuth2PasswordRequestForm):
        logger.info(f"Login attempt for username: {form_data.username}")
        access_token = await self.auth_service.authenticate_user(form_data.username, form_data.password)
        
        if not access_token:
            logger.warning(f"Login failed: Incorrect credentials for {form_data.username}")
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password", headers={"WWW-Authenticate": "Bearer"})
        
        logger.info(f"Login successful for username: {form_data.username}")
        return {"access_token": access_token, "token_type": "bearer"}

    async def google_config(self):
        return {"client_id": self.auth_service.get_google_client_id()}

    async def google_login(self, credential: str):
        logger.info("Google login attempt")
        try:
            access_token = await self.auth_service.authenticate_google_user(credential)
            logger.info("Google login successful")
            return {"access_token": access_token, "token_type": "bearer"}
        except ValueError as e:
            logger.warning(f"Google login failed: {str(e)}")
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected Google login error: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail="Internal Server Error")
