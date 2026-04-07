from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, Token, GoogleAuthRequest
from app.api.v1.endpoints.user_repository import UserRepository
from app.services.auth_service import AuthService
from app.services.auth_controller import AuthController

router = APIRouter()

# Dependency to get db pool
def get_pool(request: Request):
    return request.app.state.pool

# Dependency Injection Pipeline
def get_auth_controller(pool=Depends(get_pool)) -> AuthController:
    repository = UserRepository(pool)
    service = AuthService(repository)
    return AuthController(service)

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, controller: AuthController = Depends(get_auth_controller)):
    return await controller.signup(user)

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), controller: AuthController = Depends(get_auth_controller)):
    return await controller.login(form_data)

@router.get("/google/config")
async def google_config(controller: AuthController = Depends(get_auth_controller)):
    return await controller.google_config()

@router.post("/google", response_model=Token)
async def google_login(payload: GoogleAuthRequest, controller: AuthController = Depends(get_auth_controller)):
    return await controller.google_login(payload.credential)
