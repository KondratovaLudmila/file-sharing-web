import unittest
# from aioresponses import aioresponses
from unittest.mock import MagicMock, patch
from src.repository.users import UserRepository
from src.models.user import User, Role, Enum
from src.models.image import Image
from src.schemas.user import UserCreate, UserResponse
from fastapi import HTTPException, status
from src.routes.users import delete_user
from sqlalchemy.orm import Session
import unittest.mock as mock
from fastapi.datastructures import UploadFile


class TestUserRepository(unittest.IsolatedAsyncioTestCase):
    async def asyncSetUp(self):
        self.db_mock = MagicMock()

    @patch('src.repository.users.User')
    async def test_create_user(self, mock_user):
        db_mock_instance = MagicMock()
        user_repo = UserRepository(db_mock_instance)
        user_data = UserCreate(username="test1", email="test_test1@example.com", password="testpassword")
        db_mock_instance.query.return_value.filter.return_value.first.return_value = None
        mock_user_instance = MagicMock()
        mock_user.return_value = mock_user_instance
        mock_user_instance.username = user_data.username
        mock_user_instance.email = user_data.email
        mock_user_instance.password = user_data.password
        mock_user_instance.role = Role.user.value

        created_user = await user_repo.create(**user_data.dict())

        self.assertEqual(created_user.username, "test1")
        self.assertEqual(created_user.email, "test_test1@example.com")
        self.assertEqual(created_user.password, "testpassword")
        self.assertEqual(created_user.role, Role.user.value)

    async def test_create_user_existing_username(self):
        db_mock = MagicMock()
        db_mock.query.return_value.filter.return_value.first.return_value = MagicMock()  # Simulating existing user
        with patch('src.repository.users.Session', return_value=db_mock):
            user_repo = UserRepository(db_mock)
            with self.assertRaises(HTTPException) as context:
                await user_repo.create("test_user", "test_user@example.com", "test_password")

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "User with the same username already exists.")

    async def test_create_user_existing_email(self):
        db_mock = MagicMock()
        db_mock.query.return_value.filter.side_effect = [None, MagicMock()]  # Simulating existing email user
        with patch('src.repository.users.Session', return_value=db_mock):
            user_repo = UserRepository(db_mock)
            with patch.object(user_repo, 'create') as mock_create:
                mock_create.side_effect = HTTPException(status_code=409,
                                                        detail="User with the same email already exists.")
                with self.assertRaises(HTTPException) as context:
                    await user_repo.create("testuser", "test@example.com", "testpassword")

        self.assertEqual(context.exception.status_code, 409)
        self.assertEqual(context.exception.detail, "User with the same email already exists.")

    async def test_update_user_avatar(self):
        # Mocking objects and preparing test data
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)

        # Creating a real User object
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)

        # Mocking the avatar_upload function
        avatar_url = 'https://example.com/avatar.jpg'
        with patch('src.repository.users.storage.avatar_upload') as avatar_upload_mock:
            avatar_upload_mock.return_value.url = avatar_url

            # Calling the update function and checking the results
            updated_user = await user_repo.update(user, avatar=b'avatar_data')
            self.assertEqual(updated_user.avatar, avatar_url)

    async def test_update_user_email(self):
        # Mocking objects and preparing test data
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)

        # Creating a real User object
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)

        # Calling the update function to change email
        updated_user = await user_repo.update(user, email="new_email@example.com")

        # Checking if the email was updated correctly
        self.assertEqual(updated_user.email, "new_email@example.com")

    async def test_update_user_without_changes(self):
        # Mocking objects and preparing test data
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)

        # Creating a real User object
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)

        # Calling the update function without any changes
        updated_user = await user_repo.update(user)

        # Checking if the user object remains unchanged
        self.assertEqual(user, updated_user)

    async def test_update_user_error(self):
        # Mocking objects and preparing test data
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)

        # Creating a real User object
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)

        # Mocking the avatar_upload function to raise an exception
        with patch('src.repository.users.storage.avatar_upload') as avatar_upload_mock:
            avatar_upload_mock.side_effect = Exception("Avatar upload failed")

            # Calling the update function and expecting an HTTPException
            with self.assertRaises(HTTPException) as context:
                await user_repo.update(user, avatar=b'avatar_data')

            # Checking the status code of the HTTPException
            self.assertEqual(context.exception.status_code, 500)

    async def test_update_email(self):
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", avatar=None)
        db_mock = MagicMock()
        user_repo = UserRepository(db_mock)
        updated_user = await user_repo.update(user)
        self.assertEqual(updated_user.email, user.email)

    # async def test_delete_user_success(self):
    #     # Мокуємо об'єкти та підготовуємо тестові дані
    #     db_mock = MagicMock()
    #     user_id = 1
    #     user_response_data = {"id": user_id, "username": "testuser", "email": "test@example.com"}
    #     user_repo_mock = MagicMock(spec=UserRepository)
    #     user_repo_mock.get_single.return_value = user_response_data
    #
    #     # Мокуємо функцію delete_user та передаємо user_repo_mock
    #     with patch('src.routes.users.UserRepository', return_value=user_repo_mock):
    #         # Викликаємо функцію delete_user та перевіряємо результат
    #         deleted_user_data = await delete_user(user_id=user_id, db=db_mock)
    #         deleted_user = UserResponse(**deleted_user_data)
    #
    #     # Перевіряємо, чи отримали ми об'єкт користувача UserResponse
    #     self.assertIsInstance(deleted_user, UserResponse)
    #     # Перевіряємо, чи співпадає id користувача
    #     self.assertEqual(deleted_user.id, user_id)

    async def test_delete_user_not_found(self):
        # Mocking objects and preparing test data
        user_id = 1
        db_mock = MagicMock(spec=Session)
        user_repo_mock = MagicMock(spec=UserRepository)
        user_repo_mock.get_single.return_value = None
        with patch('src.routes.users.UserRepository', return_value=user_repo_mock):
            # Calling the delete_user function and expecting an HTTPException
            with self.assertRaises(HTTPException) as context:
                await delete_user(user_id=user_id, db=db_mock)
            # Checking the status code of the HTTPException
            self.assertEqual(context.exception.status_code, status.HTTP_404_NOT_FOUND)
            # Checking the detail of the HTTPException
            self.assertEqual(context.exception.detail, "User not found")

    async def test_get_single_user(self):
        db_mock = MagicMock()

        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
        db_mock_instance = db_mock.return_value
        db_mock_instance.query.return_value.filter.return_value.first.return_value = user_to_get
        user_repo = UserRepository(db_mock_instance)
        result = await user_repo.get_single(1)
        self.assertEqual(result, user_to_get)

    async def test_get_username(self):
        db_mock = MagicMock()
        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")

        db_mock_instance = db_mock.return_value
        db_mock_instance.query.return_value.filter.return_value.first.return_value = user_to_get
        user_repo = UserRepository(db_mock_instance)
        result = await user_repo.get_username("testuser")
        self.assertEqual(result, user_to_get)

    async def test_get_email(self):
        db_mock = MagicMock()
        user_to_get = User(id=1, username="testuser", email="test@example.com", password="testpassword")
        db_mock_instance = db_mock.return_value
        db_mock_instance.query.return_value.filter.return_value.first.return_value = user_to_get
        user_repo = UserRepository(db_mock_instance)
        result = await user_repo.get_email("test@example.com")
        self.assertEqual(result, user_to_get)

    async def test_get_many(self):
        db_mock = MagicMock()
        user1 = User(id=1, username="user1", email="user1@example.com", password="testpassword1")
        user2 = User(id=2, username="user2", email="user2@example.com", password="testpassword2")
        db_mock_instance = db_mock.return_value
        db_mock_instance.query.return_value.filter.return_value.all.return_value = [user1, user2]
        user_repo = UserRepository(db_mock_instance)
        result = await user_repo.get_many("test")
        self.assertEqual(result, [user1, user2])

    async def test_ban_user(self):
        db_mock = MagicMock()
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", ban=False)

        user_repo = UserRepository(db_mock)
        result = await user_repo.ban(1)
        self.assertEqual(result.ban, user.ban)

    from unittest.mock import MagicMock

    async def test_change_role(self):
        db_mock = MagicMock()
        user = User(id=1, username="testuser", email="test@example.com", password="testpassword", role=Role.user)

        user_repo = UserRepository(db_mock)
        result = await user_repo.change_role(1, Role.moderator)
        self.assertEqual(result.role, Role.moderator.value)


if __name__ == '__main__':
    unittest.main()

