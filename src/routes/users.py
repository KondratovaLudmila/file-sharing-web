from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, File, UploadFile
from pydantic import EmailStr
from sqlalchemy.orm import Session
from typing import List, Annotated

from ..schemas.user import UserCreate, UserUpdate, UserResponse, UserUpdateResponse, UserBan, UserProfileResponse
from ..repository.users import UserRepository
from ..dependencies.db import get_db
from ..dependencies.roles import RoleAccess
from ..models.user import Role, User
from ..services.auth import get_current_user

router = APIRouter(prefix='/users', tags=["users"])

allowed_action = RoleAccess([Role.admin])

# Implement role access
@router.get('/', response_model=List[UserResponse], dependencies=[Depends(allowed_action),])
async def get_users(query: str = Query(..., min_length=1), db: Session = Depends(get_db)):
    """
The get_users function returns a list of users.

:param query: str: Filter the users by their name
:param min_length: Set a minimum length for the query string
:param db: Session: Get the database session
:return: A list of users
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    users = await user_repo.get_many(query)
    if not users:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Users not found")
    return users


@router.put('/me', response_model=UserUpdateResponse)
async def update_user( avatar: Annotated[UploadFile, File()], user_email: EmailStr = Form(max_length=150, default=None), db: Session = Depends(get_db), user: User=Depends(get_current_user)):
    """
The update_user function updates a user's email and avatar.
    The function takes in an UploadFile object, which is the avatar file that will be uploaded to the server.
    It also takes in an EmailStr object, which is the new email address of the user.
    Finally it takes in a Session object from SQLAlchemy and uses it to create a UserRepository instance for interacting with our database.

:param avatar: Annotated[UploadFile: Upload the file to the server
:param File()]: Indicate that the avatar is a file
:param user_email: EmailStr: Update the user's email address
:param default: Set a default value for the parameter if no argument is passed
:param db: Session: Get the database session
:param user: User: Get the current user from the database
:return: A user object
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user.id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    updated_user = await user_repo.update(user=user, email=user_email, avatar=avatar.file)
    return updated_user


@router.delete('/{user_id}', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def delete_user(user_id: int, db: Session = Depends(get_db)):
    """
The delete_user function deletes a user from the database.

:param user_id: int: Specify the user id of the user to be deleted
:param db: Session: Get the database session
:return: The deleted user
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    user = await user_repo.get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    await user_repo.delete(user)
    return user

@router.get('/{user_id}', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """
The get_user function takes a user_id and returns the corresponding User object.
If no such user exists, it raises an HTTP 404 error.

:param user_id: int: Specify the user_id that will be passed in as a path parameter
:param db: Session: Pass the database session to the repository
:return: A user object
:doc-author: Trelent
"""
    user = await UserRepository(db).get_single(user_id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@router.get('/profile/{username}', response_model=UserProfileResponse, dependencies=[Depends(get_current_user)])
async def get_user_by_username(username: str, db: Session = Depends(get_db)):
    """
The get_user_by_username function is a coroutine that takes in a username and returns the user object
    associated with that username. If no such user exists, it raises an HTTPException.

:param username: str: Pass the username of the user to be retrieved
:param db: Session: Get the database session from the dependency injection container
:return: A user object
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    user = await user_repo.get_username(username)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch('/{user_id}/ban', response_model=UserBan, dependencies=[Depends(allowed_action)])
async def ban_user(user_id: int, db: Session = Depends(get_db)):
    """
The ban_user function takes a user_id and bans the user with that id.
    It returns True if the ban was successful, False otherwise.

:param user_id: int: Pass the user_id of the user to be banned
:param db: Session: Pass the database session to the repository
:return: A boolean value
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    return await user_repo.ban(user_id)


@router.patch('/{user_id}/role', response_model=UserResponse, dependencies=[Depends(allowed_action)])
async def change_user_role(user_id: int, new_role: Role, db: Session = Depends(get_db)):
    """
The change_user_role function changes the role of a user.
    Args:
        user_id (int): The id of the user to change.
        new_role (Role): The new role for the specified user.

:param user_id: int: Identify the user that will have their role changed
:param new_role: Role: Specify the role of the user
:param db: Session: Pass the database session to the userrepository
:return: A user object
:doc-author: Trelent
"""
    user_repo = UserRepository(db)
    user = await user_repo.change_role(user_id, new_role)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return user





