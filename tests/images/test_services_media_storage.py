import unittest
from unittest.mock import MagicMock, patch
from cloudinary import CloudinaryImage

from src.services.media_storage import MediaCloud


class TestMediaCloud(unittest.IsolatedAsyncioTestCase):

    def setUp(self) -> None:
        self.file_mock = MagicMock()
        self.image_mock = MagicMock(spec=CloudinaryImage)


    @patch("src.services.media_storage.upload_image")
    async def test_avatar_upload(self, cloud_mock):
        cloud_mock.return_value = self.image_mock
        ident = "111111111"

        image = await MediaCloud().avatar_upload(self.file_mock, ident)

        self.assertEqual(image, self.image_mock)


    @patch("src.services.media_storage.upload_image")
    async def test_user_image_upload(self, cloud_mock):
        cloud_mock.return_value = self.image_mock
        ident = "111111111"
        trans = {"effect": "sepia"}

        image = await MediaCloud().user_image_upload(self.file_mock, ident, trans)

        self.assertEqual(image, self.image_mock)


    @patch("src.services.media_storage.upload_image")
    async def test_user_image_transform(self, cloud_mock):
        cloud_mock.return_value = self.image_mock
        url = "wwww"
        trans = {}
        new_ident = "22222"

        image = await MediaCloud().image_transform(url, trans, new_ident)

        self.assertEqual(image, self.image_mock)


    @patch("src.services.media_storage.destroy")
    async def test_user_image_remove(self, cloud_mock):
        cloud_mock.return_value = self.image_mock
        ident = "11111111111"

        image = await MediaCloud().remove_media(ident)

        self.assertEqual(image, self.image_mock)


if __name__ == '__main__':
    unittest.main()
