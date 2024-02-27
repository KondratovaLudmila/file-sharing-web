import unittest
from unittest.mock import MagicMock, patch

from fastapi import HTTPException

from src.models.user import User
from src.services.auth import (
                               verify_password, 
                               create_refresh_token, 
                               create_access_token,
                               get_user_by_refresh_token,
                               get_current_user)
from src.services.hash_handler import hash_password

token_data = {"sub": "test_user"}
fake_user = {"id": 1, "username": 
             "test_user", "email": 
             "test_user@example.com", 
             "password": hash_password("test"), 
             "role": "admin",
             "refresh_token": create_refresh_token(data=token_data),}

user_data = {"username": fake_user["username"], "password": "test"}

class TestAuth(unittest.IsolatedAsyncioTestCase):
    user = User(**fake_user)

    async def test_verify_password(self):
        self.assertTrue(verify_password(user_data["password"], fake_user["password"]))

    
    async def test_verify_password_wrong(self):
        password = "abracadabra"
        self.assertFalse(verify_password(password, fake_user["password"]))


    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_current_user(self, user_repo):
        user_repo.return_value = self.user
        token = create_access_token(data=token_data)
        cur_user = await get_current_user(token=token)

        self.assertEqual(cur_user.id, self.user.id)


    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_current_user_invalid(self, user_repo):
        user_repo.return_value = None
        token = "abracadabra"

        with self.assertRaises(HTTPException) as err:
            await get_current_user(token=token)


    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_current_user_ban(self, user_repo):
        self.user.ban = True
        user_repo.return_value = self.user
        token = create_access_token(token_data)
        with self.assertRaises(HTTPException) as err:
            await get_current_user(token)

        self.user.ban = False


    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_user_by_refresh_token(self, user_repo):
        user_repo.return_value = self.user
        token = create_refresh_token(token_data)
        cur_user = await get_user_by_refresh_token(token)

        self.assertEqual(cur_user.id, self.user.id)

        
    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_user_by_refresh_token_invalid(self, user_repo):
        user_repo.return_value = None
        token = "abracadabra"
        with self.assertRaises(HTTPException) as err:
            await get_user_by_refresh_token(token)

    
    @patch("src.services.auth.UserRepository.get_username")
    async def test_get_user_by_refresh_token_ban(self, user_repo):
        self.user.ban = True
        user_repo.return_value = self.user
        token = create_refresh_token(token_data)
        with self.assertRaises(HTTPException) as err:
            await get_user_by_refresh_token(token)

        self.user.ban = False


if __name__ == "__main__":
    unittest.main()


