from fastapi import Depends, HTTPException, Request, status

from ..services.auth import get_current_user

from ..models.user import User, Role

class RoleAccess:
    def __init__(self, permited_roles: list[Role]):
        self.permited_roles = permited_roles

    def __call__(self, request: Request, user: User=Depends(get_current_user)) -> User:
        if user.role not in self.permited_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Current user not authorized for this action')
        