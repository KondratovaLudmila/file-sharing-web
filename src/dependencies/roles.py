from fastapi import Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from ..repository.base_repository import AbstractRepository
from ..dependencies.db import get_db
from ..services.auth import get_current_user
from ..models.user import User, Role

class RoleAccess:
    def __init__(self, permited_roles: list[Role]):
        self.permited_roles = permited_roles

    def __call__(self, request: Request, user: User=Depends(get_current_user)) -> User:
        if user.role not in self.permited_roles:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Current user not authorized for this action')
        
        return True

class OwnerRoleAccess:
    def __init__(self, permited_roles: list[Role], repository: AbstractRepository, param_name: str):
        self.repo = repository
        self.param_name = param_name
        self.permited_roles = permited_roles
        

    async def __call__(self, request: Request, 
                       user: User = Depends(get_current_user), 
                       db: Session=Depends(get_db)) -> User:
        
        permited = user.role in self.permited_roles
        if not permited:
            try:
                pk = request.path_params.get(self.param_name)
                record = await self.repo(user, db).get_single(pk)
                permited = record is None or record.user_id == user.id
            except Exception as err:
                print(err)
        
        if not permited:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, 
                                detail='Current user not authorized for this action')
        
        return True

        

