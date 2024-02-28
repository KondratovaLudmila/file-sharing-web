from pydantic import BaseModel, EmailStr, field_validator, validator
from typing import Union, Optional
from ..models.user import Role
from datetime import date


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
    
    class Config:
        from_attributes = True


class UserUpdateResponse(UserResponse):
    avatar: str | None


class UserProfileResponse(UserUpdateResponse):
    images: int
    comments: int
    created_at: date

    @field_validator("images", mode="before")
    def image_count(cls, val):
        return len(val)
    
    @field_validator("comments", mode="before")
    def comments_count(cls, val):
        return len(val)
    
    @field_validator("created_at", mode="before")
    def created_at_date(cls, val):
        return val.date()  