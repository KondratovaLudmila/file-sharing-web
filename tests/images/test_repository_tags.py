import unittest
import os
import dotenv
from unittest.mock import MagicMock, patch
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from src.repository.tags import Tags, Tag
from src.dependencies.db import Base
from src.repository.images import Images


dotenv.load_dotenv()

user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{user}:{password}@localhost:{port}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class TestTags(unittest.IsolatedAsyncioTestCase):
    @classmethod
    def setUpClass(cls) -> None:
        Base.metadata.create_all(bind=engine)
        

    @classmethod
    def tearDownClass(cls) -> None:
        Base.metadata.drop_all(bind=engine)


    def setUp(self) -> None:
        self.db = TestingSessionLocal()


    def tearDown(self) -> None:
        self.db.close()


    async def test_tag_create(self):
        name = "tag1"
        tag = await Tags(self.db).create(name)

        self.assertEqual(tag.name, name)
        self.assertIsNotNone(tag.id)


    async def test_tag_create_wrong(self):
        name = "tag1"
        if self.db.get(Tag, 1) is None:
            await Tags(self.db).create(name)
        tag2 = await Tags(self.db).create(name)

        self.assertIsNone(tag2)


    async def test_tag_update(self):
        with self.assertRaises(NotImplementedError) as err:
            await Tags(self.db).update()


    async def test_tag_delete(self):
        name = "tag1"
        if self.db.get(Tag, 1) is None:
            await Tags(self.db).create(name)

        tag = await Tags(self.db).delete(name)

        self.assertEqual(tag.name, name)


    async def test_tag_delete_wrong(self):
        name = "abracadabra"
        tag = await Tags(self.db).delete(name)

        self.assertIsNone(tag)


    async def test_tag_get_single_wrong(self):
        name = "abracadabra"
        tag = await Tags(self.db).get_single(name)

        self.assertIsNone(tag)


    async def test_tag_get_or_create_single_get(self):
        name = "tag1"
        test_tag = self.db.query(Tag).filter(Tag.name==name).first()
        if test_tag is None:
            test_tag = await Tags(self.db).create(name)

        tag = await Tags(self.db).get_or_create_single(name)

        self.assertEqual(tag.id, test_tag.id)


    async def test_tag_get_or_create_single_create(self):
        name = "tag2"

        tag = await Tags(self.db).get_or_create_single(name)

        self.assertEqual(tag.name, name)


    async def test_tag_get_or_create_many(self):
        names = ["tag1", "tag101"]
        test_tag = self.db.query(Tag).filter(Tag.name==names[0]).first()
        if test_tag is None:
            test_tag = await Tags(self.db).create(names[0])

        tags = await Tags(self.db).get_or_create_many(names)

        self.assertEqual(tags[0].id, test_tag.id)
        self.assertEqual(tags[1].name, names[1])


    async def test_tag_get_many(self):
        names = ["tag1", "tag101"]
        test_tags = []
        for name in names:
            test_tag = self.db.query(Tag).filter(Tag.name==name).first()
            if test_tag is None:
                test_tag = await Tags(self.db).create(name)

            test_tags.append(test_tag)

        tags = await Tags(self.db).get_many(names)

        self.assertEqual(tags[0].id, test_tags[0].id)
        self.assertEqual(tags[1].id, test_tags[1].id)


    async def test_tag_delete_unused(self):
        names = ["tag1", "tag101"]
        test_tags = []
        for name in names:
            test_tag = self.db.query(Tag).filter(Tag.name==name).first()
            if test_tag is None:
                test_tag = await Tags(self.db).create(name)
            
            test_tags.append(test_tag)

        await Tags(self.db).delete_unused(test_tags)

        tags = await Tags(self.db).get_many(names)

        self.assertEqual(tags, [])
    

if __name__ == '__main__':
    unittest.main()

