from sqlalchemy.orm import Session

from ..models.image import Tag, Image
from .base_repository import AbstractRepository


class Tags(AbstractRepository):
    model = Tag

    async def create(self, name) -> Tag:
        tag = await self.get_single(name)

        if tag:
            return None
        
        tag = self.model(name=name)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)

        return tag
    

    async def delete(self, name) -> Tag:
        tag = await self.get_single(name)

        if not tag:
            return None
        
        self.db.delete(tag)
        self.db.commit()

        return tag
    

    async def update(self, **kwargs):
        raise NotImplementedError
    

    async def get_many(self, names: [str]) -> [Tag]:
        tags = self.db.query(self.model).filter(self.model.name.in_(names)).all()

        return tags
    

    async def get_single(self, name: str) -> Tag:
        tag = self.db.query(self.model).filter(self.model.name == name).first()

        return tag
    

    async def get_or_create_single(self, name: str) -> Tag:
        tag = await self.get_single(name) 
        if tag is None:
            tag = await self.create(name)

        return tag
    
    
    async def get_or_create_many(self, names: [str]) -> [Tag]:
        tags = []
        for name in names:
            tag = await self.get_or_create_single(name)
            tags.append(tag)

        return tags