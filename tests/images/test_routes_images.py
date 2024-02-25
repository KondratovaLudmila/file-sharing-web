import unittest
import os
from unittest.mock import patch
import dotenv
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from main import app
from src.dependencies.db import Base
from src.models.user import User
from src.models.image import Image

dotenv.load_dotenv()

pg_user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{pg_user}:{password}@localhost:{port}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake_user = {"username": "user", "email": "user@gmail.com", "password": "password"}
fake_image = {"url": "www.ttt.com/folder/image.jpeg", "description": "my_desk",  "user_id": 1}
fake_image2 = {"url": "www.ttt.com/folder/image2.jpeg", "description": "my_desk", "user_id": 1}


class TestImagesRoutes(unittest.IsolatedAsyncioTestCase):
    client = TestClient(app)

    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)
        

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(bind=engine)


    def setUp(self) -> None:
        self.db = TestingSessionLocal()
        self.user = self.db.get(User, 1)
        self.image1 = self.db.get(Image, 1)
        self.image2 = self.db.get(Image, 2)

        if self.user is None:
            self.user = User(**fake_user)
            self.image1 = Image(**fake_image)
            self.image2 = Image(**fake_image2)

            self.db.add_all(self.user, self.image1, self.image2)
            self.db.commit()
            self.db.refresh(self.user)
            self.db.refresh(self.image1)
            self.db.refresh(self.image2)


    def tearDown(self) -> None:
        self.db.close()

    
    @patch("src.routes.ImageRepo")
    async def test_route_create_image(self, image_repo):
        image_repo.create.return_value = self.image1
        
        response = self.client.post("/images", json=self.image1)



if __name__ == '__main__':
    unittest.main()
