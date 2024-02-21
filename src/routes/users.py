from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..schemas.user import UserCreate, UserUpdate, User
from ..repository.users import UserRepository
from ..dependencies.db import get_db
from ..dependencies.roles import RoleAccess
from ..models.user import Role

router = APIRouter(prefix='/users', tags=["users"])

# Implement role access
allowed_action = RoleAccess([Role.admin, Role.moderator])

# Implement role access
@router.get('/', response_model=List[User], dependencies=[Depends(allowed_action),])
async def get_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    users = await user_repo.get_many(query)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return users


@router.post('/', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = await UserRepository(db).create(**user_data.dict())
    return user


@router.put('/{user_id}', response_model=User)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await user_repo.update(user=user, **user_data.dict())
    return updated_user


@router.delete('/{user_id}', response_model=User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user_repo.delete(user)
    return user

@router.get('/{user_id}', response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = await UserRepository(db).get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get('/users/{username}', response_model=User)
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user

