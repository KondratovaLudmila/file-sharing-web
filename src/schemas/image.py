from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum

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





