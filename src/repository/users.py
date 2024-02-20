from sqlalchemy.orm import Session
from ..models.user import User, Role, Enum
from ..schemas.user import UserCreate, UserUpdate
from .base_repository import AbstractRepository
from typing import Optional, List
from sqlalchemy import inspect, or_, func


class UserRepository(AbstractRepository):
    def __init__(self, db: Session):
        self.db = db

    async def create(self, username: str, email: str, password: str, avatar: str = None) -> User:
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
            setattr(user, key, value)
        insp = inspect(user)
        with self.db.begin_nested():
            if insp.pending:
                self.db.flush()
        return user


    async def delete(self, user: User):
        self.db.delete(user)
        self.db.commit()


    async def get_single(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()


    async def get_many(self, query: str) -> List[User]:
        query = query.lower()
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
            )
        ).all()
        return users



