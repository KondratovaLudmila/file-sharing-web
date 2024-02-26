from fastapi import (APIRouter, 
                     HTTPException,
                     Depends, 
                     Request, 
                     status, 
                     Path, 
                     Query, 
                     UploadFile, 
                     File, 
                     Form,
                     )
from typing import List, Annotated
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
import qrcode
import io


from ..schemas.image import (ImageResponseModel, 
                             ImageUpdate, 
                             ImageTransfornModel, 
                             ImageCreate, 
                             ImageCreateResponseModel,
                             ImageShareModel,
                             ImageShareResponseModel,
                             )
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
async def get_images(offset: int=0, limit: int=0,
                     user: User=Depends(get_current_user), 
                     db: Session=Depends(get_db)):
    images = await ImagesRepo(user, db).get_many(offset, limit)
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
async def update_image_description(body: ImageUpdate, 
                                   image_id: int, 
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

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.post('/{image_id}/transform', response_model=ImageResponseModel)
async def transform_image(image_id: int, 
                          transform_model: ImageTransfornModel,
                          user: User=Depends(get_current_user),
                          db: Session=Depends(get_db)):
    
    image = await ImagesRepo(user, db).transform(image_id, transform_model)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.get('/{image_id}/share')
async def share_image(image_id: int,
                      request: Request, 
                      user: User=Depends(get_current_user),
                      db: Session=Depends(get_db)
                      ):
    image = await ImagesRepo(user, db).get_single(image_id)
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    url = str(request.base_url) + 'images/shared/' + image.identifier
    
    qr = qrcode.make(url)
    buf = io.BytesIO()
    qr.save(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="image/jpeg")


@router.get('/shared/{identifier}', response_model=ImageShareResponseModel)
async def get_shared_image(identifier: str, db: Session=Depends(get_db)):
    image = await ImagesRepo(None, db).identify(identifier)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")

    return image
