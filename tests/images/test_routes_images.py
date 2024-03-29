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
    response = client.put("/images/1", json=body)

    assert response.status_code == 200, response.text
    assert response.json()["id"] == fake_image["id"]


def test_image_update_wrong(client):
    body = {"description": "new_desc", "tags": ["tag1"]}
    response = client.put("/images/10", json=body)

    assert response.status_code == 404, response.text


def test_image_delete(client):
    response = client.delete("/images/1")

    assert response.status_code == 200, response.text
    assert response.json()["id"] == fake_image["id"]


def test_image_get(client):
    response = client.get("/images/1")

    assert response.status_code == 200, response.text
    assert response.json()["id"] == fake_image["id"]


def test_image_get(client):
    response = client.get("/images/1")

    assert response.status_code == 404, response.text


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
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(**fake_image)
    monkeypatch.setattr("src.repository.images.Images.get_single", mock_get)

    response = client.get("/images/1/share")

    assert response.status_code == 200, response.text


def test_image_share_wrong(client, monkeypatch):
    mock_get = AsyncMock()
    mock_get.return_value = None
    monkeypatch.setattr("src.repository.images.Images.get_single", mock_get)

    response = client.get("/images/10/share")

    assert response.status_code == 404, response.text


def test_image_shared_get_wrong(client, monkeypatch):
    mock_get = AsyncMock()
    mock_get.return_value = None
    monkeypatch.setattr("src.repository.images.Images.identify", mock_get)

    response = client.get("/images/shared/abracadabra")

    assert response.status_code == 404, response.text


def test_image_shared_get(client, monkeypatch):
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(**fake_image)
    monkeypatch.setattr("src.repository.images.Images.identify", mock_get)
    identifier = fake_image.get("identifier")
    response = client.get(f"/images/shared/{identifier}")

    assert response.status_code == 200, response.text


def test_image_get(client, monkeypatch):
    mock_get = AsyncMock()
    mock_get.return_value = MagicMock(**fake_image)
    monkeypatch.setattr("src.repository.images.Images.get_single", mock_get)
    pk = fake_image.get("id")
    response = client.get(f"/images/{pk}")

    assert response.status_code == 200, response.text


def test_image_get_wrong(client, monkeypatch):
    mock_get = AsyncMock()
    mock_get.return_value = None
    monkeypatch.setattr("src.repository.images.Images.get_single", mock_get)
    pk = 10
    response = client.get(f"/images/{pk}")

    assert response.status_code == 404, response.text