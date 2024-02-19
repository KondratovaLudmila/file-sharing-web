from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


from .tag import TagResponse
from .comment_example import Comment 

class ImageResponseModel(BaseModel):
    id: int
    identifier: str
    description: str
    url: str
    tags: List[TagResponse]
    comments: List[Comment] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImageDescriptionUpdate(BaseModel):
    description: str=Field(max_length=250)