from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc, or_
from uuid import uuid4

from .base_repository import AbstractRepository
from .tags import Tags
from ..models.image import Image, Tag
from ..models.user import User
from ..schemas.image import ImageUpdate, ImageTransfornModel, OrderBy
from ..services.media_storage import storage


class Images(AbstractRepository):
    model = Image
    
    def __init__(self, user: User, db: Session) -> None:
        self.user = user
        super().__init__(db)
        

    async def create(self, file: str, description: str, tags: [Tag]) -> Image:
        """
        The create function creates a new image for the user.
        
        :param self: Represent the instance of the class
        :param file: str: Get the file from the request
        :param description: str: Add a description to the image
        :return: An image object
        """
        
        identifier = uuid4().hex
        public_id = storage.get_public_id(self.user.username, identifier)
        img = await storage.user_image_upload(file, public_id)
        image = self.model(user=self.user, 
                           url=img.url, 
                           identifier=identifier, 
                           description=description, 
                           tags=tags)

        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)

        return image
    

    async def update(self, pk: int, image_model: ImageUpdate):
        """
        The update method updates image filds.
        
        :param self: Represent the instance of the class
        :param pk: int: Specify the primary key of the image to be deleted
        :param image_model: ImageDescriptionUpdate: Values to update image
        :return: The updated image object
        """
        
        image = await self.get_single(pk)

        if not image:
            return None
        tags = image.tags
        image.description = image_model.description
        image.tags = image_model.tags
        self.db.commit()

        await Tags(self.db).delete_unused(tags)
        
        return image


    async def delete(self, pk: int) -> Image:
        """
        The delete mathod deletes an image from the database and from storage.
        
        :param self: Reference the class itself
        :param pk: int: Specify the primary key of the image to be deleted
        :return: The deleted image
        :doc-author: Trelent
        """
        
        image = await self.get_single(pk)

        if not image:
            return None
        
        tags = image.tags
        self.db.delete(image)
        self.db.commit()

        public_id = storage.get_public_id(self.user.username, image.identifier)
        await storage.remove_media(public_id)
        await Tags(self.db).delete_unused(tags)

        return image


    async def get_single(self, pk: int) -> Image:
        """
        This method is used to retrieve a single image from the database.
        The function takes in an integer primary key and returns an Image object.
        
        :param self: Represent the instance of a class
        :param pk: int: Get the image with a specific id
        :return: The image if it exists and is owned by the user. Otherwise None
        """
        
        image = self.db.get(self.model, pk)
        
        return image


    async def get_many(self, offset: int, limit: int, order_by: str, keyword: str, **filters):
        """
        The get_many function is used to retrieve a list of images from the database.
        The function takes in an offset, limit, order_by and keyword as parameters.
        It also takes in filters which are passed into the filter_by method of SQLAlchemy's query object.
        If there is a keyword provided then it will join on tags and search for that keyword within both the description field 
        and tag name field of each image record. If there is an order by parameter then it will sort by that column either ascending or descending depending on what was specified after the column name (i.e &quot;id desc&quot;). Finally if all these conditions
        
        :param self: Access the attributes and methods of the class
        :param offset: int: Specify the offset of the first row to return
        :param limit: int: Limit the number of results returned
        :param order_by: str: Sort the images by a certain field
        :param keyword: str: Search for images by description or tag name
        :param filters: Filter the images by tag
        :return: A list of images from the database
        :doc-author: Trelent
        """
        images = self.db.query(self.model)
        if filters:
            images = images.filter_by(**filters)
        if keyword:
            images = images.join(Tag, self.model.tags, isouter=True)
            images = images.filter(or_(self.model.description.like(f'%{keyword}%'), Tag.name.like(f'%{keyword}%')))
        if order_by:
            field, order = order_by.split()
            if order=="desc":
                images = images.order_by(getattr(self.model, field).desc())
            else:
                images = images.order_by(getattr(self.model, field))

        images = images.group_by(self.model.id).offset(offset).limit(limit).all()

        return images
    

    async def transform(self, pk: int, transform_model: ImageTransfornModel):
        """
        The transform function takes an image and applies a transformation to it.
        
        :param self: Refer to the class instance itself
        :param pk: int: Get the image from the database
        :param transform_model: ImageTransfornModel: Pass in the model that is used to transform the image
        :return: The transformed image
        """
        
        image = await self.get_single(pk)

        if not image:
            return None
        
        identifier = uuid4().hex
        public_id = storage.get_public_id(self.user.username, identifier)
        
        try:
            img = await storage.image_transform(image.url, transform_model.model_dump(), public_id)
            transformed_image = self.model(user=self.user, 
                                       url=img.url, 
                                       identifier=identifier, 
                                       description=image.description)
            self.db.add(transformed_image)
            self.db.commit()
            self.db.refresh(transformed_image)
        
        except Exception as err:
            raise HTTPException(status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(err))

        return transformed_image


    async def identify(self, identifier: str) -> Image | None:
        """
        The identify function is used to identify an image by its identifier.
                
        
        :param self: Represent the instance of the class
        :param identifier: str: Identify the image
        :return: An image object or none if no image is found
        """
        image = self.db.query(self.model).filter(self.model.identifier==identifier).first()

        return image

        
        

        

    

        


        