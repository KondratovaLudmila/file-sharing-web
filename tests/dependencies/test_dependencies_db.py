import unittest
from fastapi import Depends
from sqlalchemy import text

from src.dependencies.db import get_db, session
from src.models.image import Tag

class TestDB(unittest.IsolatedAsyncioTestCase):
    
    async def test_connection(self):
        db = next(get_db())
        
        result = db.execute(text('SELECT 1')).fetchone()
        self.assertIsNotNone(result)


    async def test_connection_err(self):
        with session() as s:
            s.add(Tag("name"))
            s.commit()

            


if __name__ == '__main__':
    unittest.main()