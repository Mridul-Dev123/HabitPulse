from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from app.models.user import UserCreate, Token
from app.services import auth_service
from app.core import security

router = APIRouter()

# Dependency to get db pool
def get_pool(request: Request):
    return request.app.state.pool

@router.post("/signup", status_code=status.HTTP_201_CREATED)
async def signup(user: UserCreate, pool=Depends(get_pool)):
    db_user = await auth_service.get_user_by_username(pool, user.username)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )
    
    new_user = await auth_service.create_user(pool, user)
    return {"message": "User created successfully", "user_id": new_user["id"], "username": new_user["username"]}

@router.post("/login", response_model=Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), pool=Depends(get_pool)):
    user_dict = await auth_service.get_user_by_username(pool, form_data.username)
    if not user_dict or not security.verify_password(form_data.password, user_dict["hashed_password"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token = security.create_access_token(data={"sub": user_dict["username"]})
    return {"access_token": access_token, "token_type": "bearer"}
