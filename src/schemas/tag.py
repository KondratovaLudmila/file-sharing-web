from pydantic import BaseModel, Field


class TagModel(BaseModel):
    name: str = Field(max_length=25)

class TagResponse(TagModel):
    id: int

    class Config:
        from_attributes = True