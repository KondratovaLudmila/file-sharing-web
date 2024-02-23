from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime
from typing import List
from enum import Enum
from fastapi import HTTPException, UploadFile, Form, status

from .tag import TagResponse
from .comment_example import Comment 


class CropTransform(str, Enum):
    thumb = "thumb"
    fill = "fill"
    auto = "auto"
    pad = "pad"


class GravityTransform(str, Enum):
    face = "face"
    fases = "faces"


class EffectTransform(str, Enum):
    sepia = "sepia"
    cartunify = "cartunify"
    vignette = "vignette"
    pixelate = "pixelate"


class BackgroundTransform(str, Enum):
    auto = "auto"
    blure = "blurred"
    gen_fill = "gen_fill"


class ImageCreateResponseModel(BaseModel):
    id: int
    identifier: str
    description: str
    url: str
    tags: List[TagResponse]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ImageResponseModel(ImageCreateResponseModel):
    comments: List[Comment] = []


class ImageCreate(BaseModel):
    file: UploadFile
    description: str=Field(max_length=250)
    tags: List[str]=[]

    
    @field_validator('tags')
    @classmethod
    def max_length_check(cls, tags):
        if len(tags) > 5:
            raise HTTPException(
                detail=jsonable_encoder("Only up to five tags can be provided"),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        for tag in tags:
            l = len(tag)
            if l < 25 and l > 0:
                raise HTTPException(
                detail=jsonable_encoder("Length of each tag shoul be from 1 to 25 characters"),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return tags


    @classmethod
    def as_form(cls, file: UploadFile, description: str=Form(max_length=250), tags: List[str]=Form([])):
        try:
            tags = tags[0].split(',')
        except ValidationError as e:
            raise HTTPException(
                detail=jsonable_encoder(e.errors()),
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            )
        return cls(file=file, description=description, tags=tags)


class ImageUpdate(BaseModel):
    description: str=Field(max_length=250)
    tags: List[str]=[]


    @field_validator('tags')
    def max_length_check(cls, value):
        if len(value) > 5:
            raise ValueError("Only up to five tags allowed")
        if not all(len(tag) <= 25 and len(tag) > 0 for tag in value):
            raise ValueError("Max length of each tag 25")
        return value
        

class ImageTransfornModel(BaseModel):
    height: int | None = Field(gt=50)
    width: int | None = Field(gt=50)
    effect: EffectTransform | None
    crop: CropTransform | None
    gravity: GravityTransform | None
    radius: str | None = "max"
    background: BackgroundTransform | None

    class Config:
        use_enum_values = True


class ImageShareModel(BaseModel):
    identifier: str


class ImageShareResponseModel(BaseModel):
    url: str
    description: str



