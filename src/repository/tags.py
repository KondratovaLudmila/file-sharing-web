from sqlalchemy.orm import Session

from ..models.image import Tag, Image
from .base_repository import AbstractRepository


class Tags(AbstractRepository):
    model = Tag

    async def create(self, name) -> Tag:
        
        """
        The create function creates a new tag in the database.
            Args:
                name (str): The name of the tag to be created.
        
        :param self: Represent the instance of the class
        :param name: Create a new tag with the name of the parameter
        :return: A tag object
        """
        tag = await self.get_single(name)

        if tag:
            return None
        
        tag = self.model(name=name)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        return tag
    

    async def delete(self, name) -> Tag:
        """
        The delete function deletes a tag from the database.
                Args:
                    name (str): The name of the tag to delete.
        
        :param self: Represent the instance of the class
        :param name: Get the tag to delete
        :return: A tag object, but the get_single function returns a query
        :doc-author: Trelent
        """
        tag = await self.get_single(name)

        if not tag:
            return None
        
        self.db.delete(tag)
        self.db.commit()

        return tag
    

    async def update(self, **kwargs):
        """Not implemented method in case tag update forbiden"""
        raise NotImplementedError
    

    async def get_many(self, names: [str]) -> [Tag]:
        """
        The get_many function takes a list of names and returns a list of Tag objects.
            The function uses the SQLAlchemy query method to filter the database for all tags with names in the given list.
            It then returns those tags as a Python object.
        
        :param self: Represent the instance of the class
        :param names: [str]: Specify the type of data that is going to be passed into the function
        :return: A list of tag objects
        """
        tags = self.db.query(self.model).filter(self.model.name.in_(names)).all()

        return tags
    

    async def get_single(self, name: str) -> Tag:
        """
        The get_single function is used to retrieve a single tag from the database.
            It takes in a name parameter and returns the first tag that matches that name.
        
        :param self: Represent the instance of the class
        :param name: str: Pass the name of the tag to be retrieved
        :return: A tag object
        :doc-author: Trelent
        """
        tag = self.db.query(self.model).filter(self.model.name == name).first()

        return tag
    

    async def get_or_create_single(self, name: str) -> Tag:
        """
        The get_or_create_single function will return a tag if it exists, or create one if it doesn't.
            This is useful for when you want to ensure that a tag exists before using it.
        
        :param self: Represent the instance of the class
        :param name: str: Get the name of the tag
        :return: A tag
        """
        tag = await self.get_single(name) 
        if tag is None:
            tag = await self.create(name)

        return tag
    
    
    async def get_or_create_many(self, names: [str]) -> [Tag]:
        """
        The get_or_create_many function takes a list of strings and returns a list of Tag objects.
        If the tag does not exist, it is created. If it exists, then the existing tag is returned.
        
        :param self: Represent the instance of the class
        :param names: [str]: Specify that the names parameter is a list of strings
        :return: A list of tag objects
        """
        tags = []
        for name in names:
            tag = await self.get_or_create_single(name)
            tags.append(tag)

        return tags
    

    async def delete_unused(self, tags: [Tag]) -> None:
        """
        The delete_unused function deletes tags that are no longer used by any images.
        
        :param self: Access the current instance of the class
        :param tags: [Tag]: Pass in a list of tags
        :return: Nothing
        :doc-author: Trelent
        """
        for tag in tags:
            self.db.refresh(tag)
            if tag.images:
                continue
            
            await self.delete(tag.name)