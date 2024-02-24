from sqlalchemy.orm import Session
from ..models.user import User, Role, Enum
from ..schemas.user import UserCreate, UserUpdate
from .base_repository import AbstractRepository
from typing import Optional, List
from sqlalchemy import inspect, or_, func
from fastapi import HTTPException
from ..services.media_storage import storage


class UserRepository(AbstractRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, username: str, email: str, password: str, avatar: str = None) -> User:
        existing_username_user = self.db.query(User).filter(User.username == username).first()
        if existing_username_user:
            raise HTTPException(status_code=409, detail="User with the same username already exists.")

        existing_email_user = self.db.query(User).filter(User.email == email).first()
        if existing_email_user:
            raise HTTPException(status_code=409, detail="User with the same email already exists.")

        user = User(username=username, email=email, password=password, avatar=avatar)
        existing_users_count = self.db.query(func.count(User.id)).scalar()
        if existing_users_count == 0:
            user.role = Role.admin.value
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            if key=='avatar':
                try:
                    avatar = await storage.avatar_upload(value,user.username)
                    print(avatar.url)
                except Exception as err:
                    raise HTTPException(status_code=500, detail= str(err))
                value = avatar.url

            if key == 'email'and value is None:
                continue

            setattr(user, key, value)
        insp = inspect(user)
        with self.db.begin_nested():
            if insp.pending:
                self.db.flush()
            self.db.commit()
        return user


    async def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()


    async def get_single(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()


    async def get_username(self, user_name: str) -> Optional[User]:
        return self.db.query(User).filter(User.username == user_name).first()


    async def get_email(self, user_email: str) -> Optional[User]:
        return self.db.query(User).filter(User.email == user_email).first()



    async def get_many(self, query: str) -> List[User]:
        query = query.lower()
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
            )
        ).all()
        return users

    async def ban(self, user_id: int) -> User:
        user = await self.get_single(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.ban = True
        await self.update(user)
        return user


    async def change_role(self, user_id: int, new_role: Role) -> Optional[User]:
        user = await self.get_single(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.role = new_role.value
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user


