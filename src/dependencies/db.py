from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from contextlib import contextmanager

from ..models.base import Base

from ..models.user import User
from ..models.image import Image
from ..models.comment import Comment


from ..conf.config import settings


SQLALCHEMY_DATABASE_URL = settings.sqlalchemy_database_url
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Dependency
@contextmanager
def session():
    session = SessionLocal()
    try:
        yield session
    except Exception as err:
        print(err)
        session.rollback()
    finally:
        session.close()

def get_db():
    with session() as db:
        yield db

