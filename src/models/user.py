from sqlalchemy import Column, Integer, DateTime, func, String, Boolean


from .base import Base



class User(Base):
    __tablename__ = "users"

    # required fields for each table
    id = Column(Integer, primary_key=True)
    username = Column(String(50))
    email = Column(String(150), nullable=False, unique=True)
    password = Column(String(255), nullable=False)
    avatar = Column(String(255), nullable=True)
    refresh_token = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    confirmed = Column(Boolean, default=False)
    ban = Column(Boolean, default=False)


