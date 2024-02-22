from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    body: str

class CommentCreate(CommentBase):
    image_id: int
    user_id: int

class Comment(CommentBase):
    id: int
    image_id: int
    user_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True