from sqlalchemy import Column, String, Integer, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Role(Base):
    __tablename__ = "roles"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())