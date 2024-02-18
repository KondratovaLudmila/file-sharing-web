from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List

from ..schemas.user import UserCreate, UserUpdate, User
from ..repository.users import UserRepository  # Зміна імені класу
from ..dependencies.db import get_db

router = APIRouter(prefix='/users', tags=["users"])

@router.post('/', response_model=User, status_code=status.HTTP_201_CREATED)
async def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    user = UserRepository(db).create_user(**user_data.dict())  # Виклик методу create_user з правильними аргументами
    return user


@router.put('/{user_id}', response_model=User)
async def update_user(user_id: int, user_data: UserUpdate, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await user_repo.update_user(user=user, **user_data.dict())
    return updated_user


@router.delete('/{user_id}', response_model=User)
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    user = await user_repo.get_single_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    user_repo.delete_user(user)
    return user


@router.get('/{user_id}', response_model=User)
async def get_user(user_id: int, db: Session = Depends(get_db)):
    user = UserRepository(db).get_single_user(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


@router.get('/search/', response_model=List[User])
async def search_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    user_repo = UserRepository(db)
    users = user_repo.search_users(query)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return users

