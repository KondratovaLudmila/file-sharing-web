from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List, Annotated

from ..schemas.user import UserCreate, UserUpdate, UserResponse, UserUpdateResponse, UserBan
from ..repository.users import UserRepository
from ..dependencies.db import get_db
from ..dependencies.roles import RoleAccess
from ..models.user import Role, User
from ..services.auth import get_current_user

router = APIRouter(prefix='/users', tags=["users"])

# Implement role access
allowed_action = RoleAccess([Role.admin])

# Implement role access
@router.get('/', response_model=List[UserResponse], dependencies=[Depends(allowed_action),])
async def get_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    users = await user_repo.get_many(query)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return users


@router.put('/me', response_model=UserUpdateResponse)
async def update_user( avatar: Annotated[UploadFile, File()], user_email: EmailStr = Form(max_length=150, default=None), db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await user_repo.update(user=user, email=user_email, avatar=avatar.file)
    return updated_user


@router.delete('/{user_id}', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user_repo.delete(user)
    return user

@router.get('/{user_id}', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await UserRepository(db).get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get('/profile/{username}', response_model=UserResponse, dependencies=[Depends(get_current_user)])
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put('/{user_id}/ban', response_model=UserBan, dependencies=[Depends(allowed_action)])
async def ban_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    return await user_repo.ban_user(user_id)


@router.put('/{user_id}/role', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def change_user_role(user_id: int, new_role: Role, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.change_user_role(user_id, new_role)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user





