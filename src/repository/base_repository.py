from abc import ABC, abstractmethod
from sqlalchemy.orm import Session


class AbstractRepository(ABC):
    model = None

    def __init__(self, db: Session) -> None:
        self.db = db

    @abstractmethod
    async def create(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def update(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def delete(self, **kwargs):
        raise NotImplementedError

    @abstractmethod
    async def get_single(self, **kwargs):
        raise NotImplementedError