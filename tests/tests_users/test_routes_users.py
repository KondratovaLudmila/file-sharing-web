import tracemalloc
import unittest
from unittest.mock import MagicMock, AsyncMock, patch
from src.repository.users import UserRepository
from src.schemas.user import UserResponse
from src.models.user import User
from sqlalchemy.orm import Session
from src.routes.users import get_users, update_user, delete_user, get_user, get_user_by_username, ban_user, change_user_role
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
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)
        avatar_url = 'https://example.com/avatar.jpg'
        avatar_data = b'avatar_data'
        with patch('src.repository.users.storage.avatar_upload') as avatar_upload_mock:
            avatar_upload_mock.return_value.url = avatar_url
            updated_user = await user_repo.update(user, avatar=avatar_data)
            self.assertEqual(updated_user.avatar, avatar_url)

    # async def test_delete_user(self):
    #     db_mock = MagicMock(spec=Session)
    #     user_to_delete = User(id=1, username="testuser", email="test@example.com", password="testpassword")
    #     user_repo_mock = MagicMock(spec=UserRepository)
    #     user_repo_mock.get_single.return_value = user_to_delete
    #     with patch('src.routes.users.delete_user') as delete_user_mock:
    #         delete_user_mock.return_value = user_to_delete
    #         deleted_user = await delete_user(user_id=1, db=db_mock)
    #
    #     self.assertIsInstance(deleted_user, User)
    #     self.assertEqual(deleted_user.id, user_to_delete.id)

    # async def test_get_user(self):
    #     db_mock = MagicMock()
    #     user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
    #     user_repo_mock = MagicMock(spec=UserRepository)
    #     user_repo_mock.get_single.return_value = user_to_get
    #     returned_user = await get_user(user_id=1, db=db_mock)
    #     self.assertEqual(returned_user.id, user_to_get.id)

    # async def test_get_user_by_username(self):
    #     db_mock = MagicMock()
    #     user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
    #     user_repo_mock = MagicMock(spec=UserRepository)
    #     user_repo_mock.get_username.return_value = user_to_get
    #     returned_user = await get_user_by_username(username="testuser", db=db_mock)
    #     self.assertEqual(returned_user.id, user_to_get.id)

    async def test_ban_user(self):
        db_mock = MagicMock()
        user_repo_mock = MagicMock()
        user_repo_mock.ban.return_value = {'id': 1, 'ban': True}
        returned_result = await ban_user(user_id=1, db=db_mock)
        self.assertEqual(returned_result, {'id': 1, 'ban': True})

    # async def test_change_user_role(self):
    #     db_mock = MagicMock()
    #     user_repo_mock = MagicMock()
    #     user_repo_mock.change_role.return_value = {'id': 1, 'role': Role.admin}
    #     returned_result = await change_user_role(user_id=1, new_role=Role.admin, db=db_mock)
    #     self.assertEqual(returned_result, {'id': 1, 'role': Role.admin})


if __name__ == '__main__':
    unittest.main()
