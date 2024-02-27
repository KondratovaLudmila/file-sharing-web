import pytest
from unittest.mock import MagicMock
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


from main import app
from src.models.user import Base
from src.dependencies.db import get_db
from src.services.auth import get_current_user
from src.models.user import User
import os
import dotenv

dotenv.load_dotenv()

pg_user = os.getenv("POSTGRES_USER")
password = os.getenv("POSTGRES_PASSWORD")
port = os.getenv("POSTGRES_PORT")
SQLALCHEMY_DATABASE_URL = f"postgresql+psycopg2://{pg_user}:{password}@localhost:{port}/tests"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def user():
    return {"id": 1, "username": "test_user", "email": "test_user@example.com", "password": "test", "role": "admin"}


@pytest.fixture(scope="module")
def session():
    # Create the database

    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)

    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="module")
def client(session, user):
    # Dependency override

    def override_get_db():
        try:
            yield session
        finally:
            session.close()

    def override_get_current_user():
        return User(**user)


    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user

    yield TestClient(app)



