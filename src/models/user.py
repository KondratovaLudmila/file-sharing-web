from sqlalchemy import Column, Integer, DateTime, func, String
from sqlalchemy.orm import relationship

#required import for each table
from .base import Base

class User(Base):
    __tablename__ = "users"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    
    