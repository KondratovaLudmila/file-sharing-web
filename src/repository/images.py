from sqlalchemy.orm import Session
from sqlalchemy import update
from uuid import uuid4

from .base_repository import AbstractRepository
from ..models.image import Image
from ..models.user import User
from ..schemas.image import ImageDescriptionUpdate
from ..services.media_storage import storage


class Images(AbstractRepository):
    model = Image
    
    def __init__(self, user: User, db: Session) -> None:
        self.user = user
        super().__init__(db)
        

    async def create(self, file: str, description: str) -> Image:
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
        image = self.model(user=self.user, url=img.url, identifier=identifier, description=description)

        self.db.add(image)
        self.db.commit()
        self.db.refresh(image)

        return image
    

    async def update(self, pk: int, image_model: ImageDescriptionUpdate):
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
        
        image.description = image_model.description
        self.db.commit()

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
        
        self.db.delete(image)
        self.db.commit()

        public_id = storage.get_public_id(self.user.username, image.identifier)
        await storage.remove_media(public_id)

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
        if not image or image.user != self.user:
            return None
        
        return image
    

    async def get_many(self):
        """
        The get_many function returns all images associated with a user.
            
        
        :param self: Represent the instance of the class
        :return: A list of objects
        :doc-author: Trelent
        """
        images = self.db.query(self.model).filter(self.model.user==self.user).all()

        return images
    

        


        