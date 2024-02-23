from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File, Form
from typing import List, Annotated
from sqlalchemy.orm import Session


from ..schemas.image import ImageResponseModel, ImageUpdate, ImageTransfornModel, ImageCreate, ImageCreateResponseModel
from ..dependencies.db import get_db
from ..repository.images import Images as ImagesRepo
from ..repository.tags import Tags as TagsRepo
from ..models.user import User
from ..services.auth import get_current_user
from ..dependencies.roles import OwnerRoleAccess, Role


router = APIRouter(prefix='/images', tags=["images"])

allowed_action = OwnerRoleAccess(permited_roles=[Role.admin,], 
                                 repository=ImagesRepo, 
                                 param_name='image_id')

@router.get('/', response_model=List[ImageResponseModel])
async def get_images(user: User=Depends(get_current_user), db: Session=Depends(get_db)):
    images = await ImagesRepo(user, db).get_many()
    return images


@router.post('/', response_model=ImageCreateResponseModel, status_code=status.HTTP_201_CREATED)
async def create_image(image_form: ImageCreate=Depends(ImageCreate.as_form),
                        user: User=Depends(get_current_user),
                        db: Session=Depends(get_db)):
    
    tags = await TagsRepo(db).get_or_create_many(image_form.tags)

    image = await ImagesRepo(user, db).create(image_form.file.file, 
                                              image_form.description, 
                                              tags)
    return image


@router.patch('/{image_id}', response_model=ImageResponseModel, dependencies=[Depends(allowed_action),])
async def update_image_description(body: ImageUpdate, image_id: int, 
                                   user: User=Depends(get_current_user),
                                   db: Session=Depends(get_db)):
    
    body.tags = await TagsRepo(db).get_or_create_many(body.tags)
    image = await ImagesRepo(user, db).update(image_id, body)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.delete('/{image_id}', response_model=ImageResponseModel, dependencies=[Depends(allowed_action),])
async def delete_image(image_id: int, 
                       user: User=Depends(get_current_user),
                       db: Session=Depends(get_db),
                       ):
    image = await ImagesRepo(user, db).delete(image_id)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.post('/{image_id}/transform', response_model=ImageResponseModel)
async def transform_image(image_id: int, 
                          transform_model: ImageTransfornModel,
                          user: User=Depends(get_current_user),
                          db: Session=Depends(get_db)):
    
    image = await ImagesRepo(user, db).transform(image_id, transform_model)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


# @router.post('/{image_id}/qr', response_model=ImageResponseModel)
# async def transform_image(image_id: int, transform_model: ImageTransfornModel, db: Session=Depends(get_db)):
#     # Temporary
#     user = db.query(User).filter().first()
    
#     image = await ImagesRepo(user, db).transform(image_id, transform_model)

#     if not image:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")

#     return image
