import asyncio
import unittest
from unittest.mock import patch, AsyncMock

from src.models.comment import Comment
from src.models.user import User, Role
from src.repository.comments import CommentsRepo
from src.models.image import Image

fake_user_data = {"id": 1, "username": "testuser", "email": "test@example.com", "role": Role.user}
fake_comment_data = {"id": 1, "body": "Test comment", "image_id": 1, "user_id": 1}
fake_image_data = {"id": 1, "url": "www.ttt.com/folder/image.jpeg", "description": "A sample image", "user_id": 1}

class TestCommentsRepo(unittest.IsolatedAsyncioTestCase):
    
    async def asyncSetUp(self):
        # Налаштування мокованих об'єктів
        self.mock_async_session = AsyncMock()
        self.mock_user = User(**fake_user_data)
        self.mock_comment = Comment(**fake_comment_data)
        self.mock_image = Image(**fake_image_data)
        
        # Створення екземпляру CommentsRepo з мокованою сесією
        self.comments_repo = CommentsRepo(self.mock_user, self.mock_async_session)

    @patch('src.repository.comments.CommentsRepo.create')
    async def test_create_comment(self, mock_create):
        mock_create.return_value = self.mock_comment
        result = await self.comments_repo.create(body=fake_comment_data['body'], image_id=fake_comment_data['image_id'])
        self.assertEqual(result.body, fake_comment_data['body'])
        mock_create.assert_awaited_once()

    @patch('src.repository.comments.CommentsRepo.get_single')
    async def test_get_comment(self, mock_get_single):
        mock_get_single.return_value = self.mock_comment
        result = await self.comments_repo.get_single(comment_id=fake_comment_data['id'])
        self.assertEqual(result.id, fake_comment_data['id'])
        mock_get_single.assert_awaited_once()

    @patch('src.repository.comments.CommentsRepo.update')
    async def test_update_comment(self, mock_update):
        updated_body = "Updated test comment"
        mock_update.return_value = Comment(**{**fake_comment_data, "body": updated_body})
        result = await self.comments_repo.update(comment_id=fake_comment_data['id'], body=updated_body)
        self.assertEqual(result.body, updated_body)
        mock_update.assert_awaited_once()

    @patch('src.repository.comments.CommentsRepo.delete')
    async def test_delete_comment(self, mock_delete):
        mock_delete.return_value = True
        result = await self.comments_repo.delete(comment_id=fake_comment_data['id'])
        self.assertTrue(result)
        mock_delete.assert_awaited_once()

    @patch('src.repository.comments.CommentsRepo.get_many')
    async def test_get_many_comments(self, mock_get_many):
        mock_get_many.return_value = [self.mock_comment]
        result = await self.comments_repo.get_many(image_id=fake_comment_data['image_id'])
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, fake_comment_data['id'])
        mock_get_many.assert_awaited_once()

    @patch('src.repository.comments.CommentsRepo.can_edit_comment')
    async def test_can_edit_comment(self, mock_can_edit):
        # Сценарій, коли користувач є автором коментаря
        mock_can_edit.return_value = True
        result = await self.comments_repo.can_edit_comment(self.mock_user, self.mock_comment)
        self.assertTrue(result)
        mock_can_edit.assert_awaited_once_with(self.mock_user, self.mock_comment)

        # Сценарій, коли користувач не є автором коментаря
        mock_can_edit.return_value = False
        another_user = User(**{**fake_user_data, "id": 2})
        result = await self.comments_repo.can_edit_comment(another_user, self.mock_comment)
        self.assertFalse(result)
        mock_can_edit.assert_awaited_with(another_user, self.mock_comment)

    @patch('src.repository.comments.CommentsRepo.can_delete_comment')
    async def test_can_delete_comment(self, mock_can_delete):
        # Сценарій, коли користувач є адміністратором
        admin_user = User(**{**fake_user_data, "role": Role.admin})
        mock_can_delete.return_value = True
        result = await self.comments_repo.can_delete_comment(admin_user)
        self.assertTrue(result)
        mock_can_delete.assert_awaited_once_with(admin_user)

        # Сценарій, коли користувач є звичайним користувачем
        user = User(**{**fake_user_data, "role": Role.user})
        mock_can_delete.return_value = False
        result = await self.comments_repo.can_delete_comment(user)
        self.assertFalse(result)
        mock_can_delete.assert_awaited_with(user)



if __name__ == '__main__':
    asyncio.run(unittest.main())
