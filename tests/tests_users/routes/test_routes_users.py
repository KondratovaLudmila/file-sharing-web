import tracemalloc
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from src.repository.users import UserRepository
from src.schemas.user import UserResponse
from src.models.user import User
from sqlalchemy.orm import Session
from src.routes.users import get_users, update_user, delete_user, get_user, get_user_by_username, ban_user, \
    change_user_role
from fastapi.datastructures import UploadFile
from src.models.user import Role


class TestRoutes(unittest.IsolatedAsyncioTestCase):

    async def test_get_users(self):
        tracemalloc.start()
        db_mock = MagicMock()
        user_repo_mock = UserRepository(db_mock)
        users_data = [
            {"id": 1, "username": "user1", "email": "user1@example.com", "role": "user"},
            {"id": 2, "username": "user2", "email": "user2@example.com", "role": "admin"}
        ]
        user_repo_mock.get_many = MagicMock(return_value=[
            UserResponse(**user_data) for user_data in users_data
        ])
        db_mock.query.return_value.filter.return_value.all.return_value = user_repo_mock.get_many()

        users = await get_users(query="test", db=db_mock)
        self.assertEqual(len(users), 2)
        self.assertEqual(users[0].username, "user1")
        self.assertEqual(users[1].username, "user2")
        tracemalloc.stop()

    async def test_update_user_avatar(self):
        # Mocking objects and preparing test data
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)

        # Creating a real User object
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)

        # Mocking the avatar_upload function
        avatar_url = 'https://example.com/avatar.jpg'
        avatar_data = MagicMock(file=b"123")
        with patch('src.repository.users.storage.avatar_upload') as avatar_upload_mock:
            # Mocking the return value of the avatar_upload function
            avatar_upload_mock.return_value.url = avatar_url

            # Calling the update function and checking the results
            updated_user = await update_user(avatar=avatar_data, user_email=user.email, db=db_mock, user=user)
            self.assertEqual(updated_user.avatar, avatar_url)

    @patch("src.repository.users.UserRepository.delete")
    @patch("src.repository.users.UserRepository.get_single")
    async def test_delete_user(self, user_repo_single, user_repo_delete):
        db_mock = MagicMock()
        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
        user_repo_single.return_value = user_to_get
        user_repo_delete.return_value = None
        returned_user = await delete_user(user_id=1, db=db_mock)
        self.assertEqual(returned_user.id, user_to_get.id)

    @patch("src.repository.users.UserRepository.get_single")
    async def test_get_user(self, user_repo_single):
        db_mock = MagicMock()
        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
        user_repo_single.return_value = user_to_get
        returned_user = await get_user(user_id=1, db=db_mock)
        self.assertEqual(returned_user.id, user_to_get.id)

    @patch("src.repository.users.UserRepository.get_username")
    async def test_get_user_by_username(self, user_repo_username):
        db_mock = MagicMock()
        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
        user_repo_username.return_value = user_to_get
        returned_user = await get_user_by_username(username="testuser", db=db_mock)
        self.assertEqual(returned_user.id, user_to_get.id)

    @patch("src.repository.users.UserRepository.ban")
    async def test_ban_user(self, user_repo_ban):
        db_mock = MagicMock()
        user_repo_ban.return_value = {'id': 1, 'ban': True}
        returned_result = await ban_user(user_id=1, db=db_mock)
        self.assertEqual(returned_result, {'id': 1, 'ban': True})

    @patch("src.repository.users.UserRepository.change_role")
    async def test_change_user_role(self, user_repo):
        db_mock = MagicMock()
        user_repo.return_value = {'id': 1, 'role': Role.admin}
        returned_result = await change_user_role(user_id=1, new_role=Role.admin, db=db_mock)
        self.assertEqual(returned_result, {'id': 1, 'role': Role.admin})


if __name__ == '__main__':
    unittest.main()
