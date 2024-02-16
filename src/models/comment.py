from sqlalchemy import Column, Integer, DateTime, func
from sqlalchemy.orm import relationship

from .base import Base

class Comment(Base):
    __tablename__ = "comments"

    #required fields for each table
    id = Column(Integer, primary_key=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())