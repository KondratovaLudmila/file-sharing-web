from sqlalchemy.orm import Session
from ..models.user import User
from ..schemas.user import UserCreate, UserUpdate
from .base_repository import AbstractRepository
from typing import Optional, List
from sqlalchemy import inspect, or_


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, username: str, email: str, password: str, avatar: str = None, refresh_token: str = None, confirmed: bool = False, ban: bool = False) -> User:
        user = User(username=username, email=email, password=password, avatar=avatar, refresh_token=refresh_token, confirmed=confirmed, ban=ban)
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    async def update_user(self, user: User, **kwargs) -> User:
        for key, value in kwargs.items():
            setattr(user, key, value)
        insp = inspect(user)
        with self.db.begin_nested():
            if insp.pending:
                self.db.flush()  # Flush to update user data
        return user

    def delete_user(self, user: User):
        self.db.delete(user)
        self.db.commit()

    async def get_single_user(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def search_users(self, query: str) -> List[User]:
        query = query.lower()
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
            )
        ).all()
        return users



