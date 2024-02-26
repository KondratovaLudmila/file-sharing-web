from unittest.mock import MagicMock, AsyncMock

from src.models.user import User


def test_create_user(client, user):
    response = client.post(
                            "/auth/signup",
                            json=user,
                            )
    assert response.status_code == 201, response.text


def test_create_user_duplicate_username(client, user):
    response = client.post(
        "/auth/signup",
        json=user,
    )

    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "User with the same username already exists."


def test_create_user_duplicate_email(client, user):
    email_user = user.copy()
    email_user["username"] = "vasya"
    response = client.post(
        "/auth/signup",
        json=email_user,
    )
    
    assert response.status_code == 409, response.text
    assert response.json()["detail"] == "User with the same email already exists."


def test_signin_user(client, session, user):
    session.commit()
    response = client.post(
        "/auth/signin",
        data=user,
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["token_type"] == "bearer"


def test_signin_wrong_password(client, user):
    response = client.post(
        "/auth/signin",
        data={"username": user.get('username'), "password": 'password'},
    )
    assert response.status_code == 401, response.text


def test_signin_wrong_username(client, user):
    response = client.post(
        "/auth/signin",
        data={"username": 'username', "password": user.get('password')},
    )
    assert response.status_code == 401, response.text


def test_refresh_token(client, user, monkeypatch):
    get_user = AsyncMock()
    cur_user = User(**user)
    get_user.return_value = cur_user
    monkeypatch.setattr("src.routes.auth.get_user_by_refresh_token", get_user)
    response = client.get("/auth/refresh_token", headers={"Authorization": f"Bearer {cur_user.refresh_token}"})
    
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["access_token"] is not None
    assert data["token_type"] is not None


def test_refresh_token_invalid_token(client, monkeypatch):
    get_user = AsyncMock()
    get_user.return_value = None
    monkeypatch.setattr("src.routes.auth.get_user_by_refresh_token", get_user)
    response = client.get("/auth/refresh_token", headers={"Authorization": "Bearer test"})
    
    assert response.status_code == 401, response.text
    assert response.json()["detail"] == "Invalid refresh token"





    



        
