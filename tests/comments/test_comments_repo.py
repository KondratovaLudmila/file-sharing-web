import asyncio
import unittest
from unittest.mock import MagicMock
from sqlalchemy.orm import Session

from src.models.comment import Comment
from src.models.user import User, Role
from src.repository.comments import CommentsRepo
from src.models.image import Image

fake_user_data = {"id": 1, "username": "testuser", "email": "test@example.com", "role": Role.user}
fake_comment_data = {"id": 1, "body": "Test comment", "image_id": 1, "user_id": 1}
fake_image_data = {"id": 1, "url": "www.ttt.com/folder/image.jpeg", "description": "A sample image", "user_id": 1}


class TestCommentsRepo(unittest.IsolatedAsyncioTestCase):

    async def asyncSetUp(self):
        self.mock_session = MagicMock(spec=Session)
        self.mock_user = User(**fake_user_data)
        self.mock_comment = Comment(**fake_comment_data)
        self.mock_image = Image(**fake_image_data)
        self.comments_repo = CommentsRepo(self.mock_user, self.mock_session)

    async def test_create_comment(self):
        result = await self.comments_repo.create(
            body=fake_comment_data['body'],
            image_id=fake_comment_data['image_id'],
            user_id=self.mock_user.id
        )
        self.assertEqual(result.body, self.mock_comment.body)
        self.assertEqual(result.image_id, self.mock_comment.image_id)
        self.assertEqual(result.user_id, self.mock_comment.user_id)

    async def test_get_comment(self):
        self.mock_session.query().filter().first.return_value = self.mock_comment

        result = await self.comments_repo.get_single(self.mock_image.id, self.mock_comment.id)

        self.assertEqual(result.id, self.mock_comment.id)

    async def test_update_comment(self):
        updated_body = "Updated test comment"
        self.mock_session.query().filter().first.return_value = self.mock_comment

        result = await self.comments_repo.update(self.mock_image.id, self.mock_comment.id, updated_body)

        self.assertEqual(result.body, updated_body)
        self.mock_session.commit.assert_called_once()

    async def test_delete_comment(self):
        self.mock_session.query().filter().first.return_value = self.mock_comment

        result = await self.comments_repo.delete(self.mock_image.id, self.mock_comment.id)

        self.assertTrue(result)
        self.mock_session.delete.assert_called_once_with(self.mock_comment)
        self.mock_session.commit.assert_called_once()

    async def test_get_many_comments(self):
        self.mock_session.query().filter().all.return_value = [self.mock_comment]

        result = await self.comments_repo.get_many(self.mock_image.id)

        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, fake_comment_data['id'])

    async def test_can_edit_comment(self):
        result = await self.comments_repo.can_edit_comment(self.mock_user, self.mock_comment)
        self.assertTrue(result)

        another_user = User(**{**fake_user_data, "id": 2})
        result = await self.comments_repo.can_edit_comment(another_user, self.mock_comment)
        self.assertFalse(result)

    async def test_can_delete_comment(self):
        admin_user = User(**{**fake_user_data, "role": Role.admin})
        result = await self.comments_repo.can_delete_comment(admin_user)
        self.assertTrue(result)

        moderator_user = User(**{**fake_user_data, "role": Role.moderator})
        result = await self.comments_repo.can_delete_comment(moderator_user)
        self.assertTrue(result)

        user = User(**{**fake_user_data, "role": Role.user})
        result = await self.comments_repo.can_delete_comment(user)
        self.assertFalse(result)


if __name__ == '__main__':
    asyncio.run(unittest.main())
