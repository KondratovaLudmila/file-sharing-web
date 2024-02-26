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
        """
        The create function creates a new user in the database.

        :param self: Represent the instance of a class
        :param username: str: Specify the type of data that is expected to be passed in
        :param email: str: Get the email of the user
        :param password: str: Create a new user
        :param avatar: str: Store the avatar image of a user
        :return: A user object
        """
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
        """
        The update function takes a user object and updates it with the values passed in.
        It then returns the updated user object.

        :param self: Represent the instance of the class
        :param user: User: Get the user object from the database
        :param **kwargs: Pass a variable number of keyword arguments to the function
        :return: The updated user
        """
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
        """
    The delete function deletes a user from the database.


    :param self: Represent the instance of the class
    :param user: User: Pass in the user object to be deleted
    :return: The number of rows deleted
    :doc-author: Trelent
    """
        self.db.delete(user)
        self.db.commit()


    async def get_single(self, user_id: int) -> Optional[User]:
        """
    The get_single function is used to retrieve a single user from the database.
    It takes in an integer, which represents the id of the user we want to get.
    The function returns either a User object or None if no such user exists.

    :param self: Represent the instance of the class
    :param user_id: int: Specify the user_id of the user we want to get
    :return: The first user with the given id
    :doc-author: Trelent
    """
        return self.db.query(User).filter(User.id == user_id).first()


    async def get_username(self, user_name: str) -> Optional[User]:
        """
    The get_username function takes in a user_name and returns the first User object that matches
    the username. If no such user exists, it returns None.

    :param self: Refer to the class instance itself
    :param user_name: str: Specify the type of data that will be passed into the function
    :return: The first user in the database whose username matches the one provided as an argument
    :doc-author: Trelent
    """
        return self.db.query(User).filter(User.username == user_name).first()


    async def get_email(self, user_email: str) -> Optional[User]:
        """
    The get_email function takes in a user_email string and returns the first User object that matches
    the email. If no such user exists, it returns None.

    :param self: Refer to the class instance itself, and is always required in a method
    :param user_email: str: Specify the type of data that is being passed in to the function
    :return: The first user object in the database with a matching email address
    :doc-author: Trelent
    """
        return self.db.query(User).filter(User.email == user_email).first()



    async def get_many(self, query: str) -> List[User]:
        """
    The get_many function is used to search for users by username or email.
    It returns a list of User objects that match the query.

    :param self: Represent the instance of a class
    :param query: str: Filter the results of the query
    :return: A list of user objects that match the query
    :doc-author: Trelent
    """
        query = query.lower()
        users = self.db.query(User).filter(
            or_(
                User.username.ilike(f'%{query}%'),
                User.email.ilike(f'%{query}%'),
            )
        ).all()
        return users

    async def ban(self, user_id: int) -> User:
        """
    The ban function is used to ban a user.

    :param self: Access the class attributes and methods
    :param user_id: int: Get the user id from the database
    :return: A user object
    :doc-author: Trelent
    """
        user = await self.get_single(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.ban = not user.ban
        await self.update(user)
        return user


    async def change_role(self, user_id: int, new_role: Role) -> Optional[User]:
        """
    The change_role function changes the role of a user.

    :param self: Refer to the class itself, and is used in order to access other methods within the same class
    :param user_id: int: Identify the user that we want to change the role for
    :param new_role: Role: Set the new role of a user
    :return: The updated user object, which is of type user
    :doc-author: Trelent
    """
        user = await self.get_single(user_id)
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")

        user.role = new_role.value
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user





