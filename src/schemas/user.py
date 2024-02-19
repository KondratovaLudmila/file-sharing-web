from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    username: str
    email: EmailStr
    password: str


class UserUpdate(BaseModel):
    email: EmailStr
    password: str


class UserInDBBase(UserCreate):
    id: int

    class Config:
        orm_mode = True


class User(UserInDBBase):
    pass