from fastapi import Depends, HTTPException, Request, status

from .auth import get_user

from ..models.user import User, Role

class Roles:
    def __init__(self, permited_roles: list[Role]):
        self.permited_roles = permited_roles

    def __call__(self, request: Request, user: User=Depends(get_user)) -> User:
        if user.role not in self.permited_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Current user not authorized for this action')
        