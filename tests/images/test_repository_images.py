from collections.abc import Callable
from typing import Any
import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from src.models.user import User
from src.models.image import Image
from src.dependencies.db import Base
from src.repository.images import Images
from src.schemas.image import OrderBy

import os
import dotenv

dotenv.load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
#SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/tests"
SQLALCHEMY_DATABASE_URL="sqlite://"

engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


fake_user = {"username": "user", "email": "user@gmail.com", "password": "password"}
fake_image = {"url": "www.ttt.com/folder/image.jpeg", "description": "my_desk", "tags": [], "user_id": 1}
fake_image2 = {"url": "www.ttt.com/folder/image2.jpeg", "description": "my_desk", "tags": [], "user_id": 1}


class TestImagesRepository(unittest.IsolatedAsyncioTestCase):

    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)
        

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(bind=engine)


    def setUp(self) -> None:
        self.db = TestingSessionLocal()
        self.user = self.db.get(User, 1)
        if self.user is None:
            self.user = User(**fake_user)
            self.db.add(self.user)
            self.db.commit()
            self.db.refresh(self.user)


    def tearDown(self) -> None:
        self.db.close()

    
    @patch('src.services.media_storage.storage.user_image_upload')
    async def test_image_create(self, mock_upload):
        mock_upload.return_value = MagicMock(**fake_image)
        image = await Images(self.user, self.db).create(MagicMock(), fake_image["description"], fake_image["tags"])
        self.assertEqual(image.url, fake_image["url"])


    @patch('src.services.media_storage.storage.remove_media')
    async def test_image_delete(self, mock_drop):
        mock_drop.return_value = {}
        img = Image(**fake_image)
        self.db.add(img)
        self.db.commit()
        self.db.refresh(img)

        image = await Images(self.user, self.db).delete(img.id)
        self.assertIsNone(self.db.get(Image, img.id))
        self.assertEqual(image.id, img.id)

    
    async def test_image_delete_wrong(self):
        pk = 100
        image = await Images(self.user, self.db).delete(pk)

        self.assertIsNone(image)


    async def test_image_update(self):
        mock_model = MagicMock(description="new_desc", tags=[])
        img = Image(**fake_image)
        self.db.add(img)
        self.db.commit()
        self.db.refresh(img)

        image = await Images(self.user, self.db).update(img.id, mock_model)
        self.assertEqual(image.description, mock_model.description)
        self.assertEqual(image.id, img.id)


    async def test_image_update_wrong(self):
        mock_model = MagicMock(description="new_desc", tags=[])
        pk = 100

        image = await Images(self.user, self.db).update(pk, mock_model)
        self.assertIsNone(image)


    async def test_image_get_single(self):
        image = await Images(self.user, self.db).get_single(1)

        self.assertEqual(fake_image["description"], image.description)
        self.assertEqual(fake_image["url"], image.url)
        self.assertEqual(fake_image["user_id"], image.user_id)


    async def test_image_get_many(self):
        images = await Images(self.user, self.db).get_many(0, 100, 
                                                           order_by=OrderBy.created_at_desc.value,
                                                           keyword=fake_image["description"], 
                                                           url=fake_image["url"],
                                                           )

        self.assertEqual(fake_image["description"], images[0].description)
        self.assertEqual(fake_image["url"], images[0].url)


    @patch("src.services.media_storage.storage.image_transform")
    @patch("src.schemas.image.ImageTransfornModel")
    async def test_image_transform(self, transform_mock, mock_upload):
        mock_upload.return_value = MagicMock(**fake_image2)
        transform = transform_mock()
        transform.model_dump.return_value = {"effect": "sepia"}

        img = self.db.get(Image, 1)

        image = await Images(self.user, self.db).transform(img.id, transform)

        self.assertNotEqual(image.id, img.id)
        self.assertEqual(image.description, img.description)


    async def test_image_transform_wrong(self):
        pk = 100
        image = await Images(self.user, self.db).transform(pk, MagicMock())

        self.assertIsNone(image)


    @patch("src.schemas.image.ImageTransfornModel")
    async def test_image_transform_err(self, trans_mock):
        transform = trans_mock()
        transform.model_dump.return_value = {"effect": "sepia"}

        img = self.db.get(Image, 1)
        with self.assertRaises(HTTPException) as err:
            image = await Images(self.user, self.db).transform(img.id, transform)


    async def test_image_identify(self):
        img = self.db.get(Image, 1)

        image = await Images(self.user, self.db).identify(img.identifier)

        self.assertEqual(img.id, image.id)
        


if __name__ == '__main__':
    unittest.main()