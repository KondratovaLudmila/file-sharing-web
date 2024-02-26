import unittest
from unittest.mock import MagicMock, patch
from fastapi import HTTPException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models.user import User, Role
from src.repository.images import Images, Image
from src.dependencies.db import Base
from src.dependencies.roles import RoleAccess, OwnerRoleAccess

import os
import dotenv

dotenv.load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

fake_user = {"username": "user", "email": "user@gmail.com", "password": "password", "role": Role.user}
fake_admin = {"username": "admin", "email": "admin@gmail.com", "password": "password", "role": Role.admin}
fake_image = {"url": "www.ttt.com/folder/image.jpeg", "description": "my_desk", "user_id": 1}

class TestRoleAccess(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)
        

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(bind=engine)


    def setUp(self) -> None:
        self.db = TestingSessionLocal()
        self.user = self.db.get(User, 1)
        self.admin = self.db.get(User, 2)
        self.image = self.db.get(Image, 1)

        if self.user is None:
            self.user = User(**fake_user)
            self.admin = User(**fake_admin)
            self.image = Image(**fake_image)
            self.db.add(self.user)
            self.db.add(self.admin)
            self.db.add(self.image)
            self.db.commit()
            self.db.refresh(self.user)
            self.db.refresh(self.admin)

    def tearDown(self) -> None:
        self.db.close()


    async def test_role_permited(self):
        result = RoleAccess([Role.admin,])(MagicMock(), user=self.admin)

        self.assertEqual(result, True)

    
    async def test_role_denied(self):
        with self.assertRaises(HTTPException):
            RoleAccess([Role.admin,])(MagicMock(), user=self.user)


    async def test_resourse_owner_permited(self):
        image_id = 1
        result = await OwnerRoleAccess([Role.admin,], 
                                 repository=Images, 
                                 param_name="image_id")(MagicMock(path_params={"image_id": image_id}),
                                                        user=self.admin,
                                                        db=self.db)
        
        self.assertEqual(result, True)


    async def test_resource_owner_denied(self):
        image_id = 1
        with self.assertRaises(HTTPException) as err:
            await OwnerRoleAccess([Role.moderator,],
                                 repository=Images, 
                                 param_name="image_id")(MagicMock(path_params={"image_id": image_id}),
                                                        user=self.admin,
                                                        db=self.db) 

    async def test_resource_owner_wrong(self):
        with self.assertRaises(HTTPException) as err:
            result = await OwnerRoleAccess([Role.moderator,],
                                            repository=Images, 
                                            param_name="image_id")(MagicMock(),
                                                                user=self.user,
                                                                db=self.db)
        
    

if __name__ == "__main__":
    unittest.main()