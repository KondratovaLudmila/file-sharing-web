from fastapi import Depends, APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from ..dependencies.db import SessionLocal, get_db
from ..services.auth import (oauth2_scheme,
                             create_refresh_token,
                             create_access_token, 
                             get_user_by_refresh_token, 
                             verify_password)
from ..repository.users import UserRepository
from ..schemas.user import UserCreate, User

router = APIRouter(prefix='/auth', tags=["auth"])

@router.post('/signup', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = await UserRepository(db).create(**user_data.dict())
    return user


@router.post("/signin", response_model=dict)
async def signin(username: str, password: str, db: Session = Depends(get_db)):
    user = UserRepository(db).get_username(username)
    
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")

    
    refresh_token = create_refresh_token({"sub": username})

    user_repo = UserRepository(db)
    user_repo.update(user, refresh_token=refresh_token)

    return {
        "access_token": create_access_token(data={"sub": username}),
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post("/refresh_token")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user = await get_user_by_refresh_token(refresh_token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user.username})
    return {"access_token": new_access_token, "token_type": "bearer"}