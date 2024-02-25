import unittest
from unittest.mock import MagicMock

from src.repository.base_repository import AbstractRepository


class FakeRepository(AbstractRepository):

    async def create(self, **kwargs):
        return await super().create(**kwargs)
    
    async def update(self, **kwargs):
        return await super().update(**kwargs)
    
    async def delete(self, **kwargs):
        return await super().delete(**kwargs)
    
    async def get_single(self, **kwargs):
        return await super().get_single(**kwargs)
    

class TestAbstractRepository(unittest.IsolatedAsyncioTestCase):

    async def test_create(self):
        with self.assertRaises(NotImplementedError) as err:
            await FakeRepository(MagicMock()).create()

    async def test_update(self):
        with self.assertRaises(NotImplementedError) as err:
            await FakeRepository(MagicMock()).update()

    async def test_delete(self):
        with self.assertRaises(NotImplementedError) as err:
            await FakeRepository(MagicMock()).delete()

    async def test_get_single(self):
        with self.assertRaises(NotImplementedError) as err:
            await FakeRepository(MagicMock()).get_single()


if __name__ == '__main__':
    unittest.main()