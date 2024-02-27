from fastapi import Depends, APIRouter, HTTPException, Security, status
from sqlalchemy.orm import Session
from fastapi.security import (HTTPAuthorizationCredentials, OAuth2PasswordRequestForm,
                              HTTPBearer,
                              )

from ..dependencies.db import get_db
from ..services.auth import (oauth2_scheme,
                             create_refresh_token,
                             create_access_token, 
                             get_user_by_refresh_token, 
                            )
from ..repository.users import UserRepository
from ..services.hash_handler import hash_password, check_password
from ..schemas.user import UserCreate, UserResponse


router = APIRouter(prefix='/auth', tags=["auth"])

security = HTTPBearer()

@router.post('/signup', response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_username_user = await UserRepository(db).get_username(user_data.username)
    if existing_username_user:
        raise HTTPException(status_code=409, detail="User with the same username already exists.")

    existing_email_user = await UserRepository(db).get_email(user_data.email)
    if existing_email_user:
        raise HTTPException(status_code=409, detail="User with the same email already exists.")
    
    user_data.password = hash_password(user_data.password)
    user = await UserRepository(db).create(**user_data.dict())
    
    return user


@router.post("/signin", response_model=dict)
async def signin(request_user: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = await UserRepository(db).get_username(request_user.username)
    
    if not user or not check_password(request_user.password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    refresh_token = create_refresh_token({"sub": request_user.username})

    user_repo = UserRepository(db)
    user = await user_repo.update(user, refresh_token=refresh_token)

    return {
        "access_token": create_access_token(data={"sub": request_user.username}),
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.get("/refresh_token")
async def refresh_token(credentials: HTTPAuthorizationCredentials=Security(security), db: Session = Depends(get_db)):
    user = await get_user_by_refresh_token(credentials.credentials, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user.username})
    return {"access_token": new_access_token, "token_type": "bearer"}