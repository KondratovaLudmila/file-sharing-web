from fastapi import APIRouter, HTTPException, Depends, status, Path, Query, UploadFile, File, Form
from typing import List, Annotated
from sqlalchemy.orm import Session


from ..schemas.image import ImageResponseModel, ImageDescriptionUpdate
from ..dependencies.db import get_db
from ..repository.images import Images as ImagesRepo
from ..models.user import User


router = APIRouter(prefix='/images', tags=["images"])


@router.get('/', response_model=List[ImageResponseModel], status_code=status.HTTP_201_CREATED)
async def create_image(db: Session=Depends(get_db)):
    
    # Temporary before we have users
    user = db.get(User, 1)
    if not user:
        db.add(User(username="vasya", password="1234", email="vasya@gmail.com", confirmed=True))
        db.commit()

    images = await ImagesRepo(user, db).get_many()
    return images


@router.post('/', response_model=ImageResponseModel)
async def create_image(file: Annotated[UploadFile, File()],
                        description: Annotated[str, Form()], 
                        db: Session=Depends(get_db)):
    
    # Temporary before we have users
    user = db.get(User, 1)
    if not user:
        db.add(User(username="vasya", password="1234", email="vasya@gmail.com", confirmed=True))
        db.commit()

    image = await ImagesRepo(user, db).create(file.file, description)
    return image


@router.patch('/{image_id}', response_model=ImageResponseModel)
async def update_image_description(body: ImageDescriptionUpdate, image_id: int, db: Session=Depends(get_db)):
    # Temporary
    user = db.get(User, 1)
    image = await ImagesRepo(user, db).update(image_id, body)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.delete('/{image_id}', response_model=ImageResponseModel)
async def delete_image(image_id: int, db: Session=Depends(get_db)):
    # Temporary
    user = db.get(User, 1)
    image = await ImagesRepo(user, db).delete(image_id)

    if not image:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image

