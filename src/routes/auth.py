from fastapi import Depends, APIRouter, HTTPException
from services.auth import oauth2_scheme,settings, create_access_token, get_current_user, get_user_by_refresh_token, verify_password, get_user
from sqlalchemy.orm import Session
from dependencies.db import SessionLocal

router = APIRouter(prefix="/auth",tags=["Authentication"])

@router.post("/auth/signup", pass_credentials=True)
async def signup():
    pass

@router.post("/auth/signin")
async def signin(username: str, password: str, db: Session = Depends(SessionLocal)):
    user = get_user(db, username)
    if not user or not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    return {"access_token": create_access_token(data={"sub": username}), "token_type": "bearer"}

@router.post("/auth/refresh_token")
async def refresh_token(refresh_token: str = Depends(oauth2_scheme), db: Session = Depends(SessionLocal)):
    user = await get_user_by_refresh_token(refresh_token, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    new_access_token = create_access_token(data={"sub": user.name})
    return {"access_token": new_access_token, "token_type": "bearer"}
