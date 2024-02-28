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
                             OrderBy,
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
async def get_images(keyword: str | None=Query(max_length=25, default=None),
                     order_by: OrderBy=None,
                     offset: int=0, limit: int=100,
                     user: User=Depends(get_current_user), 
                     db: Session=Depends(get_db)):
    """
    The get_images function returns a list of images.
    
    :param keyword: str | None: Filter the images by keyword
    :param default: Set a default value for the parameter
    :param order_by: OrderBy: Specify the order in which to return images
    :param offset: int: Skip the first n images
    :param limit: int: Limit the number of images returned
    :param user: User: Get the user's id from the database
    :param db: Session: Pass the database session to the imagesrepo class
    :return: A list of images objects
    :doc-author: Trelent
    """
    images = await ImagesRepo(user, db).get_many(offset=offset,
                                                 limit=limit,
                                                 order_by=order_by,
                                                 keyword=keyword,
                                                )
    return images


@router.post('/', response_model=ImageCreateResponseModel, status_code=status.HTTP_201_CREATED)
async def create_image(image_form: ImageCreate=Depends(ImageCreate.as_form),
                        user: User=Depends(get_current_user),
                        db: Session=Depends(get_db)):
    """
    The create_image function creates a new image in the database.
        It takes an ImageCreate form, which contains a file and description, 
        as well as tags for the image. The function then uses these values to create 
        an Image object and store it in the database.
    
    :param image_form: ImageCreate: Validate the request body
    :param user: User: Get the current user
    :param db: Session: Pass the database session to the repository
    :return: A tuple of the image and a list of tags
    :doc-author: Trelent
    """
    tags = await TagsRepo(db).get_or_create_many(image_form.tags)

    image = await ImagesRepo(user, db).create(image_form.file.file, 
                                              image_form.description, 
                                              tags)
    return image


@router.get("/{image_id}", response_model=ImageResponseModel)
async def get_image(image_id: int, 
                    user: User=Depends(get_current_user),
                    db: Session=Depends(get_db)):
    """
    The get_image function returns a single image from the database.
        The function takes an integer as an argument, which is the id of the image to be returned.
        If no such image exists in the database, then a 404 error is raised.
    
    :param image_id: int: Get the image with that id from the database
    :param user: User: Get the user from the token
    :param db: Session: Pass the database session to the function
    :return: An image object, which is a named tuple
    :doc-author: Trelent
    """
    image = await ImagesRepo(user, db).get_single(image_id)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.put('/{image_id}', response_model=ImageResponseModel, dependencies=[Depends(allowed_action),])
async def update_image(body: ImageUpdate, 
                       image_id: int, 
                       user: User=Depends(get_current_user),
                       db: Session=Depends(get_db)):
    """
    The update_image_description function updates the description of an image.
        
        Args:
            body (ImageUpdate): The new description and tags for the image.
            image_id (int): The ID of the image to update.
            user (User, optional): The current user making this request, if any. Defaults to Depends(get_current_user).
            db (Session, optional): A database session object used for querying data from a database and committing changes made by this function back into it. Defaults to Depends(get_db).  # noQA
    
    :param body: ImageUpdate: Get the image description and tags from the request body
    :param image_id: int: Specify the image to update
    :param user: User: Get the current user
    :param db: Session: Pass in the database session to the imagesrepo class
    :return: A image object
    """
    body.tags = await TagsRepo(db).get_or_create_many(body.tags)
    image = await ImagesRepo(user, db).update(image_id, body)
    
    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.delete('/{image_id}', response_model=ImageResponseModel, dependencies=[Depends(allowed_action),])
async def delete_image(image_id: int, 
                       user: User=Depends(get_current_user),
                       db: Session=Depends(get_db),
                       ):
    """
    The delete_image function deletes an image from the database.
    
    :param image_id: int: Identify the image to be deleted
    :param user: User: Get the user object from the database
    :param db: Session: Pass in the database session to the function
    :param: Get the image id from the url
    :return: The image that was deleted
    """
    image = await ImagesRepo(user, db).delete(image_id)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")
    
    return image


@router.post('/{image_id}/transform', response_model=ImageResponseModel)
async def transform_image(image_id: int, 
                          transform_model: ImageTransfornModel,
                          user: User=Depends(get_current_user),
                          db: Session=Depends(get_db)):
    """
    The transform_image function transforms an image by applying a transformation model to it.
        The function takes in the following parameters:
            - image_id: The id of the image to be transformed.
            - transform_model: A JSON object containing information about how to transform the image. 
                This includes information such as which transformation algorithm should be used, and what 
                parameters should be passed into that algorithm (e.g., if we are using a Gaussian blur, then 
                this would include information about what sigma value should be used).
    
    :param image_id: int: Identify the image to be transformed
    :param transform_model: ImageTransfornModel: Pass the transformation model to the function
    :param user: User: Get the user from the token
    :param db: Session: Get access to the database
    :return: An image object
    :doc-author: Trelent
    """
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
    """
    The share_image function is used to generate a QR code that can be scanned by another user.
    The QR code contains the URL of the image, which will allow them to view it without having an account.
    
    :param image_id: int: Get the image from the database
    :param request: Request: Get the base url of the request
    :param user: User: Get the user from the database
    :param db: Session: Get the database session from the dependency injection container
    :return: A streamingresponse object, which is a subclass of response
    :doc-author: Trelent
    """
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
    """
    The get_shared_image function is used to retrieve an image from the database using its identifier.
    
    :param identifier: str: Identify the image that is being requested
    :param db: Session: Pass the database session to the imagesrepo class
    :return: An image object
    :doc-author: Trelent
    """
    image = await ImagesRepo(None, db).identify(identifier)

    if image is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Image not found!")

    return image
