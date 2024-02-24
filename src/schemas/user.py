from pydantic import BaseModel, EmailStr
from typing import Union, Optional
from ..models.user import Role


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str
      
      
class UserUpdate(BaseModel):
    email: EmailStr

class UserResponse(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: Union[Role, str]

    class Config:
        from_attributes = True

class UserBan(UserResponse):
    ban: bool = False
    
    class Config
        from_attributes = True

class UserUpdateResponse(UserResponse):
    avatar: str