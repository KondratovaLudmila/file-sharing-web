import unittest
from src.schemas.user import UserCreate, UserUpdate, UserResponse, UserBan, UserUpdateResponse  # Підставте вашу назву модулю

class TestUserCreate(unittest.TestCase):
    def test_required_fields(self):
        # Перевіряємо, що обов'язкові поля дійсно обов'язкові
        with self.assertRaises(ValueError):
            user_create = UserCreate()

    def test_valid_values(self):
        # Перевіряємо, що валідні значення працюють правильно
        user_create = UserCreate(username="testuser", email="test@example.com", password="testpassword")
        self.assertEqual(user_create.username, "testuser")
        self.assertEqual(user_create.email, "test@example.com")
        self.assertEqual(user_create.password, "testpassword")

class TestUserUpdate(unittest.TestCase):
    def test_valid_email(self):
        # Перевіряємо, що валідні значення працюють правильно
        user_update = UserUpdate(email="test@example.com")
        self.assertEqual(user_update.email, "test@example.com")

class TestUserResponse(unittest.TestCase):
    def test_valid_values(self):
        # Перевіряємо, що валідні значення працюють правильно
        user_response = UserResponse(id=1, username="testuser", email="test@example.com", role="admin")
        self.assertEqual(user_response.id, 1)
        self.assertEqual(user_response.username, "testuser")
        self.assertEqual(user_response.email, "test@example.com")
        self.assertEqual(user_response.role, "admin")

class TestUserBan(unittest.TestCase):
    def test_valid_values(self):
        # Перевіряємо, що валідні значення працюють правильно
        user_ban = UserBan(id=1, username="testuser", email="test@example.com", role="user", ban=True)
        self.assertEqual(user_ban.id, 1)
        self.assertEqual(user_ban.username, "testuser")
        self.assertEqual(user_ban.email, "test@example.com")
        self.assertEqual(user_ban.role, "user")
        self.assertTrue(user_ban.ban)

class TestUserUpdateResponse(unittest.TestCase):
    def test_valid_values(self):
        # Перевіряємо, що валідні значення працюють правильно
        user_update_response = UserUpdateResponse(id=1, username="testuser", email="test@example.com", role="user", avatar="test_avatar.jpg")
        self.assertEqual(user_update_response.id, 1)
        self.assertEqual(user_update_response.username, "testuser")
        self.assertEqual(user_update_response.email, "test@example.com")
        self.assertEqual(user_update_response.role, "user")
        self.assertEqual(user_update_response.avatar, "test_avatar.jpg")

if __name__ == '__main__':
    unittest.main()
