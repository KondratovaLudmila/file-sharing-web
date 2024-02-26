import pytest
from unittest.mock import MagicMock, AsyncMock
from pathlib import Path

from src.models.user import User
from src.models.image import Image
from src.schemas.image import ImageTransfornModel


fake_image = {"id": 1, 
              "url": "www.ttt.com/folder/image.jpeg", 
              "description": "my_desk", 
              "tags": [], 
              "user_id": 1, 
              "identifier": "kjhjhkjlkjh"}

def test_image_create(client, user, monkeypatch):
    data = {"description": "my_desc", "tags": None}
    url = "www.test/1212/reeyey.jpeg"
    public_id = "1212/reeyey"
    mock_upload = MagicMock()
    mock_upload.return_value = MagicMock(url=url, public_id=public_id)
    monkeypatch.setattr("src.services.media_storage.upload_image", mock_upload)

    file_name = "test.jpeg"
    path = Path(file_name)
    if not path.exists():
        path.touch()
    response = client.post("/images", files={"file": open(file_name, 'rb')}, data=data)
    

    assert response.status_code == 201, response.text


def test_images_get(client):
    response = client.get("/images/?offset=0&limit=10")

    assert response.status_code == 200, response.text


def test_image_update(client):
    body = {"description": "new_desc", "tags": ["tag1"]}
    response = client.patch("/images/1", json=body)

    assert response.status_code == 200, response.text


def test_image_update_wrong(client):
    body = {"description": "new_desc", "tags": ["tag1"]}
    response = client.patch("/images/10", json=body)

    assert response.status_code == 404, response.text


def test_image_delete(client):
    response = client.delete("/images/1")

    assert response.status_code == 200, response.text


def test_image_delete_wrong(client):
    response = client.delete("/images/100")

    assert response.status_code == 404, response.text


def test_image_transform(client, monkeypatch):
    body = {
            "height": None,
            "width": None,
            "effect": "sepia",
            "crop": "thumb",
            "gravity": "face",
            "radius": "max",
            "background": "auto"
            }
    
    mock_upload = AsyncMock()
    mock_upload.return_value = MagicMock(**fake_image)
    monkeypatch.setattr("src.repository.images.Images.transform", mock_upload)

    response = client.post("/images/1/transform", json=body)

    assert response.status_code == 200, response.text


def test_image_transform_wrong(client, monkeypatch):
    body = {
            "height": None,
            "width": None,
            "effect": "sepia",
            "crop": "thumb",
            "gravity": "face",
            "radius": "max",
            "background": "auto"
            }
    
    mock_upload = AsyncMock()
    mock_upload.return_value = None
    monkeypatch.setattr("src.repository.images.Images.transform", mock_upload)

    response = client.post("/images/1/transform", json=body)

    assert response.status_code == 404, response.text


def test_image_share(client, monkeypatch):
    mock_upload = AsyncMock()
    mock_upload.return_value = MagicMock(**fake_image)
    monkeypatch.setattr("src.repository.images.Images.get_single", mock_upload)

    response = client.post("/images/1/share")

    assert response.status_code == 200, response.text

