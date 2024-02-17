from pydantic import BaseModel
from datetime import datetime

class CommentBase(BaseModel):
    body: str

class CommentCreate(CommentBase):
    pass

class Comment(CommentBase):
    id: int
    image_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True